import enet
import handler.client as client
from handler.packet import TankPacket
from handler.packet import PackTankPacket
from handler.variants import Variants
from globals import *


host = enet.Host(enet.Address(b"0.0.0.0", 17091), 32, 1, 0, 0)
host.checksum = enet.ENET_CRC32
host.compress_with_range_coder()
print("Server listening on port 17091")


try:
    while True:
        event = host.service(1000)
        if event.type == enet.EVENT_TYPE_CONNECT:
            client.OnConnected(event.peer, event.peer.address, host)
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            client.OnDisconnected(event.peer, event.peer.address, host)
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            client.OnReceived(event.peer, event.peer.address, host, event.packet)
except KeyboardInterrupt:
    pass
