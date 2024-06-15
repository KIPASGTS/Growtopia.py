import random
import time
import pickle
import os
import struct

class Tile:
    Fg = 0
    Bg = 0
    Flags = 0
    Label = ""

    HitTotal = 0
    HitTime = 0

class World:
    def __init__(self) -> None:
        self.WorldName = ""
        self.SizeX = 100
        self.SizeY = 60
        self.OwnerUID = 0
        self.Tiles = []

        #unsaved
        self.TotalPlayer = 0
        self.TotalTiles = 0

    def save_world(self):
        buffer = bytearray()
        buffer.extend(struct.pack("<b", len(self.WorldName)))
        buffer.extend(self.WorldName.encode())
        buffer.extend(struct.pack("<b", self.SizeX))
        buffer.extend(struct.pack("<b", self.SizeY))
        buffer.extend(struct.pack("<i", self.OwnerUID))

        for tile in self.Tiles:
            buffer.extend(struct.pack("<h", tile.Fg))
            buffer.extend(struct.pack("<h", tile.Bg))
            buffer.extend(struct.pack("<i", tile.Flags))

            buffer.extend(struct.pack("<b", len(tile.Label)))
            buffer.extend(tile.Label.encode())
        
        file = open(f'database/world/_{self.WorldName}.bin', 'wb')
        file.write(buffer)
        file.close()


class WorldCallback:
    Worlds = {}
def CreateWorld(name, sizex, sizey) -> World:
    random.seed(int(time.time()))
    world = World()
    world.WorldName = name
    world.SizeX = sizex
    world.SizeY = sizey
    world.TotalTiles = world.SizeX * world.SizeY

    random_pos_door = random.randint(0, world.TotalTiles // (world.TotalTiles // 100 - 4) + 2)
    for i in range(world.TotalTiles):
        tile = Tile()
        if 2500 <= i < 5400 and random.randint(0, 49) == 0: tile.Fg = 10
        elif 2500 <= i < 5400:
            if i > 5000:
                if random.randint(0, 7) < 3: tile.Fg = 4
                else: tile.Fg = 2
            else: tile.Fg = 2
        elif i >= 5400: tile.Fg = 8
        if i == 2400 + random_pos_door: tile.Label = "EXIT"; tile.Fg = 6
        if i == 2500 + random_pos_door: tile.Fg = 8
        if i >= 2500: tile.Bg = 14
        world.Tiles.append(tile)

    worlds.Worlds[world.WorldName] = world
    return world

def GetWorld(name: str) -> World:
    name = name.upper()
    if name in worlds.Worlds:
        return worlds.Worlds[name]
    
    if os.path.exists(f'database/world/_{name}.bin'):
        file = open(f'database/world/_{name}.bin', 'rb')
        buffer = file.read()
        file.close()

        offset = 0
        temp_world = World()

        nameLen = struct.unpack_from('<b', buffer, offset)[0]; offset += 1
        temp_world.WorldName = buffer[offset : offset + nameLen].decode(); offset += nameLen
        temp_world.SizeX = struct.unpack_from('<b', buffer, offset)[0];    offset += 1
        temp_world.SizeY = struct.unpack_from('<b', buffer, offset)[0];    offset += 1
        temp_world.OwnerUID = struct.unpack_from('<i', buffer, offset)[0]; offset += 4
        temp_world.TotalTiles = temp_world.SizeX * temp_world.SizeY
        for i in range(0, temp_world.SizeX * temp_world.SizeY):
            tile = Tile()
            tile.Fg = struct.unpack_from('<h', buffer, offset)[0];    offset += 2
            tile.Bg = struct.unpack_from('<h', buffer, offset)[0];    offset += 2
            tile.Flags = struct.unpack_from('<i', buffer, offset)[0]; offset += 4

            labelLen = struct.unpack_from('<b', buffer, offset)[0]; offset += 1
            tile.Label = buffer[offset : offset + labelLen].decode(); offset += labelLen
            temp_world.Tiles.append(tile)
        
        worlds.Worlds[name] = temp_world
        return temp_world

    return CreateWorld(name, 100, 60)

worlds = WorldCallback()