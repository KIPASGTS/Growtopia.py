import pickle
import os
class PlayerClothes:
    Hair     = 0
    Shirt    = 0
    Pants    = 0
    Feet     = 0
    Face     = 0
    Hand     = 0
    Back     = 0
    Mask     = 0
    Necklace = 0
    Ances    = 0
    SkinColor = 2022356223

class PlayerRole:
    PLAYER = 0
    VIP = 1
    ADMIN = 2
    MODS = 3
    DEVS = 4
    FOUNDER = 5

class PlayerPet:
    def __init__(self, pet_name = 'root', pet_pos_x = 0, pet_pos_y = 0) -> None:
        self.petName = pet_name
        self.posX = pet_pos_x
        self.posY = pet_pos_y

    def get_position(self):
        return [self.posX, self.posY]
    
    def set_pos_x_y(self, posX, posY):
        self.posX = posX
        self.posY = posY


class PlayerInventory:
    def __init__(self, itemid = 0, amount = 0) -> None:
        self.ItemID = itemid
        self.Amount = amount

class Player:
    def __init__(self) -> None:
        self.tankIDName = ''
        self.tankIDPass = ''
        self.requestedName = ''
        self.requestedGuestID = 0
        self.UserID = -1
        self.NetID = 0
        self.Nicked = ''
        self.Country = ''
        self.Inventory = [PlayerInventory(itemid=18, amount=1), PlayerInventory(itemid=32, amount=1)]
        self.Clothes = PlayerClothes()
        self.PetCustom = PlayerPet("kipas")
        self.Suspended = False
        self.InventoryAmount = 16
        self.CurrentWorld = ''
        self.PosX = 0
        self.PosY = 0
        self.Role = 0
        self.UpdateClothes = False
        self.DebugMode = False


    def GetDisplayName(self) -> str:
        if self.Nicked != '': return self.Nicked
        nickname = ''
        if self.Role == PlayerRole.PLAYER: nickname = ''
        elif self.Role == PlayerRole.VIP: nickname = '[`cVIP`w] '
        elif self.Role == PlayerRole.ADMIN: nickname = '[`4ADMIN`w] '
        elif self.Role == PlayerRole.MODS: nickname = '`#@'
        elif self.Role == PlayerRole.DEVS: nickname = '`6@'
        elif self.Role == PlayerRole.FOUNDER: nickname = '`b@'
        nickname += self.requestedName + '_' + str(self.requestedGuestID) if self.tankIDName == '' and self.tankIDPass == '' else self.tankIDName

        return nickname

def register_player(player: Player, username: str, password: str) -> bool:
    player.tankIDName = username
    player.tankIDPass = password
    player.UserID = len(os.listdir('database/players')) + 1
    with open(f'database/players/_{player.tankIDName.lower()}.bin', "wb") as file:
        pickle.dump(player, file)
        file.close()

    return os.path.exists(f'database/players/_{player.tankIDName.lower()}.bin')

def save_player(player: Player):
    with open(f'database/players/_{player.tankIDName.lower()}.bin', "wb") as file:
        pickle.dump(player, file)
        file.close()

def load_player(username: str) -> Player:
    if os.path.exists(f'database/players/_{username.lower()}.bin') == False:
        return None
    else:
        with open(f'database/players/_{username.lower()}.bin', "rb") as file:
            data = pickle.load(file)
            file.close()
            return data
        
    
