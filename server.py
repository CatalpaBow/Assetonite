import asyncio
import websockets
from message.message_producer import MessageProducer
import traceback
class TelemetryServer:
    msg_prdcr : MessageProducer

    def __init__(self, msg_prdcr : MessageProducer):
        self.tasks = []
        self.msg_prdcr = msg_prdcr

    async def run(self):
        try:
            async with websockets.serve(self.client_handler(), "localhost", 8765):
                print("🚀 WebSocketサーバー起動: ws://localhost:8765")
                await asyncio.Future()  # 無限待機（Ctrl+Cで終了）
        except asyncio.CancelledError:
            print("🛑 サーバー停止要求を受信")
        finally:
            print("🛑 サーバー停止")

    def client_handler(self):
        async def handler(websocket :websockets.ServerConnection):
            print("クライアント接続:", websocket.remote_address)
            try:
                async for msg in self.msg_prdcr.wait_new_msg():
                    await websocket.send(msg)   
            except websockets.exceptions.ConnectionClosed:
                print('クライアントが切断されました')
            except Exception as e:
                print(f"ClientHandler内で例外{e}")
                traceback.print_exc()

            '''
            while(True):
                msg = await self.msg_prdcr.msg_queue.get()
                await websocket.send(msg)
            '''
        return handler