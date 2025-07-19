import asyncio
from telemetry.telemetry_tyre import TelemetryTyre
from ac_telemetry import ACTelemetry
from message import message_packer as msg_packer
import cfg_loder
from telemetry.telemetry_analog_instruments import TelemetryAnalogInstruments
from logging import getLogger
logger = getLogger('def')

class MessageProducer:
    ac_telemetry : ACTelemetry
    tele_tyre : TelemetryTyre
    tele_analog : TelemetryAnalogInstruments
    first_message : bool

    def __init__(self,ac_telemetry : ACTelemetry,tele_tyre :TelemetryTyre,tele_analog : TelemetryAnalogInstruments):
        self.ticker = Ticker(0.166666)
        self.ac_telemetry = ac_telemetry
        self.tele_tyre = tele_tyre
        self.tele_analog = tele_analog
        self.first_message = True

    async def wait_new_msg(self):
        async for _ in self.ticker:
            sm = self.ac_telemetry.get_sm()
            if(sm == None):
                continue
            stc_msg = self.create_static_msg(sm)
            tick_msg = self.create_tick_msg(sm)
            final_rslt = ",".join(stc_msg + tick_msg)
            yield final_rslt

    def create_static_msg(self,sm):
        if not(self.ac_telemetry.ac_on_launch or self.first_message):
            return []
        
        self.first_message = False
        logger.info(f'CFG読み込み')
        cfg = cfg_loder.load_cfg(sm.Static.car_model.rstrip('\x00'))
        
        self.update_telemetry_data_soruce(sm,cfg['analog_instruments'])

        # メッセージの作成
        stc_ls = msg_packer.pack(sm.Static,msg_packer.STATIC_TABLE)
        car_ls = msg_packer.pack(cfg,msg_packer.CAR_CFG_TABLE)
        
        return stc_ls + car_ls
    
    def update_telemetry_data_soruce(self,sm,cfg):
        # Telemetryデータソースの更新
        self.tele_tyre.update_data_src(sm)
        self.tele_analog.update_data_src(cfg)
        
    def create_tick_msg(self,sm) -> list[str]:
        self.tele_tyre.update(sm)
        tele_anlg_data = self.tele_analog.create(sm)
        gra_ls = msg_packer.pack(sm.Graphics,msg_packer.GRAPHICS_TABLE)
        phy_ls = msg_packer.pack(sm.Physics, msg_packer.PHYSICS_TABLE)
        tyre_ls = msg_packer.pack(self.tele_tyre,msg_packer.TYRE_TABLE)
        anlg_ls = msg_packer.pack(tele_anlg_data,msg_packer.ANALOG_INSTRUMENTS_TABLE)
        return gra_ls + phy_ls + tyre_ls + anlg_ls


def create():
    sm_ticker = ACTelemetry()
    telemetry_tyre = TelemetryTyre()
    tele_analog = TelemetryAnalogInstruments()
    return MessageProducer(sm_ticker,telemetry_tyre,tele_analog)


import asyncio
from typing import AsyncIterator

class Ticker:
    def __init__(self, interval: float):
        self.interval = interval 
        self._running = False

    def __aiter__(self) -> AsyncIterator[int]:
        self._running = True
        return self

    async def __anext__(self) -> int:
        if not self._running:
            raise StopAsyncIteration
        await asyncio.sleep(self.interval)
        return None

    def stop(self):
        self._running = False