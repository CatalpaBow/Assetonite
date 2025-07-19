import configparser 
from configparser import ConfigParser as cfgPrsr
from typing import Union
from pathlib import Path
from pyaccsharedmemory import ACC_map
from dataclasses import dataclass
from typing import Callable
from typing import Any
def create_lut(lut_str: str) -> list[tuple[int, float]]:
    # LUTの形式は "(0=0|1000=10|2000=26|...)" のような文字列
    parsed = lut_str[1:-1]  # 最初と最後の括弧を取り除く
    key_value_list = parsed.split('|')
    key_value_pair = [kv.split('=') for kv in key_value_list]
    return [(int(k), float(v)) for k, v in key_value_pair]


def lerp_from_lut(value: Union[int, float], lut: list[tuple[int, float]]) -> float:
    for i in range(1, len(lut)):
        key_low, value_low = lut[i - 1]
        key_high, value_high = lut[i]
        if key_low <= value < key_high:
            t = (value - key_low) / (key_high - key_low)
            return value_low + t * (value_high - value_low)
    if value < lut[0][0]:
        return lut[0][1]
    else:
        return lut[-1][1]


class AnalogInstrument:
    def __init__(self, name: str, step: float, lut: list[tuple[int, float]]):
        self.name = name
        self.step = step
        self.lut = lut

    def get_rot(self, val: Union[int, float]) -> float:
        if self.lut is None:
            return self.step * val
        return lerp_from_lut(val, self.lut)


def create_analog_instrument(cfg: cfgPrsr, section_name: str) -> AnalogInstrument:
    lut = None
    step = 0.0
    if cfg.has_option(section_name, 'LUT'):
        lut_str = cfg[section_name]['LUT']
        lut = create_lut(lut_str)
    if cfg.has_option(section_name, 'STEP'):
        step = float(cfg[section_name]['STEP'])
    return AnalogInstrument(section_name, step, lut)


def create_analog_instrument_dic(cfg: configparser.ConfigParser) -> dict[str,AnalogInstrument]:
    return {section : create_analog_instrument(cfg, section) for section in cfg.sections()}


@dataclass
class TelemetryDataAnalogInstruments:
    rpm_rot : float
    speed_rot : float
    fuel_rot : float
    turbo_rot : float
    water_temp_rot : float
    
class TelemetryAnalogInstruments:

    def update_data_src(self,cfg: configparser.ConfigParser):
        self.instrument_dic = create_analog_instrument_dic(cfg)
    
    def create(self,sm : ACC_map) -> TelemetryDataAnalogInstruments:
        return TelemetryDataAnalogInstruments(
            rpm_rot = self.instrument_dic['RPM_INDICATOR'].get_rot(sm.Physics.rpm),
            speed_rot = self.instrument_dic['SPEED_INDICATOR'].get_rot(sm.Physics.speed_kmh),
            fuel_rot = self.instrument_dic['FUEL_INDICATOR'].get_rot(sm.Physics.fuel),
            turbo_rot = self.instrument_dic['TURBO_INDICATOR'].get_rot(sm.Physics.turbo_boost),
            water_temp_rot = self.instrument_dic['WATER_TEMP'].get_rot(sm.Physics.water_temp),
        )
# スクリプト本体（テスト）
if __name__ == "__main__":
    path = Path(r'mocks\ini\analog_instruments.ini')
    cfg = cfgPrsr()
    cfg.read(path)
    list = TelemetryAnalogInstruments(cfg)
    print(list)