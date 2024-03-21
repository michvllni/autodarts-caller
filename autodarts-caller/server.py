from websocket_server import WebsocketServer
import logging
import json
import threading
import queue
import os
import base64
import time
from urllib.parse import quote
import websocket
import requests
import math

from globals import AUTODART_WEBSOCKET_URL, AUTODART_MATCHES_URL
from caller_configuration import CallerConfiguration
from match_helpers import listen_to_match, correct_throw, next_game, next_throw, undo_throw, setup_caller
from utils import ppe,ppi
from process.process_atc import process_match_atc
from process.process_cricket import process_match_cricket
from process.process_rtw import process_match_rtw
from process.process_x01 import process_match_x01
from process.process_common import process_common
from process.process_bulling import process_bulling
from sound import play_sound_effect, mirror_sounds, check_sounds
from player import get_player_average
from board import Board
from caller import caller, caller_title_without_version, ban_caller
from defaults import DEFAULT_CALLER, DEFAULT_EMPTY_PATH

class CallerServer:
    server: WebsocketServer
    config: CallerConfiguration
    ws: websocket.WebSocketApp
    board: Board
    websocket_server_thread: threading.Thread

    def connect_autodarts(self):
        def process(*args):
            websocket.enableTrace(False)
            ws = websocket.WebSocketApp(AUTODART_WEBSOCKET_URL,
                                        header={'Authorization': 'Bearer ' + self.config.access_token},
                                        on_open = self.__on_open_autodarts,
                                        on_message = self.__on_message_autodarts,
                                        on_error = self.__on_error_autodarts,
                                        on_close = self.__on_close_autodarts)
            

            ws.run_forever()
        threading.Thread(target=process).start()

    def __on_open_autodarts(self,ws):
        try:
            res = requests.get(AUTODART_MATCHES_URL, headers={'Authorization': 'Bearer ' + self.config.access_token})
            res = res.json()
            # ppi(json.dumps(res, indent = 4, sort_keys = True))

            # watchout for a match with my board-id
            should_break = False
            for m in res:
                for p in m['players']:
                    if 'boardId' in p and p['boardId'] == self.config.AUTODART_USER_BOARD_ID:
                        mes = {
                            "event": "start",
                            "id": m['id']
                        }
                        listen_to_match(mes, ws)
                        should_break = True
                        break
                if should_break:
                    break
                
        except Exception as e:
            ppe('Fetching matches failed', e)

        
        try:
            # EXAMPLE:
            # const unsub = MessageBroker.getInstance().subscribe<{ id: string; event: 'start' | 'finish' | 'delete' }>(
            # 'autodarts.boards',
            # id + '.matches',

            # (msg) => {
            #     if (msg.event === 'start') {
            #     setMatchId(msg.id);
            #     } else {
            #     setMatchId(undefined);
            #     }
            # }
            # );
            paramsSubscribeMatchesEvents = {
                "channel": "autodarts.boards",
                "type": "subscribe",
                "topic": self.config.AUTODART_USER_BOARD_ID + ".matches"
            }
            ws.send(json.dumps(paramsSubscribeMatchesEvents))

            ppi('Receiving live information for board-id: ' + self.config.AUTODART_USER_BOARD_ID)
            # poll_lobbies(ws)

        except Exception as e:
            ppe('WS-Open-boards failed: ', e)


        try:
            paramsSubscribeUserEvents = {
                "channel": "autodarts.users",
                "type": "subscribe",
                "topic": self.config.keyCloakClient.user_id + ".events"
            }
            ws.send(json.dumps(paramsSubscribeUserEvents))

            # ppi('Receiving live information for user-id: ' + kc.user_id)

        except Exception as e:
            ppe('WS-Open-users failed: ', e)
            
    def __on_message_autodarts(self, ws, message):
        def process(*args):
            try:
                global lastMessage
                global lobbyPlayers
                m = json.loads(message)
                # ppi(json.dumps(m, indent = 4, sort_keys = True))

                if m['channel'] == 'autodarts.matches':
                    data = m['data']
                    # ppi(json.dumps(data, indent = 4, sort_keys = True))

                    global currentMatch
                    # ppi('Current Match: ' + currentMatch)
                    
                    if('turns' in data and len(data['turns']) >=1):
                        data['turns'][0].pop("id", None)
                        data['turns'][0].pop("createdAt", None)

                    if lastMessage != data and currentMatch != None and 'id' in data and data['id'] == currentMatch:
                        lastMessage = data

                        # ppi(json.dumps(data, indent = 4, sort_keys = True))

                        process_common(data)

                        variant = data['variant']
                        
                        if variant == 'Bull-off':
                            process_bulling(data)

                        elif variant == 'X01' or variant == 'Random Checkout':
                            process_match_x01(data)
                            
                        elif variant == 'Cricket':
                            process_match_cricket(data)
                        
                        elif variant == 'ATC':
                            process_match_atc(data)

                        elif variant == 'RTW':
                            process_match_rtw(data)

                elif m['channel'] == 'autodarts.boards':
                    data = m['data']
                    # ppi(json.dumps(data, indent = 4, sort_keys = True))

                    listen_to_match(data, ws)
                
                elif m['channel'] == 'autodarts.users':
                    data = m['data']
                    # ppi(json.dumps(data, indent = 4, sort_keys = True))
                    if 'event' in data:
                        if data['event'] == 'lobby-enter':
                            # ppi("lobby-enter", data)

                            lobby_id = data['body']['id']

                            ppi('Listen to lobby: ' + lobby_id)
                            paramsSubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "subscribe",
                                    "topic": lobby_id + ".state"
                                }
                            ws.send(json.dumps(paramsSubscribeLobbyEvents))
                            paramsSubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "subscribe",
                                    "topic": lobby_id + ".events"
                                }
                            ws.send(json.dumps(paramsSubscribeLobbyEvents))
                            lobbyPlayers = []

                            if play_sound_effect("lobby_ambient_in", False, mod = False):
                                mirror_sounds()

                        elif data['event'] == 'lobby-leave':
                            # ppi("lobby-leave", data)

                            lobby_id = data['body']['id']

                            ppi('Stop Listen to lobby: ' + lobby_id)
                            paramsUnsubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "unsubscribe",
                                    "topic": lobby_id + ".state"
                                }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            paramsUnsubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "unsubscribe",
                                    "topic": lobby_id + ".events"
                                }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            lobbyPlayers = []

                            if play_sound_effect("lobby_ambient_out", False, mod = False):
                                mirror_sounds()

                elif m['channel'] == 'autodarts.lobbies':
                    data = m['data']
                    # ppi(json.dumps(data, indent = 4, sort_keys = True))
                    
                    if 'event' in data:
                        if data['event'] == 'start':
                            pass

                        elif data['event'] == 'finish' or data['event'] == 'delete':
                            ppi('Stop listening to lobby: ' + m['id'])
                            paramsUnsubscribeLobbyEvents = {
                                "type": "unsubscribe",
                                "channel": "autodarts.lobbies",
                                "topic": m['id'] + ".events"
                            }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            paramsUnsubscribeLobbyEvents = {
                                "type": "unsubscribe",
                                "channel": "autodarts.lobbies",
                                "topic": m['id'] + ".state"
                            }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            if play_sound_effect("lobby_ambient_out", False, mod = False):
                                mirror_sounds()
      
                            # poll_lobbies(ws)


                    elif 'players' in data:
                        # did I left the lobby?
                        me = False
                        for p in data['players']:
                            if 'boardId' in p and p['boardId'] == self.config.AUTODART_USER_BOARD_ID:
                                me = True
                                break
                        if me == False:
                            lobby_id = data['id']

                            ppi('Stop Listen to lobby: ' + lobby_id)
                            paramsUnsubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "unsubscribe",
                                    "topic": lobby_id + ".state"
                                }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            paramsUnsubscribeLobbyEvents = {
                                    "channel": "autodarts.lobbies",
                                    "type": "unsubscribe",
                                    "topic": lobby_id + ".events"
                                }
                            ws.send(json.dumps(paramsUnsubscribeLobbyEvents))
                            if play_sound_effect("lobby_ambient_out", False, mod = False):
                                mirror_sounds()
                            lobbyPlayers = []
                            return
                            

                        # check for left players
                        lobbyPlayersLeft = []
                        for lp in lobbyPlayers:
                            player_found = False
                            for p in data['players']:
                                if p['userId'] == lp['userId']:
                                    player_found = True
                                    break
                            if player_found == False:
                                lobbyPlayersLeft.append(lp)

                        for lpl in lobbyPlayersLeft:
                            lobbyPlayers.remove(lpl)
                            player_name = str(lpl['name']).lower()
                            ppi(player_name + " left the lobby")

                            play_sound_effect('lobby_ambient_out', False, mod = False)

                            if check_sounds([player_name, 'left']):
                                play_sound_effect(player_name, True)
                                play_sound_effect('left', True)
                            
                            playerLeft = {
                                "event": "lobby",
                                "action": "player-left",
                                "player": player_name
                            }
                            self.broadcast(playerLeft)


                        # check for joined players
                        for p in data['players']:
                            player_id = p['userId']
                            if 'boardId' in p and p['boardId'] != self.config.AUTODART_USER_BOARD_ID and not any(lobbyPlayer['userId'] == player_id for lobbyPlayer in lobbyPlayers):
                                lobbyPlayers.append(p)
                                player_name = str(p['name']).lower()
                                player_avg = get_player_average(player_id,access_token=self.config.access_token)
                                if player_avg != None:
                                    player_avg = str(math.ceil(player_avg))

                                ppi(player_name + " (" + player_avg + " average) joined the lobby")

                                play_sound_effect('lobby_ambient_in', False, mod = False)

                                if check_sounds([player_name, 'average', player_avg]):
                                    play_sound_effect(player_name, True)
                                    if player_avg != None:
                                        play_sound_effect('average', True)
                                        play_sound_effect(player_avg, True)
                                
                                playerJoined = {
                                    "event": "lobby",
                                    "action": "player-joined",
                                    "player": player_name,
                                    "average": player_avg
                                }
                                self.broadcast(playerJoined)
                                break
                        mirror_sounds()
                
                else:
                    ppi('INFO: unexpected ws-message')
                    # ppi(json.dumps(m, indent = 4, sort_keys = True))
                    

            except Exception as e:
                ppe('WS-Message failed: ', e)

        threading.Thread(target=process).start()

    def __on_close_autodarts(self, ws, close_status_code, close_msg):
        try:
            ppi("Websocket [" + str(ws.url) + "] closed! " + str(close_msg) + " - " + str(close_status_code))
            ppi("Retry : %s" % time.ctime())
            time.sleep(3)
            self.connect_autodarts()
        except Exception as e:
            ppe('WS-Close failed: ', e)
        
    def __on_error_autodarts(ws, error):
        try:
            ppi(error)
        except Exception as e:
            ppe('WS-Error failed: ', e)
    
    def broadcast(self,data):
        def process(*args):
            self.server.send_message_to_all(json.dumps(data, indent=2).encode('utf-8'))
        t = threading.Thread(target=process)
        t.start()
        # t.join()  

    def unicast(self,client, data, dump=True):
        def process(*args):
            send_data = data
            if dump:
                send_data = json.dumps(send_data, indent=2).encode('utf-8')
            self.server.send_message(client, send_data)
        t = threading.Thread(target=process)
        t.start()
        # t.join()

    #TODO
    def on_open_client(client, server):
        global webCallerSyncs
        ppi('NEW CLIENT CONNECTED: ' + str(client))
        cid = str(client['id'])
        if cid not in webCallerSyncs or webCallerSyncs[cid] is None:
            webCallerSyncs[cid] = queue.Queue()

    def on_message_client(self,client, server, message):
        def process(*args):
            try:
                global RANDOM_CALLER_LANGUAGE
                global RANDOM_CALLER_GENDER

                if message.startswith('board'):
                    self.board.receive_local_board_address()

                    if self.board.boardManagerAddress != None:
                        if message.startswith('board-start'):
                            msg_splitted = message.split(':')

                            wait = 0.1
                            if len(msg_splitted) > 1:
                                wait = float(msg_splitted[1])
                            if wait == 0.0:
                                wait = 0.5
                            time.sleep(wait)
                            
                            self.board.start_board()
                            
                        elif message == 'board-stop':
                            self.board.stop_board()

                        elif message == 'board-reset':
                            self.board.reset_board()

                        elif message == 'board-calibrate':
                            self.board.calibrate_board()

                        else:
                            ppi('This message is not supported')  
                    else:
                        ppi('Can not change board-state as board-address is unknown!')  

                elif message.startswith('correct'):
                    msg_splitted = message.split(':')
                    msg_splitted.pop(0)
                    throw_indices = msg_splitted[:-1]
                    score = msg_splitted[len(msg_splitted) - 1]
                    correct_throw(throw_indices, score)
                        
                elif message.startswith('next'):
                    if message.startswith('next-game'):
                        next_game()
                    else:
                        next_throw()

                elif message.startswith('undo'):
                    undo_throw()

                elif message.startswith('ban'):
                    msg_splitted = message.split(':')
                    if len(msg_splitted) > 1:
                        ban_caller(self.config.CALLER, True, self.config.BLACKLIST_PATH)
                    else:
                        ban_caller(self.config.CALLER, False, self.config.BLACKLIST_PATH)

                elif message.startswith('language'):
                    msg_splitted = message.split(':')
                    if len(msg_splitted) > 1:
                        RANDOM_CALLER_LANGUAGE = int(msg_splitted[1])
                        setup_caller()
                        if play_sound_effect('hi', wait_for_last = False):
                            mirror_sounds()

                elif message.startswith('gender'):
                    msg_splitted = message.split(':')
                    if len(msg_splitted) > 1:
                        RANDOM_CALLER_GENDER = int(msg_splitted[1])
                        setup_caller()
                        if play_sound_effect('hi', wait_for_last = False):
                            mirror_sounds()

                elif message.startswith('call'):
                    msg_splitted = message.split(':')
                    to_call = msg_splitted[1]
                    call_parts = to_call.split(' ')
                    for cp in call_parts:
                        play_sound_effect(cp, wait_for_last = False, volume_mult = 1.0)
                    mirror_sounds()

                # elif message.startswith('get'):
                #     files = []
                #     for key, value in caller.items():
                #         for sound_file in value:
                #             files.append(quote(sound_file, safe=""))
                #     get_event = {
                #         "event": "get",
                #         "caller": caller_title_without_version,
                #         "specific": CALLER != DEFAULT_CALLER and CALLER != '',
                #         "banable": BLACKLIST_PATH != DEFAULT_EMPTY_PATH
                #         "files": files
                #     }
                #     unicast(client, get_event)

                elif message.startswith('hello'):
                    welcome_event = {
                        "event": "welcome",
                        "caller": caller_title_without_version,
                        "specific": self.config.CALLER != DEFAULT_CALLER and self.config.CALLER != '',
                        "banable": self.config.BLACKLIST_PATH != DEFAULT_EMPTY_PATH
                    }
                    self.unicast(client, welcome_event)

                elif message.startswith('sync|'): 
                    exists = message[len("sync|"):].split("|")

                    # new = []
                    # count_exists = 0
                    # count_new = 0
                    # caller_copied = caller.copy()
                    # for key, value in caller_copied.items():
                    #     for sound_file in value:
                    #         base_name = os.path.basename(sound_file)
                    #         if base_name not in exists:
                    #             count_new+=1
                    #             # ppi("exists: " + base_name)

                    #             with open(sound_file, 'rb') as file:
                    #                 encoded_file = (base64.b64encode(file.read())).decode('ascii')
                    #             # print(encoded_file)
                                    
                    #             new.append({"name": base_name, "path": quote(sound_file, safe=""), "file": encoded_file})
                    #         else:
                    #             count_exists+=1
                    #             # ppi("new: " + base_name)   
                                    
                    # ppi(f"Sync {count_new} new files")
                    new = [{"name": os.path.basename(sound_file), "path": quote(sound_file, safe=""), "file": (base64.b64encode(open(sound_file, 'rb').read())).decode('ascii')} for key, value in caller.items() for sound_file in value if os.path.basename(sound_file) not in exists]

                    res = {
                        'caller': caller_title_without_version,
                        'event': 'sync',
                        'exists': new
                    }
                    self.unicast(client, res, dump=True)

                # else try to read json
                else: 
                    messageJson = json.loads(message)

                    # client requests for sync
                    if 'event' in messageJson and messageJson['event'] == 'sync' and caller is not None:                    
                        if 'parted' in messageJson:
                            cid = str(client['id'])

                            # ppi("client-id: " + cid)
                            # ppi("client parted " + str(messageJson['parted']) + " - " + str(messageJson['exists']))   
                            # ppi("client already cached: " + str(len(webCallerSyncs[cid])))             
                        
                            webCallerSyncs[cid].put(messageJson['exists'])

                            partsNeeded = messageJson['parted']
                            # ppi("Sync chunks. parts needed: " + str(partsNeeded))
                            
                            existing = []
                            if webCallerSyncs[cid].qsize() == partsNeeded:
                                while partsNeeded > 0:
                                    partsNeeded -= 1
                                    existing += webCallerSyncs[cid].get()
                                webCallerSyncs[cid].task_done()
                            else:
                                return
                            
                            new = []
                            count_exists = 0
                            count_new = 0
                            caller_copied = caller.copy()
                            for key, value in caller_copied.items():
                                for sound_file in value:
                                    base_name = os.path.basename(sound_file)
                                    if base_name not in existing:
                                        count_new += 1
                                        # ppi("new: " + base_name)

                                        with open(sound_file, 'rb') as file:
                                            encoded_file = (base64.b64encode(file.read())).decode('ascii')
                                        # print(encoded_file)
                                            
                                        new.append({"name": base_name, "path": quote(sound_file, safe=""), "file": encoded_file})
                                    else:
                                        count_exists+=1
                                        # ppi("exists: " + base_name)   
                                            
                            ppi(f"Sync chunks. {count_new} new files")

                            # new = [{"name": os.path.basename(sound_file), "path": quote(sound_file, safe=""), "file": (base64.b64encode(open(sound_file, 'rb').read())).decode('ascii')} for key, value in caller.items() for sound_file in value if os.path.basename(sound_file) not in webCallerSyncs[cid]]  
                            messageJson['exists'] = new
                            self.unicast(client, messageJson, dump=True)
                            webCallerSyncs[cid] = queue.Queue()
                        else:
                            # ppi("client already cached: " + str(len(messageJson['exists'])))
                            new = [{"name": os.path.basename(sound_file), "path": quote(sound_file, safe=""), "file": (base64.b64encode(open(sound_file, 'rb').read())).decode('ascii')} for key, value in caller.items() for sound_file in value if os.path.basename(sound_file) not in messageJson['exists']]
                            messageJson['exists'] = new
                            self.unicast(client, messageJson, dump=True)

            except Exception as e:
                ppe('WS-Client-Message failed.', e)

        t = threading.Thread(target=process).start()

    def on_left_client(client, server):
        ppi('CLIENT DISCONNECTED: ' + str(client))
        if client is not None:
            cid = str(client['id'])
            if cid in webCallerSyncs:
                webCallerSyncs[cid] = None



    def __init__(self, host, port, key, cert, config: CallerConfiguration):
        self.config = config
        self.connect_autodarts()
        self.board = Board(config)
        self.server = WebsocketServer(host=host, port=port, key=key, cert=cert, loglevel=logging.ERROR)
        self.server.set_fn_new_client(self.on_open_client)
        self.server.set_fn_client_left(self.on_left_client)
        self.server.set_fn_message_received(self.on_message_client)
        self.server.run_forever()
        
        self.websocket_server_thread = threading.Thread(target=self.start_websocket_server, args=(host, port, key, cert))
        self.websocket_server_thread.start()