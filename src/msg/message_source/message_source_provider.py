from typing import Iterator

from logging import getLogger

from msg.message.i_message_source import ConstantData
from msg.message.analog_instrument_angle_calculator import AnalogInstrumentConstant
from msg.message.tyre_rotation_calculator import TyreRotationConstant

from msg.message_source.i_car_config_loader import ICarConfigLoader,BaseCarConifg
from msg.message_source.i_telemtry_reader import ITelemetryReader,BaseTelemtryData
from msg.message_source.message_source_implement import MessageSourceImplement,IMessageSource

logger = getLogger('def')

class MessageSourceProvider:
    def __init__(self,cfg_loader : ICarConfigLoader):
        self.first_data : bool = True
        self.cfg_loader : ICarConfigLoader = cfg_loader        

    def create(self,telemetry : BaseTelemtryData) -> IMessageSource:
        const_data : ConstantData = None
        if(telemetry.on_launch() or self.first_data):
            reason  = ""
            if(telemetry.on_launch()):
                reason = "Game lanched."
            if(self.first_data):
                reason = "First message."
            logger.info(f"Reload static data. Reason:{reason}")
            self.first_data = False
            car_name = telemetry.Static.car_model.rstrip('\x00')
            const_data = self.reload_constant_data(car_name)
        return MessageSourceImplement(telemetry,const_data)
    
    def reload_constant_data(self,car_name : str) -> ConstantData:
        cfg : BaseCarConifg = self.cfg_loader.load(car_name)
        analog_instrument_const :  Iterator[AnalogInstrumentConstant] = cfg.read_analog_instrument_const()
        tyre_const : TyreRotationConstant = cfg.read_tyre_const()
        return ConstantData(analog_instrument_const,tyre_const)