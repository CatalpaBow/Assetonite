import traceback
import copy
import math
from enum import Enum
from typing import Iterable,Any

from reactivex import operators as ops
import reactivex as rx
from logging import getLogger

from msg.raw_data.telemetry_reader_implement import TelemetryReaderImplement
from msg.message_source.message_source_provider import MessageSourceProvider
from msg.message.message_builder import MessageBuilder
from msg.send.osc_sender_rxpy import OSCSenderRxPy

logger = getLogger('def')
SENDABLE_TYPES = (str, bytes, bool, int, float, list)

class MessageServerRxPy:
    def __init__(
        self,
        telemetry_reader : TelemetryReaderImplement,
        msg_src_prvdr : MessageSourceProvider,
        msg_bldr : MessageBuilder,
        sender :  OSCSenderRxPy,
        tick_rate : float):

        self.disposer = None
        self.telemetry_reader = telemetry_reader
        self.msg_src_prvdr = msg_src_prvdr
        self.msg_bldr = msg_bldr
        self.sender = sender
        self.tick_rate = tick_rate
    
    def __del__(self):
        self.shutdown()

    def run(self):
        logger.info("Start launch server")
        self.change_filter = make_change_filter()
        self.disposer = rx.interval(self.tick_rate).pipe(
            ops.map(lambda _ : self.telemetry_reader.read()),
            ops.filter(lambda tele : tele != None),
            ops.map(lambda tele : self.msg_src_prvdr.create(tele)),
            ops.map(self.msg_bldr.build),
            ops.filter(lambda tele : self.change_filter(tele))
        ).subscribe(
            on_next = self.sender.send,
            on_error = lambda error : print_trace_back()
        )

    def shutdown(self):
        if(self.disposer != None):
            self.disposer.dispose()
            logger.info("Server shutdowned.")
            

def make_change_filter():
    previous_msg: dict[str, Any] | None = None

    def extract_value(value: Any) -> Any:
        """SENDABLE_TYPES, Enum, Iterable から送信可能値を抽出"""
        if isinstance(value, SENDABLE_TYPES):
            return value
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, Iterable) and not isinstance(value, (dict)):
            return list(value)
        return None
    
    def _remove_same_value(dic: dict[str, Any], path: list[str] = []):
        nonlocal previous_msg

        dic_copy = copy.deepcopy(dic)  
        
        for key, value in dic_copy.items():
            full_path = path + [key]
            content_val = extract_value(value)

            if content_val is not None and previous_msg is not None:
                # previous_msg から同じ位置の値を取得
                prev_val = previous_msg
                try:
                    for p in full_path:
                        prev_val = prev_val[p]
                except (KeyError, TypeError):
                    prev_val = None
                    #print(f"Not found:{full_path}")

                # floatの場合は誤差を考慮して比較
                if isinstance(content_val,float):
                    if math.isclose(prev_val,content_val,abs_tol=1e-4):
                        #print(f"delete key:{key} value{content_val}")
                        del dic[key]
                        continue
                
                if isinstance(content_val,Iterable) :
                    is_same = True
                    zip_val = prev_val
                    if isinstance(prev_val,Enum):
                        zip_val = prev_val.name
                    for p,c in zip(zip_val,content_val):
                        if(p != c):
                            is_same = False 
                            break
                    if(is_same):
                        del dic[key]
                        continue
                # 値が同じなら削除
                if prev_val == content_val:
                    #print(f"delete key:{key} value{content_val}")
                    del dic[key]
                    continue

            if isinstance(value, dict):
                _remove_same_value(dic[key], full_path)

    def remove_same_value(dic: dict[str, Any], path: list[str] = []) -> dict[str, Any]:
        nonlocal previous_msg
        _temp = copy.deepcopy(dic)
        _remove_same_value(dic)
        previous_msg = _temp
        return dic

    return remove_same_value



def print_trace_back():
    print(traceback.format_exc())
    traceback.print_exc()