import enet
import handler.packet as Packet
import re

from handler.client_event import *
from handler.variants import Variants
from variants.packet import *
from globals import *
from players.player import *


def OnConnected(peer, address, host):
    if peer in Peers:
        OnConsoleMessage(peer, 'Invalid Peer')
        peer.disconnect_later(0)
    else:
        Peers[peer] = Player()
        print(f"[SERVER] New Client Connected: {address}")
        Packet.SendPacket(peer, 1, "")

def OnDisconnected(peer, address, host):
    if peer in Peers:
        if GetPlayer(peer).tankIDName != '' and GetPlayer(peer).tankIDPass != '': save_player(GetPlayer(peer))
        print(f"[SERVER] Client Disonnected: {address}")
        del Peers[peer]
    else:
        print('[SERVER] Invalid peer to delete')

def OnReceived(peer, address, host, packet):
    netMessage = Packet.GetNetMessageTypeFromPacket(packet.data)
    if netMessage == 2 or netMessage == 3:
        msg = Packet.GetTextMessageFromPacket(packet.data)
        print(f"[SERVER][{netMessage}]: " + msg)
        if msg == "action|quit" or msg == "action|quit\n":
            peer.disconnect_later(0)
            return
        elif 'requestedName|' in msg:
            requestedName = re.findall(r'requestedName\|(.*?)\n', msg)[0]
            tankIDName = ''
            tankIDPass = ''
            if 'tankIDName|' in msg and 'tankIDPass|' in msg:
                tankIDName = re.findall(r'tankIDName\|(.*?)\n', msg)[0]
                tankIDPass = re.findall(r'tankIDPass\|(.*?)\n', msg)[0]
            GetPlayer(peer).Country = re.findall(r'country\|(.*?)\n', msg)[0]
            Packet.SendPacket(peer, 3, "action|log\nmsg|`oWelcome to `2GrowPython3")
            OnPlayerLogin(peer, tankIDName, tankIDPass, requestedName)
            return
        
        elif 'action|join_request\nname|' in msg:
            worldName = re.findall(r'name\|(.*?)\n', msg)[0].upper()
            Packet.SendPacket(peer, 3, "action|log\nmsg|>> Sending you to " + str(worldName))
            OnClientJoinWorldRequested(peer, worldName)
            return
        elif msg == 'action|enter_game\n':
            if GetPlayer(peer).tankIDName == '' and GetPlayer(peer).tankIDPass == '':
                UpdatePlayerInventoryWhenLogin(peer)
                OnClientJoinWorldRequested(peer, 'START')
                return
            
            UpdatePlayerInventoryWhenLogin(peer)
            SendWorldOffer(peer)
            return

        elif msg == "action|quit_to_exit\n" or msg == "action|quit_to_exit":
            OnClientExitWorld(peer)
            return
        elif msg == "action|growid\n":
            register_dialog(peer)
            return
        elif msg == 'action|refresh_item_data\n':
            Packet.SendPacket(peer, 3, "action|log\nmsg|One moment, updating item data...")
            enetPacket = enet.Packet(data=ItemsData.BufferForUpdatingItems, flags=enet.PACKET_FLAG_RELIABLE)
            peer.send(0, enetPacket)
            return
        elif 'action|input\n|text|' in msg:
            text = msg[19:]
            if text[0] == '/':
                Packet.SendPacket(peer, 3, "action|log\nmsg|`6" + text)
                if text == "/info":
                    player = GetPlayer(peer) if not None else None
                    OnConsoleMessage(peer, str(player.__dict__))
                elif text.startswith("/find"):
                    if text == "/find":
                        OnConsoleMessage(peer, ">> usage: /find <`$item_name`o>")
                        return
                    try:
                        findStr = text.split("/find ")[1]
                        OnDialogRequest(peer, "add_label_with_icon|big|`wFind item``|left|6016|\nadd_textbox|Enter a word below to find the item|\nadd_text_input|nusaverse_find_item_name|Item Name|"+findStr+"|30|\nend_dialog|nusaverse_dev_find|Cancel|Find the item!|\nadd_quick_exit|\n")
                    except Exception as e:
                        OnConsoleMessage(peer, f"Error: {e}")

                elif text.startswith('/help'):
                    Packet.SendPacket(peer, 3, "action|log\nmsg|Help Command: /find <`$item_name`o> /info /give <`$item_id`o> <`$amount`o>")
                
                elif text.startswith('/give'):
                    args = text.split(' ')
                    amount = 200; itemid = 0
                    if len(args) == 2:
                        if not args[1].isdigit(): return OnConsoleMessage(peer, ">> usage : /give <`$item_id`o> <`$amount`o>")
                        itemid = int(args[1])
                    elif len(args) == 3:
                        if not args[1].isdigit() or not args[2].isdigit(): return OnConsoleMessage(peer, ">> usage : /give <`$item_id`o> <`$amount`o>")
                        itemid = int(args[1])
                        amount = int(args[2])
                    else:
                        return OnConsoleMessage(peer, ">> usage: /give <`$item_id`o> <`$amount`o>")

                    if itemid < 0 or itemid > len(ItemsData.Items): return OnConsoleMessage(peer, ">> Error.")
                    if amount < 1 or amount > 200: return OnConsoleMessage(peer, ">> Max amount range above 1 and 200")

                    GetPlayer(peer).Inventory.append(PlayerInventory(itemid, amount))
                    UpdatePlayerInventoryWhenLogin(peer)
                    OnConsoleMessage(peer, f'Added `w{amount} {ItemsData.GetItems(itemid).Name} `oto your inventory')
                else:
                    Packet.SendPacket(peer, 3, "action|log\nmsg|`4Unknown command.``  Enter `$/?`` for a list of valid commands.")
            else:
                if (text.strip() == '' or text == 'player_chat=' or
                    (text.startswith('`') and len(text) == 2) or text == '`'):
                    return

                OnConsoleMessage(peer, f'CP:_PL:0_OID:_CT:[W]_ `6<`w{GetPlayer(peer).GetDisplayName()}`6> `$' + text)
                OnTalkBubble(peer, "CP:_PL:0_OID:_player_chat=" + text, 1, False)
        elif msg.startswith('action|dialog_return\ndialog_name|nusaverse_dev_find\nbuttonClicked|get_item_find/'):
            try:
                itemid = int(re.findall(r'buttonClicked\|get_item_find/(.*?)\n', msg)[0])
                
                OnConsoleMessage(peer, "`oAdded `w200 " + ItemsData.Items[itemid].Name + " `oto inventory!")
                GetPlayer(peer).Inventory.append(PlayerInventory(itemid, 200))
                UpdatePlayerInventoryWhenLogin(peer)
            except Exception as e:
                OnConsoleMessage(peer, f"Error: {e}")
        elif msg.startswith('action|dialog_return\ndialog_name|nusaverse_dev_find\nnusaverse_find_item_name|'):
            text = re.findall(r'nusaverse_find_item_name\|(.*?)\n', msg)[0]
            founded_item = ""
            total_found = 0
            for i in range(0, len(ItemsData.Items)):
                if i % 2 != 0: continue #Seed
                if text.lower() in ItemsData.Items[i].Name.lower():
                    total_found += 1
                    founded_item += "add_button_with_icon|get_item_find/" + str(ItemsData.Items[i].ItemID) + "|" + ItemsData.Items[i].Name + "|staticBlueFrame|" + str(ItemsData.Items[i].ItemID) + "|" + str(ItemsData.Items[i].ItemID) + "|\n"

            if total_found != 0: OnDialogRequest(peer, "text_scaling_string|Dirtttttttttttttttttttttttttttttttttttt|\nadd_label_with_icon|big|`wFound Item: "+ str(total_found) +"``|left|6016|\n"+founded_item+"\nend_dialog|nusaverse_dev_find|||\nadd_quick_exit|\n")
            else: OnDialogRequest(peer, "add_label_with_icon|big|`wFound Item: 0``|left|6016|\nadd_textbox|`4No item match with that name!``|\nadd_textbox|Enter a word below to find the item|\nadd_text_input|nusaverse_find_item_name|Item Name||30|\nend_dialog|nusaverse_dev_find|Cancel|Find the item!|\nadd_quick_exit|\n")        
        elif msg.startswith('action|dialog_return\ndialog_name|growid_apply'):
            if 'logon|' in msg and 'password|' in msg and  'password_verify|' in msg and 'email|' in msg:
                logon = re.findall(r'logon\|(.*?)\n', msg)[0]
                password = re.findall(r'password\|(.*?)\n', msg)[0]
                password_verify = re.findall(r'password_verify\|(.*?)\n', msg)[0]
                email = re.findall(r'email\|(.*?)\n', msg)[0]

                pattern = re.compile(r'^[a-zA-Z0-9]+$')
                if bool(pattern.match(logon)) == False: register_dialog(peer, "`4Oops!`` You can only use letters and numbers in your GrowID.", logon, password, password_verify, email)
                elif len(logon) < 3 or len(logon) > 18: register_dialog(peer, "`4Oops!``  Your `wGrowID`` must be between `$3`` and `$18`` characters long.", logon, password, password_verify, email)
                elif len(password) < 4 or len(password) > 8: register_dialog(peer, "`4Oops!``  Your password must be between `$4`` and `$18`` characters long.", logon, password, password_verify, email)
                elif password != password_verify: register_dialog(peer, "`4Oops!`` Passwords don't match.  Try again.", logon, password, password_verify, email)
                elif '@gmail.com' not in email: register_dialog(peer, "`4Oops!`` Our Server only accept Google Mail.", logon, password, password_verify, email)
                else:
                    if register_player(GetPlayer(peer), username=logon, password=password):
                        OnTextOverlay(peer, "Account Succesfully `2Created `wnow you disconnected!")
                        peer.disconnect_later(0)
                    else: OnTextOverlay(peer, "`4Failed to create account")
            else: peer.disconnect_later(0)
        elif msg.startswith('action|setSkin\ncolor|'):
            skin_color = msg[21:].replace('\n', '')
            if skin_color.isdigit():
                skin_color = int(skin_color)
                GetPlayer(peer).Clothes.SkinColor = skin_color
                OnSetClothing(peer, GetPlayer(peer).NetID, GetPlayer(peer).Clothes.Hair, GetPlayer(peer).Clothes.Shirt, GetPlayer(peer).Clothes.Pants, GetPlayer(peer).Clothes.Feet, GetPlayer(peer).Clothes.Face, GetPlayer(peer).Clothes.Hand, GetPlayer(peer).Clothes.Back, GetPlayer(peer).Clothes.Mask, GetPlayer(peer).Clothes.Necklace, GetPlayer(peer).Clothes.Ances, GetPlayer(peer).Clothes.SkinColor)
        elif msg.startswith('action|respawn\n') or msg.startswith('action|respawn_spike\n'):
            causeSpike = 'respawn_spike' in msg
            OnPlayerRespawn(peer, causeSpike)
        elif msg.startswith('action|dialog_return\ndialog_name|door_apply\n'):
            if 'door_label|' in msg and 'door_destination|' in msg and 'door_id' in msg:
                try:
                    door_label = re.findall(r'door_label\|(.*?)\n', msg)[0]
                    door_destination = re.findall(r'door_destination\|(.*?)\n', msg)[0]
                    door_id = re.findall(r'door_id\|(.*?)\n', msg)[0]
                    door_x = int(re.findall(r'door_x\|(.*?)\|\n', msg)[0])
                    door_y = int(re.findall(r'door_y\|(.*?)\|\n', msg)[0])


                    world = GetWorld(GetPlayer(peer).CurrentWorld)
                    if ItemsData.Items[world.Tiles[door_x + (door_y * world.SizeX)].Fg].ActionType == 2: #Door
                        world.Tiles[door_x + (door_y * world.SizeX)].Label = door_label

                except Exception as e:
                    OnConsoleMessage(peer, f"Error: {e}")

    elif netMessage == 4:
        tank = Packet.GetTankPacketFromPacket(packet.data[4:])
        if tank.PacketType == 7:
            if GetPlayer(peer).CurrentWorld == '': return
            world = GetWorld(GetPlayer(peer).CurrentWorld)
            tile = world.Tiles[tank.PunchX + (tank.PunchY * world.SizeX)]
            if ItemsData.Items[tile.Fg].ActionType == 13 or ItemsData.Items[tile.Fg].ActionType == 3:
                OnClientExitWorld(peer)

        elif tank.PacketType == 3:
            OnPlayerPunch(peer, tank.PunchX, tank.PunchY, tank.Value)

        elif tank.PacketType == 0:
            OnPlayerMoving(peer, tank)
        elif tank.PacketType == 24:
            pass
        else:
            pass
    else:
        pass