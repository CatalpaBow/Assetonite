from msg.message.tyre_rotation_calculator import TyreRotationCalculator,TyreRotationInput
from msg.message.analog_instrument_angle_calculator import AnalogInstrumentAngleCalculator,AnalogInstrumentInput,AnalogInstrumentConstant
from msg.message.i_message_source import IMessageSource,ConstantData

class MessageBuilder:
    def __init__(self,tyre_rot : TyreRotationCalculator = None):
        self.tyre_rot : TyreRotationCalculator = tyre_rot
        self.instrument_angle_calculator : dict[str,AnalogInstrumentAngleCalculator] = None

    def build(self,src : IMessageSource) -> dict:
        #Update Constant

        const_data = src.get_constant_data() 
        if(const_data != None):
            self.update_constant(const_data)

        #Calculate state
        tyre_in : TyreRotationInput = src.get_tyre_rotation_input()
        tyre_out = self.tyre_rot.calculate(tyre_in)
        
        instrument_out = {}
        instrument_in : AnalogInstrumentInput = src.get_analog_instrument_input()
        for name,val in instrument_in._asdict().items():
            if(name in self.instrument_angle_calculator):
                instrument_out[name] = self.instrument_angle_calculator[name].calc_angle(val)
        
        #BuildMessage
        return {
            "Telemetry" : src.get_telemetry(), 
            "TyreRot" : tyre_out,
            "AnalogInstrument" : instrument_out
        }
    def update_constant(self,constant : ConstantData):
        self.tyre_rot = TyreRotationCalculator(constant.tyre_constant)
        self.instrument_angle_calculator = {const.name : AnalogInstrumentAngleCalculator(const.step,const.lut) for const in constant.analog_instrument_constant}
