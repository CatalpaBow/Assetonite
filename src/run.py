from msg import *
from msg.message_server_rxpy import MessageServerRxPy
async def run(server :MessageServerRxPy):
    await server.run()