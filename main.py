import os
import websockets
import asyncio
from server import TelemetryServer
import message.message_producer as message_producer
import json
from logging import getLogger, StreamHandler, DEBUG ,Formatter,config



async def run_mock_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("接続成功")
        while True:
            try:
                msg = await websocket.recv()
                splited_msg = msg.split(',')
                chunk_size = 3
                msg_chunks = [splited_msg[i:i + chunk_size] for i in range(0,len(splited_msg),chunk_size)]
                
                #for msg in msg_chunks:
                #    print(f'{msg}')    

                [print(data) for data in filter(lambda msg : msg[0] == 'rpmRot',msg_chunks)]
            except websockets.exceptions.ConnectionClosed:
                print("切断されました")
                break
            
def logger_setup():
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)

    config.dictConfig(log_conf)


async def main():
    logger_setup()
    logger = getLogger('def')
    logger.info('hora')
    msg_prdcr = message_producer.create()
    server = TelemetryServer(msg_prdcr)
    asyncio.create_task(run_mock_client())

    server_task = asyncio.create_task(server.run())
    await server_task

if __name__ == "__main__":
    asyncio.run(main())