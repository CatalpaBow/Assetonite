#from msg.senders.packer import PackedMessage
from typing import Any
from dataclasses import dataclass

@dataclass
class OSCContentData:
    msg: str
    value: Any

class OSCPackedMessage:
    def __init__(self,contents: list[OSCContentData]):
        self.contents = contents