from multiprocessing import shared_memory
import numpy as np
import struct
CAR_STRUCT = "fff"  
CAR_SIZE = struct.calcsize(CAR_STRUCT)

sm = shared_memory.SharedMemory(name="Local\\ACSSharedMemoeryEXMod")
x,y,z = struct.unpack(CAR_STRUCT,sm.buf[:CAR_SIZE])
print(f"x:{x} y:{y} z:{z}")
sm.close()
