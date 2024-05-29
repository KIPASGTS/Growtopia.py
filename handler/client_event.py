import enet
import struct
import random
import time

from players.player import *
from globals import *
from worlds.world import GetWorld
from variants.packet import *
from handler.packet import *

def OnClientJoinWorldRequested(peer, worldName: str):
    st = time.time()
    if GetPlayer(peer).tankIDName == '':
        OnTextOverlay(peer, "Sorry, But you need to create an `4Account")
        worldName = 'START'

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

        if ItemsData.Items[world.Tiles[i].Fg].ActionType == 13 or ItemsData.Items[world.Tiles[i].Fg].ActionType == 3: #Main Door
            worldPacket[extraDataPos + 8] = 1
            struct.pack_into('<h', worldPacket, extraDataPos + 9, len(world.Tiles[i].Label))
            worldPacket[extraDataPos + 11:extraDataPos + 11 + len(world.Tiles[i].Label)] = world.Tiles[i].Label.encode()
            extraDataPos += 4 + len(world.Tiles[i].Label)
            GetPlayer(peer).PosX = (i % world.SizeX) * 32
            GetPlayer(peer).PosY = (i // world.SizeX) * 32

        extraDataPos += 8
    et = time.time()
    OnConsoleMessage(peer, f"Word loaded {int((et-st) * 1000)}ms")
    enetPacket = enet.Packet(data=worldPacket, flags=enet.PACKET_FLAG_RELIABLE)
    peer.send(0, enetPacket)
    OnConsoleMessage(peer, "`oWorld `w" + worldName + f" `oentered. There are `w{world.TotalPlayer} `oother people here, `w" + str(len(Peers)) + ' `oonline.')
    
    #buble join world
    GetPlayer(peer).NetID = world.TotalPlayer + 1
    world.TotalPlayer += 1
    
    OnSpawn(peer, GetPlayer(peer).NetID, 1, GetPlayer(peer).PosX, GetPlayer(peer).PosY, GetPlayer(peer).GetDisplayName(), 'ttBadge', False, True, True, True)
    
    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld:
            OnConsoleMessage(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5entered, `w{world.TotalPlayer} `5others here>")
            OnTalkBubble(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5entered, `w{world.TotalPlayer} `5others here>", GetPlayer(peer).NetID, False)
            
            if currentPeer != peer: #jika currentpeer bukan local (kita)
                OnSpawn(peer, GetPlayer(currentPeer).NetID, 1, GetPlayer(currentPeer).PosX, GetPlayer(currentPeer).PosY, GetPlayer(currentPeer).GetDisplayName(), 'ttBadge', False, True, True, False)
                OnTalkBubble(peer, f"{GetPlayer(currentPeer).GetDisplayName()}", GetPlayer(currentPeer).NetID, False)

                

    
    GetPlayer(peer).CurrentWorld = worldName

def OnPlayerMoving(peer, tank_packet: TankPacket):
    if GetPlayer(peer).CurrentWorld == '':
        return
    
    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld:
            tank_packet.NetID = GetPlayer(peer).NetID
            SendTankPacket(currentPeer, tank_packet)

def OnClientExitWorld(peer):
    if GetPlayer(peer).CurrentWorld == '':
        return
    world = GetWorld(GetPlayer(peer).CurrentWorld)
    world.TotalPlayer -= 1
    if world.TotalPlayer <= 0:
        world.TotalPlayer = 0
        world.save_world()
        del worlds.Worlds[GetPlayer(peer).CurrentWorld]

    for currentPeer in Peers:
        if GetPlayer(currentPeer).CurrentWorld == GetPlayer(peer).CurrentWorld:
            OnRemove(currentPeer, GetPlayer(peer).NetID)
            OnConsoleMessage(currentPeer, f"`5<`w{GetPlayer(peer).GetDisplayName()} `5left, `w{world.TotalPlayer} `5others here>")

    SendWorldOffer(peer)
    GetPlayer(peer).CurrentWorld = ''


def OnPlayerLogin(peer, username: str, password: str, requestedName: str):
    print(f"New Client Login: {username},{password},{requestedName}")
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

    if Value == 18:
        tiles = world.Tiles[punchX + (punchY * world.SizeX)]
        if tiles.Fg == 0 and tiles.Bg != 0: tiles.Bg = 0
        elif tiles.Fg != 0: tiles.Fg = 0


def register_dialog(peer, title = '', username = '', password= '', password_verify = '', gmail = ''):
    dialog = "text_scaling_string|Dirttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt|\n" + "set_default_color|`o\n" + "add_label_with_icon|big|`wGet a GrowID``|left|206|\n"
    if title != "":
        dialog += f"add_textbox|{title}|left|\n"
    dialog += f"add_spacer|small|\n" + f"add_text_input|logon|Name|{username}|18|\n"
    dialog += f"add_textbox|Your `wpassword`` must contain `w8 to 18 characters, 1 letter, 1 number`` and `w1 special character: @#!$^&*.,``|left|\n" + f"add_text_input_password|password|Password|{password}|18|\n" + f"add_text_input_password|password_verify|Password Verify|{password_verify}|18|\n" + f"add_textbox|Your `wemail`` will only be used for account verification and support. If you enter a fake email, you can't verify your account, recover or change your password.|left|\n" + f"add_text_input|email|Email|{gmail}|64|\n" + f"add_textbox|We will never ask you for your password or email, never share it with anyone!|left|\n" + "end_dialog|growid_apply|Cancel|Get My GrowID!|\n"
    OnDialogRequest(peer, dialog, 1000)