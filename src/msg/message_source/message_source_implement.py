from dataclasses import dataclass
from typing import Any,Iterable
from enum import Enum

from msg.send.osc_serializer import SENDABLE_TYPES
from msg.message_source.i_telemtry_reader import BaseTelemtryData
from msg.message.i_message_source import IMessageSource,ConstantData
from msg.message.analog_instrument_angle_calculator import AnalogInstrumentInput
from msg.message.tyre_rotation_calculator import TyreRotationInput,TyreRotationConstant

@dataclass
class MessageSourceImplement(IMessageSource):
    telemetry : BaseTelemtryData
    const_data : ConstantData

    def get_analog_instrument_input(self) -> AnalogInstrumentInput: 
        return AnalogInstrumentInput(
            self.telemetry.Physics.rpm,
            self.telemetry.Physics.speed_kmh,
            self.telemetry.Physics.fuel,
            self.telemetry.Physics.turbo_boost,
            0#Temp value
        )

    def get_tyre_rotation_input(self) -> TyreRotationInput:
        return TyreRotationInput(
            self.telemetry.Physics.steer_angle,
            self.telemetry.Physics.wheel_angular_s,
            self.telemetry.Physics.camber_rad,
        )
    
    def get_constant_data(self) -> ConstantData:
        return self.const_data
    
    def get_telemetry(self) -> dict[str,Any]:
        recording_dic = {}
        atr_dic = vars(self.telemetry)
        atr_to_dic(atr_dic,recording_dic)
        return recording_dic

def atr_to_dic(atr_dic,recording_dic) -> dict[str,Any]:
    for key,value in atr_dic.items():
        content_val = None
        if isinstance(value, SENDABLE_TYPES):
            content_val = value
        elif isinstance(value,Enum):
            content_val =  value.name
        elif isinstance(value,Iterable) and not isinstance(value, dict):
            content_val = list(value)
            
        if(content_val != None):
            recording_dic[key] = value
            continue
        recording_dic[key] = {}
        atr_to_dic(vars(value),recording_dic[key])