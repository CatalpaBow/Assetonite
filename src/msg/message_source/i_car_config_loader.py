from abc import ABC,abstractmethod
from typing import Iterator

from msg.message.analog_instrument_angle_calculator import AnalogInstrumentConstant
from msg.message.tyre_rotation_calculator import TyreRotationConstant
class BaseCarConifg:   
    @abstractmethod
    def read_analog_instrument_const(self) -> Iterator[AnalogInstrumentConstant]:
        pass
    @abstractmethod
    def read_tyre_const(self) -> TyreRotationConstant:
        pass

class ICarConfigLoader(ABC):
    @abstractmethod
    def load(self,path : str) -> BaseCarConifg:
        pass