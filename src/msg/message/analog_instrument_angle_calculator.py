from typing import NamedTuple,Sequence
from collections import namedtuple

class RotationLUTKeyValue(NamedTuple):
    rpm : int
    angle : float

class AnalogInstrumentConstant(NamedTuple):
    name : str
    step : int
    lut : Sequence[RotationLUTKeyValue]


class AnalogInstrumentInput(NamedTuple):
    rpm : float
    speed : float
    fuel : float
    turbo : float 
    water : float

class AnalogInstrumentAngleCalculator:
    def __init__(self, step : float,lut : Sequence[RotationLUTKeyValue]):
        self.step = step
        self.lut = lut

    def calc_angle(self, value: int) -> float:
        if self.lut is None:
            return self.step * value
        return lerp_from_lut(value, self.lut)

def lerp_from_lut(value: int, lut : Sequence[RotationLUTKeyValue]) -> float:
    for i in range(1, len(lut)):
        value_low, angle_low = lut[i - 1]
        value_high, angle_high = lut[i]

        #If find range,return lerp value.
        if value_low <= value < value_high:
            t = (value - value_low) / (value_high - value_low)
            return angle_low + t * (angle_high - angle_low)
    
    #Clipping(rpm < 0 || rpm > max_rpm)
    if value < lut[0][0]:
        return lut[0][1]
    else:
        return lut[-1][1]