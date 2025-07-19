import asyncio
from pyaccsharedmemory import accSharedMemory
import pyaccsharedmemory
from typing import Optional
import asyncio
from pyaccsharedmemory import ACC_STATUS

class ACTelemetry:
    ac_on_launch = False
    ac_on_close = False
    _ac_status_previous : ACC_STATUS
    def __init__(self, asm = accSharedMemory(), tick_rate=0.016):
        self._asm = asm
        self._tick_event = asyncio.Event()
        self._ac_status_previous = ACC_STATUS.ACC_OFF

    def get_sm(self) -> pyaccsharedmemory.ACC_map:
        sm = self._asm.read_shared_memory()
        # update ac event
        if(sm == None):
            return sm
        
        if(self._ac_status_previous == ACC_STATUS.ACC_OFF and sm.Graphics.status == ACC_STATUS.ACC_LIVE):
            self.ac_on_launch = True
        else:
            self.ac_on_launch = False

        if(self._ac_status_previous == ACC_STATUS.ACC_LIVE and sm.Graphics.status == ACC_STATUS.ACC_OFF) :
            self.ac_on_close = True
        else:
            self.ac_on_close = False
        self._ac_status_previous = sm.Graphics.status
        return sm