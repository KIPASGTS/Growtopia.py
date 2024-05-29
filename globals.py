import items.items
ItemsData = items.items.SerializeItems("database/items.dat")

Peers = {}

def GetPlayer(peer):
    if peer in Peers:
        return Peers[peer]
    else: return None
