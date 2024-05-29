import struct
import enet

from globals import GetPlayer, Peers
from handler.packet import SendPacket
from handler.variants import Variants
from worlds.world import worlds

def OnSuperMain(peer):
    variants = Variants()
    variants.InsertString("OnSuperMainStartAcceptLogonHrdxs47254722215a")
    variants.InsertUint(285833052) #Items.dat hash
    variants.InsertString("ubistatic-a.akamaihd.net")
    variants.InsertString("0098/95685695/cache/")
    variants.InsertString("cc.cz.madkite.freedom org.aqua.gg idv.aqua.bulldog com.cih.gamecih2 com.cih.gamecih com.cih.game_cih cn.maocai.gamekiller com.gmd.speedtime org.dax.attack com.x0.strai.frep com.x0.strai.free org.cheatengine.cegui org.sbtools.gamehack com.skgames.traffikrider org.sbtoods.gamehaca com.skype.ralder org.cheatengine.cegui.xx.multi1458919170111 com.prohiro.macro me.autotouch.autotouch com.cygery.repetitouch.free com.cygery.repetitouch.pro com.proziro.zacro com.slash.gamebuster")
    variants.InsertString("proto=206|choosemusic=audio/mp3/nusaverse_lobby.mp3|active_holiday=19|wing_week_day=0|ubi_week_day=2|server_tick=123665344|clash_active=0|drop_lavacheck_faster=1|isPayingUser=2|usingStoreNavigation=1|enableInventoryTab=1|bigBackpack=1|m_clientBits=0")
    variants.Send(peer)

def OnConsoleMessage(peer, msg):
    variants = Variants()
    variants.InsertString("OnConsoleMessage")
    variants.InsertString(msg)
    variants.Send(peer)

def OnRemove(peer, netid):
    variants = Variants()
    variants.InsertString("OnRemove")
    variants.InsertString(f"netID|{netid}\n")
    variants.Send(peer)

def OnSetPos(peer, netids, x, y):
    variants = Variants(NetID=netids)
    variants.InsertString("OnSetPos")
    variants.InsertVector2F(x, y)
    variants.Send(peer)

def OnDialogRequest(peer, msg, delay = 0):
    variants = Variants(delay=delay)
    variants.InsertString("OnDialogRequest")
    variants.InsertString(msg)
    variants.Send(peer)

def OnTextOverlay(peer, msg, delay = 0):
    variants = Variants(delay=delay)
    variants.InsertString("OnTextOverlay")
    variants.InsertString(msg)
    variants.Send(peer)

def OnTalkBubble(peer, msg, netid, overlay = False):
    variants = Variants()
    variants.InsertString("OnTalkBubble")
    variants.InsertInt(netid)
    variants.InsertString(msg)
    variants.InsertInt(overlay)
    variants.InsertInt(overlay)
    variants.Send(peer)

def SendWorldOffer(peer):
    OnConsoleMessage(peer, f"`oWhere would you like to go? (`w{len(Peers)} `oonline)")
    world_packet = "add_filter|\n"
    world_packet += "add_heading|Active World<ROW2>|\n"
    for world in worlds.Worlds:
        world_packet += "add_floater|" + world + "|" + world + "|" + str(worlds.Worlds[world].TotalPlayer) + "|0.5|3529161471\n"
    world_packet += "add_heading|Credits<CR>|\n"
    world_packet += "add_floater|KIPASGTS|KIPASGTS|0|0.5|2147418367\n"
    world_packet += "add_floater|ADNAN|ADNAN|0|0.5|2147418367\n"
    world_packet += "add_floater|AKBAR|AKBAR|0|0.5|2147418367\n"
    world_packet += "add_floater|NEVOLUTION|NEVOLUTION|0|0.5|2147418367\n"
    world_packet += "add_floater|PYENET|PYENET|0|0.5|2147418367\n"
    variants = Variants()
    variants.InsertString("OnRequestWorldSelectMenu")
    variants.InsertString(world_packet)
    variants.Send(peer)

def OnSpawn(peer, netid, userid, posX, posY, username, country, invis, mstate, smsate, local):
    spawn_avatar = "spawn|avatar\n"
    spawn_avatar += f"netID|{netid}\n"
    spawn_avatar += f"userID|{userid}\n"
    spawn_avatar += "colrect|0|0|20|30\n"
    spawn_avatar += f"posXY|{posX}|{posY}\n"
    spawn_avatar += f"name|{username}\n"
    spawn_avatar += f"country|{country}\n"
    spawn_avatar += f"invis|{str(int(invis))}\n"    # 1 0
    spawn_avatar += f"mstate|{str(int(mstate))}\n"  # 1 0
    spawn_avatar += f"smstate|{str(int(smsate))}\n" # 1 0
    if local:
        spawn_avatar += "onlineID|\ntype|local\n"
    
    variants = Variants()
    variants.InsertString("OnSpawn")
    variants.InsertString(spawn_avatar)
    variants.Send(peer)

def LogonFail(peer, message, textButton, urlButton):
    SendPacket(peer, 3, "action|log\nmsg|"+message)
    if len(textButton) > 0:
        SendPacket(peer, 3, "action|set_url\nurl|"+urlButton+"\nlabel|"+textButton+"\n")
    SendPacket(peer, 3, "action|logon_fail")
    peer.disconnect_later(0)

def UpdatePlayerInventoryWhenLogin(peer):
    buffer = bytearray(66 + (GetPlayer(peer).InventoryAmount * 4) + 4)
    struct.pack_into('<I', buffer, 0, 4)
    struct.pack_into('<I', buffer, 4, 9)
    struct.pack_into('<i', buffer, 8, -1)
    struct.pack_into('<I', buffer, 16, 8)
    struct.pack_into('<I', buffer, 56, 6 + (GetPlayer(peer).InventoryAmount * 4) + 4)
    struct.pack_into('<I', buffer, 60, 1)
    struct.pack_into('<I', buffer, 61, GetPlayer(peer).InventoryAmount)
    struct.pack_into('<I', buffer, 65, GetPlayer(peer).InventoryAmount)
    memPos = 67
    for i in GetPlayer(peer).Inventory:
        struct.pack_into('<I', buffer, memPos, i.ItemID); memPos += 2
        buffer[memPos] = i.Amount; memPos += 2

    enetPacket = enet.Packet(data=buffer, flags=1)
    peer.send(0, enetPacket)
