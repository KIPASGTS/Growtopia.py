import items.items
from players.player import *
ItemsData = items.items.SerializeItems("database/items.dat")

Peers = {}

def GetPlayer(peer) -> Player:
    if peer in Peers:
        return Peers[peer]
    else: return None
