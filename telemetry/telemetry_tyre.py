from ac_telemetry import ACTelemetry
import quaternion
import numpy as np
import os
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
import cfg_loder
import telemetry.telemetry_analog_instruments
import configparser
class TelemetryTyre:
    #car_coordinate  = [0.0,0.0,0.0] 
    #car_rotation = np.quaternion(1, 0, 0, 0)
    tire_suspension = [0.0,0.0,0.0]
    _tire_pitch_q_ls = [
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0),
        np.quaternion(1, 0, 0, 0)
    ]
    tyre_rotation = [
        [np.quaternion(1, 0, 0, 0)],
        [np.quaternion(1, 0, 0, 0)],
        [np.quaternion(1, 0, 0, 0)],
        [np.quaternion(1, 0, 0, 0)]
    ]
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.grid(True)

    def update_data_src(self,sm):
        pass 

    def update(self,sm):
        # x軸反転(右手→左手)
        #self.car_coordinate[0] = -sm.Graphics.car_coordinates.x
        #self.car_coordinate[1] = sm.Graphics.car_coordinates.y
        #self.car_coordinate[2] = sm.Graphics.car_coordinates.z

        # x軸反転(右手左手)
        #roll = sm.Physics.roll
        #yaw = sm.Physics.heading
        #pitch = sm.Physics.pitch
        #self.car_rotation = quaternion.from_euler_angles(pitch,roll,yaw)     #z,x,y
        # ------------------------
        # パラメータ (34gtr v-spec)
        steer_lock = 450.0             # 度（ハンドル片側最大）
        steer_ratio = 18.0             # ステア比
        delta_time = 1 / 60.0          # 秒（1フレーム分）
        l = 2.67                        # ホイールベース
        w = 1.48                        # トレッド幅
        # ------------------------

        # 旋回角 前輪のみ回転 前輪へのアッカーマン補正あり
        tire_yaw_angle = sm.Physics.steer_angle * (steer_lock/steer_ratio)
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
            tire_yaw_q[0] = quaternion.from_rotation_vector(np.array([0,tire_yaw_angle_rad,0]))
            tire_yaw_q[1] = quaternion.from_rotation_vector(np.array([0,tire_yaw_angle_rad,0]))
        # 後輪は旋回なし
        tire_yaw_q[2] = np.quaternion(1, 0, 0, 0)
        tire_yaw_q[3] = np.quaternion(1, 0, 0, 0)

        index = 0
        for angular in sm.Physics.wheel_angular_s:
            # ロール(キャンバー角)
            chamber_q = quaternion.from_rotation_vector(np.array([0,0,sm.Physics.camber_rad[index]]))
            camber_degree = math.degrees(sm.Physics.camber_rad[index])
            #if((camber_degree > 4) or (camber_degree < - 4)):
            #    print(f'スパイク検知:{camber_degree}')
            # ピッチ角
            tire_omega_delta = -angular * delta_time
            q_wheel_rotation = quaternion.from_rotation_vector(np.array([tire_omega_delta,0,0]))
            np.quaternion(
                np.cos(tire_omega_delta / 2),
                np.sin(tire_omega_delta / 2),
                0,
                0
            )
            self._tire_pitch_q_ls[index] = self._tire_pitch_q_ls[index] * q_wheel_rotation
            self._tire_pitch_q_ls[index] = self._tire_pitch_q_ls[index].normalized()
            # 合成
            # キャンバー角は現状異常値が頻発
            # 異常値の出現条件はタイヤが縁石に乗った時
            # sm.Physics.camber_radの値自体がおかしい
            # キャンバー角が反映されずとも、見た目への影響は微々たるものなので反映しないことにする

            self.tyre_rotation[index] =  tire_yaw_q[index]  * self._tire_pitch_q_ls[index]
            index += 1