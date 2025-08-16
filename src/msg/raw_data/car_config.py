from typing import Iterator
import configparser
from msg.raw_data.pyaccsharedmemory import *
from msg.message.analog_instrument_angle_calculator import AnalogInstrumentConstant
from msg.message.tyre_rotation_calculator import TyreRotationConstant
class CarConfig:
    dic :dict[str,configparser.ConfigParser]
    def __init__(self,dic :dict[str, configparser.ConfigParser]):
        self.dic= dic

    def read_analog_instrument_const(self) -> Iterator[AnalogInstrumentConstant]:
        cfg = self.dic['analog_instruments']
        for section_name in cfg.sections():
            lut = None
            step = 0.0
            if cfg.has_option(section_name, 'LUT'):
                lut_str = cfg[section_name]['LUT']
                lut = create_lut(lut_str)
            if cfg.has_option(section_name, 'STEP'):
                step = float(cfg[section_name]['STEP'])
            lower_name = section_name.split('_')[0].lower()
            yield AnalogInstrumentConstant(lower_name,step,lut)

    
    def read_tyre_const(self) -> TyreRotationConstant:
        car = safe_get(self, 'car', default={})
        suspensions = safe_get(self, 'suspensions', default={})

        steer_lock = safe_get(car, 'CONTROLS', 'STEER_LOCK',default=450)
        steer_ratio = safe_get(car, 'CONTROLS', 'STEER_RATIO',default=18) * -1

        wheel_base = safe_get(suspensions, 'BASIC', 'WHEELBASE',default=2.67)
        tread_width = safe_get(suspensions, 'FRONT', 'TRACK',default=1.48)
        return TyreRotationConstant(steer_lock,steer_ratio,wheel_base,tread_width)
        #logger.info(f'Reloaded telemtry tyre info\nSteerLock:{self.steer_lock} SteerRatio:{self.steer_ratio} WheelBase:{self.l} TreadWidth:{self.w}')
    
   
def safe_get(cfg,*keys, default=None):
    try:
        cfg = None
        for key in keys:
            cfg = cfg[key]
        return cfg
    except (KeyError, TypeError):
        return default

def create_lut(lut_str: str) -> list[tuple[int, float]]:
    # LUTの形式は "(0=0|1000=10|2000=26|...)" のような文字列
    parsed = lut_str[1:-1]  # 最初と最後の括弧を取り除く
    key_value_list = parsed.split('|')
    key_value_pair = [kv.split('=') for kv in key_value_list]
    return [(int(k), float(v)) for k, v in key_value_pair]