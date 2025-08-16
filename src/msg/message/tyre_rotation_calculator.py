from typing import Iterable,NamedTuple
from dataclasses import dataclass
import quaternion
import numpy as np
import math

from utils.logger_getter import get_logger
logger = get_logger('def')

class TyreRotationInput(NamedTuple):
    steer_angle : float
    wheel_angulars : Iterable[float] 
    camber_rads : Iterable[float]

class TyreRotationConstant(NamedTuple):
    steer_lock  : float
    steer_ratio : float
    wheel_base  : float
    tread_width : float
@dataclass
class QuaternionData:
    w : float
    x : float
    y : float
    z : float

    def __iter__(self):
        return iter((self.x, self.y, self.z,self.w))
    
class TyreRotationCalculator:
    _tire_pitch_q_state = [
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0)
    ]

    def __init__(self,const : TyreRotationConstant):
        self.steer_lock = const.steer_lock
        self.steer_ratio = const.steer_ratio
        self.l = const.wheel_base
        self.w = const.tread_width
        logger.info(f'Tyre rotation calculator updated.\nSteerLock:{self.steer_lock} SteerRatio:{self.steer_ratio} WheelBase:{self.l} TreadWidth:{self.w}')

    def calculate(self,input : TyreRotationInput) -> dict:
        steer_angle : float = input.steer_angle
        wheel_angulars : Iterable[float] = input.wheel_angulars
        camber_rads : Iterable[float] = input.camber_rads
        
        # ------------------------
        delta_time = 1 / 160.0          # 秒（1フレーム分）
        l = self.l                     # ホイールベース
        w = self.w                     # トレッド幅
        # ------------------------
        rots = []
        # 旋回角 前輪のみ回転 前輪へのアッカーマン補正あり
        tire_yaw_angle = steer_angle * (self.steer_lock/self.steer_ratio)
        tire_yaw_angle_rad = np.deg2rad(tire_yaw_angle)
        tire_yaw_q = [
            np.quaternion(1, 0, 0, 0),
            np.quaternion(1, 0, 0, 0),
            np.quaternion(1, 0, 0, 0),
            np.quaternion(1, 0, 0, 0)
        ]
        # 前輪へのアッカーマン補正 0除算回避の為radが0時には補正しない
        if(tire_yaw_angle_rad != 0):
            r = l / math.tan(tire_yaw_angle_rad) + w / 2
            theta_in = math.atan(l / (r - w/2))
            theta_out = math.atan(l / (r + w/2))
            if(tire_yaw_angle_rad > 0):
                tire_yaw_q[0] = quaternion.from_rotation_vector(np.array([0,theta_in,0]))
                tire_yaw_q[1] = quaternion.from_rotation_vector(np.array([0,theta_out,0]))
            else:    
                tire_yaw_q[0] = quaternion.from_rotation_vector(np.array([0,theta_in,0]))
                tire_yaw_q[1] = quaternion.from_rotation_vector(np.array([0,theta_out,0]))
        #無し
        else:
            tire_yaw_q[0] = -quaternion.from_rotation_vector(np.array([0,tire_yaw_angle_rad,0]))
            tire_yaw_q[1] = -quaternion.from_rotation_vector(np.array([0,tire_yaw_angle_rad,0]))
        # 後輪は旋回なし
        tire_yaw_q[2] = np.quaternion(1, 0, 0, 0)
        tire_yaw_q[3] = np.quaternion(1, 0, 0, 0)

        index = 0
        for angular in wheel_angulars:
            # ロール(キャンバー角)
            chamber_q = quaternion.from_rotation_vector(np.array([0,0,camber_rads[index]]))
            camber_degree = math.degrees(camber_rads[index])
            #if((camber_degree > 4) or (camber_degree < - 4)):
            #    print(f'スパイク検知:{camber_degree}')
            # ピッチ角
            tire_omega_delta = angular *  delta_time
            q_wheel_rotation = quaternion.from_rotation_vector(np.array([tire_omega_delta,0,0]))
            '''
            np.quaternion(
                np.cos(tire_omega_delta / 2),
                np.sin(tire_omega_delta / 2),
                0,
                0
            )
            '''
            self._tire_pitch_q_state[index] = self._tire_pitch_q_state[index] * q_wheel_rotation
            self._tire_pitch_q_state[index] = self._tire_pitch_q_state[index].normalized()
            # 合成
            # キャンバー角は現状異常値が頻発
            # 異常値の出現条件はタイヤが縁石に乗った時
            # sm.Physics.camber_radの値自体がおかしい
            # キャンバー角が反映されずとも、見た目への影響は微々たるものなので反映しないことにする
            q = tire_yaw_q[index]  * self._tire_pitch_q_state[index]
            rots.append(QuaternionData(q.w,q.x,q.y,q.z))
            index += 1
        return {
            "front_left"  : rots[0],
            "front_right" : rots[1],
            "rear_left"   : rots[2],
            "rear_right"  : rots[3],
        }