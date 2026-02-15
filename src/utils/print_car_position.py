import sys
import os
import time
from pathlib import Path

src = Path(__file__).parent.parent
sys.path.append(str(src))

print(sys.path)
from msg.raw_data.pyaccsharedmemory import accSharedMemory

def print_car_pos():
    asm = accSharedMemory()
    while(True):
        sm = asm.read_shared_memory()
        if(sm != None):
            os.system('cls')
            print(sm.Graphics.car_coordinates)
        time.sleep(0.1)

if __name__ == "__main__":
    print_car_pos()