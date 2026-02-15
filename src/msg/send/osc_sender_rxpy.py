from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc.udp_client import UDPClient
from logging import getLogger
from msg.send.osc_serializer import OSCSerializer
from msg.send.osc_packed_message import OSCContentData
logger = getLogger('def')
MTU = 1200

class OSCSenderRxPy:
    def __init__(self,ip : str, port : int):
        self.client = UDPClient(ip, port) 
        logger.info(f"UDP Client Setuped IP:{ip} Port:{port}")
        
    def send(self,msg_dic : dict):
            serialized = OSCSerializer.serialize(msg_dic)
            bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
            packet_size = 0
            for content in serialized:
                #print(f"name:{content.msg} val:{content.value}")
                msg = osc_message_builder.OscMessageBuilder(address = content.msg)
                if(isinstance(content.value ,list)):
                    for item in content.value:
                        msg.add_arg(item)
                else : 
                    msg.add_arg(content.value)
                osc_msg = msg.build()
                bundle.add_content(osc_msg)
                packet_size += len(osc_msg.dgram)
                if(packet_size > MTU):
                    osc_bundle = bundle.build()
                    self.client.send(osc_bundle)
                    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
                    packet_size = 0
            if(packet_size > 0):
                osc_bundle = bundle.build()
                self.client.send(osc_bundle)
            