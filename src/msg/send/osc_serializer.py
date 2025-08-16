from enum import Enum
from typing import Iterator
from msg.send.osc_packed_message import OSCContentData
from collections.abc import Iterable
SENDABLE_TYPES = (str, bytes, bool, int, float, list)
class OSCSerializer: 
    @staticmethod
    def serialize(dic_parent :dict[str,any],path : str = "") -> Iterator[OSCContentData]:
        for key,value in dic_parent.items():
            full_path = path + '/' + key

            content_val = None
            if isinstance(value, SENDABLE_TYPES):
                content_val = value
            elif isinstance(value,Enum):
                content_val =  value.name
            elif isinstance(value,Iterable) and not isinstance(value, dict):
                content_val = list(value)
                
            if(content_val != None):
                yield OSCContentData(full_path,content_val)
                continue
            yield from OSCSerializer.serialize(value,full_path)