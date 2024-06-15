import enet
import struct
import random
import time

from players.player import *
from globals import *
from worlds.world import GetWorld
from variants.packet import *
from handler.packet import *

def OnPlayerUpdateState(peer):
    if GetPlayer(peer).CurrentWorld == '': return

def OnPlayerRespawn(peer, causeSpike=False):
    if GetPlayer(peer).CurrentWorld == '': return
    world = GetWorld(GetPlayer(peer).CurrentWorld)

    doorPosition = [0, 0]
    for i in range(0, len(world.Tiles)):
        if world.Tiles[i].Fg == 6: #Main Door
            doorPosition = [(i % world.SizeX) * 32, (i // world.SizeX) * 32]

    if causeSpike == False: OnKilled(peer, GetPlayer(peer).NetID, 0) #Respawn biasa ga ada animasi
    OnSetPos(peer, GetPlayer(peer).NetID, 2000, doorPosition[0], doorPosition[1])
    OnPlayPositioned(peer, GetPlayer(peer).NetID, "audio/teleport.wav", 2000)

def OnClientJoinWorldRequested(peer, worldName: str):
    if GetPlayer(peer).CurrentWorld != '': return
    GetPlayer(peer).UpdateClothes = False
    st = time.time()
    if GetPlayer(peer).tankIDName == '': worldName = 'START'

    world = GetWorld(worldName)
    nameLen = len(worldName)
    worldPacket = bytearray(78 + nameLen + len(world.Tiles) + 24 + (8*len(world.Tiles) + (0 * 16)))
    worldPacket[0] = 4
    worldPacket[4] = 4
    worldPacket[16] = 8
    worldPacket[66] = nameLen
    worldPacket[68:68 + nameLen] = worldName.encode()
    worldPacket[68 + nameLen] = 100 #SizeX
    worldPacket[72 + nameLen] = 60 #SizeY
    struct.pack_into('<h', worldPacket, 76 + nameLen, world.TotalTiles) #Total Tiles
    extraDataPos = 85 + nameLen
    for i in range(0, len(world.Tiles)):
        struct.pack_into('<h', worldPacket, extraDataPos, world.Tiles[i].Fg) #FG
        struct.pack_into('<h', worldPacket, extraDataPos+2, world.Tiles[i].Bg) #BG
        struct.pack_into('<I', worldPacket, extraDataPos+4, world.Tiles[i].Flags) #FLAGS
        # if world.Tiles[i].Fg == 3548: print(ItemsData.Items[world.Tiles[i].Fg].ActionType)
        if ItemsData.Items[world.Tiles[i].Fg].ActionType == 13 or ItemsData.Items[world.Tiles[i].Fg].ActionType == 2: #Main Door
            worldPacket[extraDataPos + 8] = 1
            struct.pack_into('<h', worldPacket, extraDataPos + 9, len(world.Tiles[i].Label))
            worldPacket[extraDataPos + 11:extraDataPos + 11 + len(world.Tiles[i].Label)] = world.Tiles[i].Label.encode()
           
            extraDataPos += 4 + len(world.Tiles[i].Label)

            if ItemsData.Items[world.Tiles[i].Fg].ActionType == 13:
                GetPlayer(peer).PosX = (i % world.SizeX) * 32
                GetPlayer(peer).PosY = (i // world.SizeX) * 32
        
        if ItemsData.Items[world.Tiles[i].Fg].ActionType == 10: #Sign
            world.Tiles[i].Label = "ADNAN PENIPU HANDAL"
            worldPacket[extraDataPos + 8] = 2
            struct.pack_into('<h', worldPacket, extraDataPos + 9, len(world.Tiles[i].Label))
            worldPacket[extraDataPos + 11:extraDataPos + 11 + len(world.Tiles[i].Label)] = world.Tiles[i].Label.encode()
            extraDataPos += 7 + len(world.Tiles[i].Label)

        extraDataPos += 8
    et = time.time()
    OnConsoleMessage(peer, f"World loaded {int((et-st) * 1000)}ms")

    enetPacket = enet.Packet(data=worldPacket, flags=enet.PACKET_FLAG_RELIABLE)
    peer.send(0, enetPacket)

    OnConsoleMessage(peer, "`oWorld `w" + worldName + f" `oentered. There are `w{world.TotalPlayer} `oother people here, `w" + str(len(Peers)) + ' `oonline.')
    
    GetPlayer(peer).NetID = world.TotalPlayer + 1
    OnSpawn(peer, GetPlayer(peer).NetID, 1, GetPlayer(peer).PosX, GetPlayer(peer).PosY, GetPlayer(peer).GetDisplayName(), GetPlayer(peer).Country, False, True, True, True)
    SendPacket(peer, 3, "action|play_sfx\nfile|audio/door_open.wav\ndelayMS|0")
    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld and GetPlayer(currentPeer).CurrentWorld != "":
            OnConsoleMessage(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5entered, `w{world.TotalPlayer} `5others here>")
            OnTalkBubble(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5entered, `w{world.TotalPlayer} `5others here>", GetPlayer(peer).NetID, False)
            SendPacket(currentPeer, 3, "action|play_sfx\nfile|audio/door_open.wav\ndelayMS|0");
            if currentPeer != peer: #jika currentpeer bukan local (kita)
                OnSpawn(peer, GetPlayer(currentPeer).NetID, 1, GetPlayer(currentPeer).PosX, GetPlayer(currentPeer).PosY, GetPlayer(currentPeer).GetDisplayName(), 'us', False, True, True, False)
                OnTalkBubble(peer, f"{GetPlayer(currentPeer).GetDisplayName()}", GetPlayer(currentPeer).NetID, False)

    world.TotalPlayer += 1
    GetPlayer(peer).CurrentWorld = worldName
def OnPlayerMoving(peer, tank_packet: TankPacket):
    if GetPlayer(peer).CurrentWorld == '': return
    GetPlayer(peer).PosX = tank_packet.X
    GetPlayer(peer).PosY = tank_packet.Y

    if GetPlayer(peer).UpdateClothes == False:
        OnSetClothing(peer, GetPlayer(peer).NetID, GetPlayer(peer).Clothes.Hair, GetPlayer(peer).Clothes.Shirt, GetPlayer(peer).Clothes.Pants, GetPlayer(peer).Clothes.Feet, GetPlayer(peer).Clothes.Face, GetPlayer(peer).Clothes.Hand, GetPlayer(peer).Clothes.Back, GetPlayer(peer).Clothes.Mask, GetPlayer(peer).Clothes.Necklace, GetPlayer(peer).Clothes.Ances, GetPlayer(peer).Clothes.SkinColor)
        #Custom Pet
        GetPlayer(peer).PetCustom.petName = "Blue Gem Lock"
        GetPlayer(peer).PetCustom.set_pos_x_y(GetPlayer(peer).PosX + random.randint(0,32), GetPlayer(peer).PosY + random.randint(0,32))
        OnSpawn(peer, -2, -2, GetPlayer(peer).PetCustom.posX, GetPlayer(peer).PetCustom.posY, GetPlayer(peer).PetCustom.petName, "ttBadge", False, True, True, False)

        #Custom Pet
        
        GetPlayer(peer).UpdateClothes = True

    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld:
            tank_packet.NetID = GetPlayer(peer).NetID
            SendTankPacket(currentPeer, tank_packet)
            OnSetClothing(peer, -2, 0, 0, 0, 0, 0, 0, 7188, 0, 0, 0, 10)
            #Pet Lerp State
            pet_lerp = tank_packet
            tank_packet.NetID = -2 #Pet Netid
            SendTankPacket(currentPeer, tank_packet)


def OnClientExitWorld(peer):
    if GetPlayer(peer).CurrentWorld == '': return
    GetPlayer(peer).UpdateClothes = False
    world = GetWorld(GetPlayer(peer).CurrentWorld)
    world.TotalPlayer -= 1
    if world.TotalPlayer <= 0:
        world.TotalPlayer = 0
        world.save_world()
        del worlds.Worlds[GetPlayer(peer).CurrentWorld]
    
    SendPacket(peer, 3, "action|play_sfx\nfile|audio/door_shut.wav\ndelayMS|0")
    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld and currentPeer != peer:
            OnRemove(currentPeer, GetPlayer(peer).NetID)
            OnConsoleMessage(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5left, `w{world.TotalPlayer} `5others here>")
            SendPacket(currentPeer, 3, "action|play_sfx\nfile|audio/door_shut.wav\ndelayMS|0")

    SendWorldOffer(peer)
    GetPlayer(peer).CurrentWorld = ''
def OnPlayerLogin(peer, username: str, password: str, requestedName: str):
    if username == '' and password == '':
        GetPlayer(peer).requestedName = requestedName
        GetPlayer(peer).requestedGuestID = random.randint(0, 255)
        OnSuperMain(peer)
    else:
        player = load_player(username)
        if player == None: #User Not Found
            LogonFail(peer, "`4Unable to log on: `oThat `wGrowID`` doesn't seem valid, or the password is wrong. If you don't have one, press `wCancel``, un-check `w'I have a GrowID'``, then click `wConnect``.", "Retrieve lost password", "https://discord.gg/nusaverse")
        else:
            if password.lower() != player.tankIDPass.lower(): #Failed Authenticated
                LogonFail(peer, "`4Unable to log on: `oThat `wGrowID`` doesn't seem valid, or the password is wrong. If you don't have one, press `wCancel``, un-check `w'I have a GrowID'``, then click `wConnect``.", "Retrieve lost password", "https://discord.gg/nusaverse")
            else:
                Peers[peer] = player
                OnSuperMain(peer)

def OnPlayerPunch(peer, punchX, punchY, Value):
    if GetPlayer(peer).CurrentWorld == '': return
    world = GetWorld(GetPlayer(peer).CurrentWorld)
    tiles = world.Tiles[punchX + (punchY * world.SizeX)]
    if Value == 18:
        send_tank = TankPacket()
        send_tank.PunchX = punchX
        send_tank.PunchY = punchY
        send_tank.CharacterState = 0
        send_tank.NetID = GetPlayer(peer).NetID

        breakID = tiles.Fg or tiles.Bg
        if not breakID: return

        currentTime = int(time.time() * 1000)
        
        send_tank.PacketType = 8
        send_tank.Value = 6
        if currentTime - tiles.HitTime >= 8000:
            tiles.HitTime = currentTime
            tiles.HitTotal = 0
        else:
            tiles.HitTime = currentTime
            tiles.HitTotal += 1

        if tiles.HitTotal >= int(ItemsData.Items[breakID].BreakHits // 6):
            if tiles.Fg != 0: tiles.Fg = 0
            elif tiles.Bg != 0: tiles.Bg = 0

            tiles.HitTime = 0
            tiles.HitTotal = 0

            send_tank.PacketType = 3
            send_tank.Value = 18
        SendTankPacket(peer, send_tank)

    elif Value == 32:
        if ItemsData.Items[tiles.Fg].ActionType == 2: #Door
            OnDialogRequest(peer, f"add_label_with_icon|big|`wEdit {ItemsData.Items[tiles.Fg].Name}|left|{tiles.Fg}|\nembed_data|door_x|{punchX}\nembed_data|door_y|{punchY}\nadd_text_input|door_label|Label|{tiles.Label}|50|\nadd_text_input|door_destination|Destination||18|\nadd_smalltext|Enter a Destination in this format: `2WORLDNAME:ID|left|\nadd_smalltext|Leave `2WORLDNAME `oblank (:ID) to go to the door with `2ID `oin the `2Current World`o.|left|\nadd_text_input|door_id|ID||18|\nadd_smalltext|Set a unique `2ID `oto target this door as a Destination from another|left|\nend_dialog|door_apply|Cancel|OK|")

    else:
        send_tank = TankPacket()
        send_tank.PunchX = punchX
        send_tank.PunchY = punchY
        send_tank.PacketType = 3
        send_tank.Value = Value
        send_tank.CharacterState = 0
        send_tank.NetID = GetPlayer(peer).NetID
        tiles.Fg = Value
        SendTankPacket(peer, send_tank)
        
def register_dialog(peer, title = '', username = '', password= '', password_verify = '', gmail = ''):
    dialog = "text_scaling_string|Dirttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt|\n" + "set_default_color|`o\n" + "add_label_with_icon|big|`wGet a GrowID``|left|206|\n"
    if title != "":
        dialog += f"add_textbox|{title}|left|\n"
    dialog += f"add_spacer|small|\n" + f"add_text_input|logon|Name|{username}|18|\n"
    dialog += f"add_textbox|Your `wpassword`` must contain `w8 to 18 characters, 1 letter, 1 number`` and `w1 special character: @#!$^&*.,``|left|\n" + f"add_text_input_password|password|Password|{password}|18|\n" + f"add_text_input_password|password_verify|Password Verify|{password_verify}|18|\n" + f"add_textbox|Your `wemail`` will only be used for account verification and support. If you enter a fake email, you can't verify your account, recover or change your password.|left|\n" + f"add_text_input|email|Email|{gmail}|64|\n" + f"add_textbox|We will never ask you for your password or email, never share it with anyone!|left|\nend_dialog|growid_apply|Cancel|Get My GrowID!|\n"
    OnDialogRequest(peer, dialog, 1000)