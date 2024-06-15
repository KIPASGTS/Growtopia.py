import os
import struct
import time
class Item:
    def __init__(self):
        self.Name = ""
        self.TexturePath = ""
        self.ExtraFilePath = ""
        self.PetName = ""
        self.PetPrefix = ""
        self.PetSuffix = ""
        self.PetAbility = ""
        self.ExtraOptions = ""
        self.TexturePath2 = ""
        self.ExtraOptions2 = ""
        self.PunchOption = ""
        self.StrData11 = ""
        self.StrData15 = ""
        self.StrData16 = ""
        self.ItemID = 0
        self.TextureHash = 0
        self.Val1 = 0
        self.DropChance = 0
        self.ExtrafileHash = 0
        self.AudioVolume = 0
        self.WeatherID = 0
        self.SeedColor = 0
        self.SeedOverlayColor = 0
        self.GrowTime = 0
        self.IntData13 = 0
        self.IntData14 = 0
        self.Rarity = 0
        self.Val2 = 0
        self.IsRayman = 0
        self.EditableType = 0
        self.ItemCategory = 0
        self.ActionType = 0
        self.HitsoundType = 0
        self.ItemKind = 0
        self.TextureX = 0
        self.TextureY = 0
        self.SpreadType = 0
        self.CollisionType = 0
        self.BreakHits = 0
        self.ClothingType = 0
        self.MaxAmount = 0
        self.SeedBase = 0
        self.SeedOverlay = 0
        self.TreeBase = 0
        self.TreeLeaves = 0
        self.IsStripeyWallpaper = 0


class ItemCallback:

    def __init__(self) -> None:
        self.Items = {}
        self.ItemCount = 0
        self.ItemVersion = 0
        self.ProtonKey = "PBG892FXX982ABC*"
        self.FileHash = 0
        self.BufferForUpdatingItems = None
    
    def GetItems(self, itemid) -> Item:
        if itemid < 0 or itemid > len(self.Items): return self.Items[0] #return Blank
        return self.Items[itemid]

def get_hash(data, length):
    acc = 0x55555555 & 0xFFFFFFFF
    if length == 0:
        for c in data:
            acc = ((acc >> 27) & 0xFFFFFFFF) + ((acc << 5) & 0xFFFFFFFF) + ord(c)
            acc = acc & 0xFFFFFFFF
    else:
        for i in range(length):
            acc = ((acc >> 27) & 0xFFFFFFFF) + ((acc << 5) & 0xFFFFFFFF) + data[i]
            acc = acc & 0xFFFFFFFF
    return acc



def SerializeItems(path: str) -> ItemCallback:
    callback = ItemCallback()
    if not os.path.exists(path):
        print(f"{path} not exists!")
        os._exit(1)
    
    file = open(path, 'rb')
    data = file.read()
    file.close()

    callback.BufferForUpdatingItems = bytearray(60 + len(data))
    struct.pack_into('<I', callback.BufferForUpdatingItems, 0, 4)
    struct.pack_into('<I', callback.BufferForUpdatingItems, 4, 16)
    struct.pack_into('<i', callback.BufferForUpdatingItems, 8, -1)
    struct.pack_into('<I', callback.BufferForUpdatingItems, 16, 8)
    struct.pack_into('<I', callback.BufferForUpdatingItems, 56, len(data))
    callback.BufferForUpdatingItems[60:] = data   

    memPos = 0
    callback.FileHash = get_hash(data, len(data))
    callback.ItemVersion = struct.unpack_from("<H", data, memPos)[0]; memPos += 2
    callback.ItemCount = struct.unpack_from("<I", data, memPos)[0]; memPos += 4
    start_time = time.time()
    for i in range(0, callback.ItemCount):
        item = Item()
        item.ItemID = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.EditableType = data[memPos]; memPos += 1
        item.ItemCategory = data[memPos]; memPos += 1
        item.ActionType = data[memPos]; memPos += 1
        item.HitsoundType = data[memPos]; memPos += 1

        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        for j in range(0, strLen):
            item.Name += chr(data[memPos] ^ ord(callback.ProtonKey[(item.ItemID + j) % len(callback.ProtonKey)])); memPos += 1
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.TexturePath = data[memPos:memPos+strLen].decode(); memPos += strLen
        item.TextureHash = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.ItemKind = data[memPos]; memPos += 1
        item.Val1 = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.TextureX = data[memPos]; memPos += 1
        item.TextureY = data[memPos]; memPos += 1
        item.SpreadType = data[memPos]; memPos += 1
        item.IsStripeyWallpaper = data[memPos]; memPos += 1
        item.CollisionType = data[memPos]; memPos += 1
        item.BreakHits = data[memPos]; memPos += 1
        item.DropChance = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.ClothingType = data[memPos]; memPos += 1
        item.Rarity = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.MaxAmount = data[memPos]; memPos += 1
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.ExtraFilePath = data[memPos:memPos+strLen].decode(); memPos += strLen
        item.ExtrafileHash = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.WeatherID = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.PetName = data[memPos:memPos+strLen].decode(); memPos += strLen
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.PetPrefix = data[memPos:memPos+strLen].decode(); memPos += strLen
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.PetSuffix = data[memPos:memPos+strLen].decode(); memPos += strLen
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.PetAbility = data[memPos:memPos+strLen].decode(); memPos += strLen
        item.SeedBase = data[memPos]; memPos += 1
        item.SeedOverlay = data[memPos]; memPos += 1
        item.TreeBase = data[memPos]; memPos += 1
        item.TreeLeaves = data[memPos]; memPos += 1
        item.SeedColor = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.SeedOverlay = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        memPos += 4; #Ingredients
        item.GrowTime = struct.unpack_from('<I', data, memPos)[0]; memPos += 4
        item.Val2 = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.IsRayman = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.ExtraOptions = data[memPos:memPos+strLen].decode(); memPos += strLen
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.TexturePath2 = data[memPos:memPos+strLen].decode(); memPos += strLen
        strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2
        item.ExtraOptions2 = data[memPos:memPos+strLen].decode(); memPos += strLen
        memPos += 80
        if callback.ItemVersion >= 11: strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2; memPos += strLen
        if callback.ItemVersion >= 12: memPos += 13
        if callback.ItemVersion >= 13: memPos += 4
        if callback.ItemVersion >= 14: memPos += 4
        if callback.ItemVersion >= 15: memPos += 25; strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2; memPos += strLen
        if callback.ItemVersion >= 16: strLen = struct.unpack_from('<H', data, memPos)[0]; memPos += 2; memPos += strLen
        if callback.ItemVersion >= 17: memPos += 4
        if callback.ItemVersion >= 18: memPos += 4
        callback.Items[item.ItemID] = item
        
    end_time = time.time()
    print(f"Items.dat serialized! item: {callback.ItemCount} version: {callback.ItemVersion}: hash: {callback.FileHash}, loaded: {int((end_time - start_time) * 1000)}ms")
    
    return callback

