from pythonosc import dispatcher, osc_server
import threading
import asyncio

async def get_server():
    loop = asyncio.get_running_loop()
    disp = dispatcher.Dispatcher()
    disp.map("/Telemetry/Graphics/car_coordinates/x", handler)
    server = osc_server.AsyncIOOSCUDPServer(("127.0.0.1", 8765), disp,loop)

    transport, protocol = await server.create_serve_endpoint()
    return transport

from osc_receiver.telemetry_plotter import TelemetryPlotter
class OSCReceiver:
    server : osc_server.ThreadingOSCUDPServer

    def launch(self):
        #self.tele_pltr = TelemetryPlotter()
        #self.hdlr = CarCordinateHandler(self.tele_pltr)
        disp = dispatcher.Dispatcher()
        #disp.map("/Telemetry/Graphics/car_coordinates", self.hdlr.handler())
        disp.map('/*',zenbu_hdlr)
        self.server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8765), disp)
        self.thread = threading.Thread(target=self.server.serve_forever, name='thread1',daemon = True)
        self.thread.start()

    def close(self):
        if not (self.server == None):
            self.server.server_close()
    
def zenbu_hdlr(addr, *args):
    print(f'{addr},{args}')
    pass
def handler(addr, fnc_args: list[any] , *args):
    pass
class CarCordinateHandler:
    def __init__(self,tele_pltr : TelemetryPlotter):
        self.queue =  CoordinateQueue()
        self.tele_pltr = tele_pltr

    def handler(self):
        def _handler(addr, *args):
            #print()
            x = args[0]
            z = args[2]
            self.tele_pltr.update(x,z)
        return _handler


class CoordinateQueue():
    def __init__(self):
        self.x = None
        self.y = None

    def clear(self):
        self.x = None
        self.y = None

    def set_x(self,val):
        self.x = val
        if(self.y != None):
            return True
        else:
            return False
        
    def set_y(self,val):
        self.y = val
        if(self.x != None):
            return True
        else:
            return False
    
    def pop(self) -> tuple[any,any]:
        data =  (self.x,self.y)
        self.clear()
        return data
    