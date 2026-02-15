import sys
import msvcrt
import asyncio

from pathlib import Path
import pytest

src = Path(__file__).parent.parent / 'src'
sys.path.append(str(src))

from msg.server_builder import build_rxpy_osc_server
from osc_receiver.osc_receiver import OSCReceiver
async def key_listener():
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode(errors="ignore")
            if(key == 'q'):
                break                
        await asyncio.sleep(0.05)  # CPU負荷軽減
        
@pytest.mark.asyncio
async def test_rxpy_server():
    server = build_rxpy_osc_server(0.08,"127.0.0.1", 8765)
    server.run()
    #receiver = OSCReceiver()
    #receiver.launch()
    await asyncio.Future()
    server.shutdown()
