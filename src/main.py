import sys
import asyncio
from msg import server_builder

async def wait_for_quit():
    loop = asyncio.get_running_loop()
    print("Press q key and enter to shutdown")
    while True:
        # 非同期で入力を待つ
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if line.strip().lower() == "q":
            print("Q key pressed, shutting down server")
            break

async def main():
    tick_rate = 1/160 # Double fps of 80fps. 
    server = server_builder.build_rxpy_osc_server(tick_rate,"127.0.0.1", 8765)
    server.run()
    
    await wait_for_quit()
    server.shutdown()

    
if __name__ == "__main__":
    asyncio.run(main())