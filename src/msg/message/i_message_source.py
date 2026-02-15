from abc import ABC, abstractmethod
from typing import Iterator,Any
from dataclasses import dataclass
from msg.message.analog_instrument_angle_calculator import AnalogInstrumentConstant,AnalogInstrumentInput
from msg.message.tyre_rotation_calculator import TyreRotationInput,TyreRotationConstant

@dataclass
class Transform:
    position : tuple[float] # f3
    rotation : tuple[float] # q

@dataclass
class Transforms:
    body : Transform
    wheel_lf : Transform
    wheel_rf : Transform
    wheel_lr : Transform
    wheel_rr : Transform

@dataclass
class AnalogInstrumentAngles:
    rpm : float
    speed : float
    fuel : float
    turbo : float 
    water : float

@dataclass
class Animations:
    analog_instrument_angles : AnalogInstrumentAngles
    steer : float
    
@dataclass
class Car:
    id : int
    transforms : Transforms
    animation : Animations

@dataclass
class AICar:
    transform : Transforms

@dataclass
class ConstantData:
    analog_instrument_constant : Iterator[AnalogInstrumentConstant]
    tyre_constant : TyreRotationConstant

class IMessageSource(ABC):
    @abstractmethod
    def get_analog_instrument_input(self) -> AnalogInstrumentInput: 
        pass

    @abstractmethod
    def get_tyre_rotation_input(self) -> TyreRotationInput:
        pass

    @abstractmethod
    def get_constant_data(self) -> ConstantData | None:
        pass
    
    @abstractmethod
    def get_telemetry(self) -> dict[str,Any]:
        pass