import requests
import json

from globals import AUTODART_MATCHES_URL, FIELD_COORDS
from defaults import DEFAULT_EMPTY_PATH,DEFAULT_CALLER, DEFAULT_RANDOM_CALLER, DEFAULT_RANDOM_CALLER_LANGUAGE, DEFAULT_RANDOM_CALLER_GENDER
from utils import ppi, ppe
from sound import play_sound_effect, mirror_sounds
from caller import setup_caller
from board import Board
from caller_configuration import CallerConfiguration
from autodarts_keycloak_client import AutodartsKeycloakClient
from server import CallerServer

def next_game(kc: AutodartsKeycloakClient):
    if play_sound_effect('control_next_game', wait_for_last = False, volume_mult = 1.0, mod = False) == False:
        play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)
    mirror_sounds()

    # post
    # https://api.autodarts.io/gs/v0/matches/<match-id>/games/next
    try:
        global currentMatch
        if currentMatch != None:
            requests.post(AUTODART_MATCHES_URL + currentMatch + "/games/next", headers={'Authorization': 'Bearer ' + kc.access_token})

    except Exception as e:
        ppe('Next game failed', e)

def next_throw(kc: AutodartsKeycloakClient):
    if play_sound_effect('control_next', wait_for_last = False, volume_mult = 1.0, mod = False) == False:
        play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)
    mirror_sounds()

    # post
    # https://api.autodarts.io/gs/v0/matches/<match-id>/players/next
    try:
        global currentMatch
        if currentMatch != None:
            requests.post(AUTODART_MATCHES_URL + currentMatch + "/players/next", headers={'Authorization': 'Bearer ' + kc.access_token})

    except Exception as e:
        ppe('Next throw failed', e)

def undo_throw(kc: AutodartsKeycloakClient):
    if play_sound_effect('control_undo', wait_for_last = False, volume_mult = 1.0, mod = False) == False:
        play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)
    mirror_sounds()

    # post
    # https://api.autodarts.io/gs/v0/matches/<match-id>/undo
    try:
        global currentMatch
        if currentMatch != None:
            requests.post(AUTODART_MATCHES_URL + currentMatch + "/undo", headers={'Authorization': 'Bearer ' + kc.access_token})
    except Exception as e:
        ppe('Undo throw failed', e)

def correct_throw(throw_indices, score, kc: AutodartsKeycloakClient):
    global currentMatch
    score = FIELD_COORDS[score]
    if currentMatch == None or len(throw_indices) > 3 or score == None:
        return

    cdcs_success = False
    cdcs_global = False
    for tii, ti in enumerate(throw_indices):
        wait = False
        if tii > 0 and cdcs_global == True:
            wait = True
        cdcs_success = play_sound_effect(f'control_dart_correction_{(int(ti) + 1)}', wait_for_last = wait, volume_mult = 1.0, mod = False)
        if cdcs_success:
            cdcs_global = True

    if cdcs_global == False and play_sound_effect('control_dart_correction', wait_for_last = False, volume_mult = 1.0, mod = False) == False:
        play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)
    mirror_sounds()

    # patch
    # https://api.autodarts.io/gs/v0/matches/<match-id>/throws
    # {
    #     "changes": {
    #         "1": {
    #              "point": {
    #                  "x": x-coord,
    #                  "y": y-coord
    #               },
    #               "type": "normal | bouncer"    
    #         },
    #         "2": {
    #             ...
    #         }
    #     }
    # }
    try:
        global lastCorrectThrow
        data = {"changes": {}}
        for ti in throw_indices:
            data["changes"][ti] = {"point": score, "type": "normal"}

        # ppi(f'Data: {data}')
        if lastCorrectThrow == None or lastCorrectThrow != data:
            requests.patch(AUTODART_MATCHES_URL + currentMatch + "/throws", json=data, headers={'Authorization': 'Bearer ' + kc.access_token})
            lastCorrectThrow = data
        else:
            lastCorrectThrow = None 

    except Exception as e:
        lastCorrectThrow = None 
        ppe('Correcting throw failed', e)

def listen_to_match(m, ws,config: CallerConfiguration, board: Board, CallerServer: CallerServer):
    global currentMatch
    global currentMatchHost
    global currentMatchPlayers

    # EXAMPLE
    # {
    #     "channel": "autodarts.boards",
    #     "data": {
    #         "event": "start",
    #         "id": "82f917d0-0308-2c27-c4e9-f53ef2e98ad2"
    #     },
    #     "topic": "1ba2df53-9a04-51bc-9a5f-667b2c5f315f.matches"  
    # }

    if 'event' not in m:
        return

    if m['event'] == 'start':
        currentMatch = m['id']
        ppi('Listen to match: ' + currentMatch)


        try:
            setup_caller()
        except Exception as e:
            ppe("Setup callers failed!", e)

        try:
            res = requests.get(AUTODART_MATCHES_URL + currentMatch, headers={'Authorization': 'Bearer ' + config.keyCloakClient.access_token})
            m = res.json()
            # ppi(json.dumps(m, indent = 4, sort_keys = True))

            currentPlayerName = None
            players = []

            if 'players' in m:
                currentPlayer = m['players'][0]
                currentPlayerName = str(currentPlayer['name']).lower()
                players = m['players']

            if 'variant' not in m:
                return
            
            mode = m['variant']


            if mode == 'Bull-off':
                bullingStart = {
                    "event": "bulling-start"
                }
                CallerServer.broadcast(bullingStart)

                play_sound_effect('bulling_start')



            if mode == 'X01':
                currentMatchPlayers = []
                currentMatchHost = None

                if players != []:
                    for p in players:
                        if 'boardId' in p:
                            if currentMatchHost is None and m['host']['id'] == p['userId'] and p['boardId'] == config.AUTODART_USER_BOARD_ID:
                                currentMatchHost = True
                            else: 
                                currentMatchPlayers.append(p)

                # Determine "baseScore"-Key
                base = 'baseScore'
                if 'target' in m['settings']:
                    base = 'target'

                matchStarted = {
                    "event": "match-started",
                    "id": currentMatch,
                    "me": config.AUTODART_USER_BOARD_ID,
                    "meHost": currentMatchHost,
                    "players": currentMatchPlayers,
                    "player": currentPlayerName,
                    "game": {
                        "mode": mode,
                        "pointsStart": str(m['settings'][base]),
                        # TODO: fix
                        "special": "TODO"
                        }     
                    }
                CallerServer.broadcast(matchStarted)

            elif mode == 'Cricket':
                matchStarted = {
                    "event": "match-started",
                    "player": currentPlayerName,
                    "game": {
                        "mode": mode,
                        # TODO: fix
                        "special": "TODO"
                        }     
                    }
                CallerServer.broadcast(matchStarted)

            if mode != 'Bull-off':
                callPlayerNameState = False
                if config.CALL_CURRENT_PLAYER and currentPlayerName != None:
                    callPlayerNameState = play_sound_effect(currentPlayerName)

                if play_sound_effect('matchon', callPlayerNameState) == False:
                    play_sound_effect('gameon', callPlayerNameState)

                if config.AMBIENT_SOUNDS > 0.0 and play_sound_effect('ambient_matchon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                    play_sound_effect('ambient_gameon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

            mirror_sounds()
            ppi('Matchon')

        except Exception as e:
            ppe('Fetching initial match-data failed', e)

        global isGameFinished
        isGameFinished = False

        board.receive_local_board_address()

        paramsSubscribeMatchesEvents = {
            "channel": "autodarts.matches",
            "type": "subscribe",
            "topic": currentMatch + ".state"
        }

        ws.send(json.dumps(paramsSubscribeMatchesEvents))
        
    elif m['event'] == 'finish' or m['event'] == 'delete':
        ppi('Stop listening to match: ' + m['id'])

        currentMatchHost = None
        # currentMatchPlayers = None
        currentMatchPlayers = []

        paramsUnsubscribeMatchEvents = {
            "type": "unsubscribe",
            "channel": "autodarts.matches",
            "topic": m['id'] + ".state"
        }
        ws.send(json.dumps(paramsUnsubscribeMatchEvents))

        if m['event'] == 'delete':
            play_sound_effect('matchcancel', mod = False)
            mirror_sounds()

        # poll_lobbies(ws)
            
def reset_checkouts_counter():
    global checkoutsCounter
    checkoutsCounter = {}

def increase_checkout_counter(player_index, remaining_score,config: CallerConfiguration):
    global checkoutsCounter

    if player_index not in checkoutsCounter:
        checkoutsCounter[player_index] = {'remaining_score': remaining_score, 'checkout_count': 1}
    else:
        if checkoutsCounter[player_index]['remaining_score'] == remaining_score:
            checkoutsCounter[player_index]['checkout_count'] += 1
        else:
            checkoutsCounter[player_index]['remaining_score'] = remaining_score
            checkoutsCounter[player_index]['checkout_count'] = 1

    return checkoutsCounter[player_index]['checkout_count'] <= config.POSSIBLE_CHECKOUT_CALL

def checkout_only_yourself(currentPlayer,config: CallerConfiguration):
    if config.POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY:
        if 'boardId' in currentPlayer and currentPlayer['boardId'] == config.AUTODART_USER_BOARD_ID:
            return True
        else:
            return False
    return True