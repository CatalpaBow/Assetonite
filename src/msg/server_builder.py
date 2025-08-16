'''
import msg.producer.producer
from msg.message_server import MessageServer
from msg.senders.osc import *
'''
from msg.message_server_rxpy import MessageServerRxPy

from msg.raw_data.telemetry_reader_implement import TelemetryReaderImplement
from msg.raw_data.cfg_loder import ConfigLoaderImplement
from msg.message_source.message_source_provider import MessageSourceProvider
from msg.message.message_builder import MessageBuilder
from msg.send.osc_sender_rxpy import OSCSenderRxPy

def build_rxpy_osc_server(tick_rate : float,ip :str, port : int) -> MessageServerRxPy:
    telemetry_reader = TelemetryReaderImplement()
    cfg_loader = ConfigLoaderImplement()
    msg_src_plvdr = MessageSourceProvider(cfg_loader)
    msg_bldr = MessageBuilder()
    sender = OSCSenderRxPy(ip,port)
    return MessageServerRxPy(telemetry_reader,msg_src_plvdr,msg_bldr,sender,tick_rate)
