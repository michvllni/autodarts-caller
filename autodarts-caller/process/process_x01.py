import math
from globals import BOGEY_NUMBERS
from utils import ppi
from caller import setup_caller
from caller_configuration import caller_configuration
from match_helpers import checkout_only_yourself, increase_checkout_counter, reset_checkouts_counter
from sound import play_sound_effect, mirror_sounds
from server import caller_server

def process_match_x01(m, config: caller_configuration, caller_server: caller_server):
    global currentMatch
    global currentMatchHost
    global currentMatchPlayers
    global isGameFinished
    global lastPoints
    
    variant = m['variant']
    players = m['players']
    currentPlayerIndex = m['player']
    currentPlayer = m['players'][currentPlayerIndex]
    currentPlayerName = str(currentPlayer['name']).lower()
    currentPlayerIsBot = (m['players'][currentPlayerIndex]['cpuPPR'] is not None)
    remainingPlayerScore = m['gameScores'][currentPlayerIndex]
    numberOfPlayers = len(m['players'])

    turns = m['turns'][0]
    points = str(turns['points'])
    busted = (turns['busted'] == True)
    matchshot = (m['winner'] != -1 and isGameFinished == False)
    gameshot = (m['gameWinner'] != -1 and isGameFinished == False)
    
    # Determine "baseScore"-Key
    base = 'baseScore'
    if 'target' in m['settings']:
        base = 'target'
    
    matchon = (m['settings'][base] == m['gameScores'][0] and turns['throws'] == [] and m['leg'] == 1 and m['set'] == 1)
    gameon = (m['settings'][base] == m['gameScores'][0] and turns['throws'] == [])

    # ppi('matchon: '+ str(matchon) )
    # ppi('gameon: '+ str(gameon) )
    # ppi('isGameFinished: ' + str(isGameFinished))

    pcc_success = False
    isGameFin = False

    if turns != None and turns['throws'] != []:
        lastPoints = points

    # Darts pulled (Playerchange and Possible-checkout)
    if gameon == False and turns != None and turns['throws'] == [] or isGameFinished == True:
        busted = "False"
        if lastPoints == "B":
            lastPoints = "0"
            busted = "True"

        dartsPulled = {
            "event": "darts-pulled",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                # TODO: fix
                "pointsLeft": str(remainingPlayerScore),
                # TODO: fix
                "dartsThrown": "3",
                "dartsThrownValue": lastPoints,
                "busted": busted
                # TODO: fix
                # "darts": [
                #     {"number": "1", "value": "60"},
                #     {"number": "2", "value": "60"},
            
                #     {"number": "3", "value": "60"}
                # ]
            }
        }
        # ppi(dartsPulled)
        caller_server.broadcast(dartsPulled)

        
        if gameon == False and isGameFinished == False:

            # Check for possible checkout
            if config.POSSIBLE_CHECKOUT_CALL and \
                    m['player'] == currentPlayerIndex and \
                    remainingPlayerScore <= 170 and \
                    checkout_only_yourself(currentPlayer,config):
                
                if not increase_checkout_counter(currentPlayerIndex, remainingPlayerScore, config):
                    if config.config.AMBIENT_SOUNDS != 0.0:
                        play_sound_effect('ambient_checkout_call_limit', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                else:
                    remaining = str(remainingPlayerScore)
                    if remainingPlayerScore not in BOGEY_NUMBERS:
                        if config.CALL_CURRENT_PLAYER:
                            play_sound_effect(currentPlayerName)

                        if config.POSSIBLE_CHECKOUT_CALL_SINGLE_FILE:
                            pcc_success = play_sound_effect('yr_' + remaining, True)
                            if pcc_success == False:
                                pcc_success = play_sound_effect(remaining, True)
                        else:
                            pcc_success = (play_sound_effect('you_require', True) and play_sound_effect(remaining, True))
                        
                        ppi('Checkout possible: ' + remaining)
                    else:
                        if config.AMBIENT_SOUNDS != 0.0:
                            play_sound_effect('ambient_bogey_number', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                        ppi('bogey-number: ' + remaining)

            if pcc_success == False and config.CALL_CURRENT_PLAYER and config.CALL_CURRENT_PLAYER_ALWAYS and numberOfPlayers > 1:
                play_sound_effect(currentPlayerName)

            # Player-change
            if pcc_success == False and config.AMBIENT_SOUNDS != 0.0:
                play_sound_effect('ambient_playerchange', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                

            ppi("Next player")

    # Call every thrown dart
    elif config.CALL_EVERY_DART == True and turns != None and turns['throws'] != [] and len(turns['throws']) >= 1 and busted == False and matchshot == False and gameshot == False: 

        throwAmount = len(turns['throws'])
        type = turns['throws'][throwAmount - 1]['segment']['bed'].lower()
        field_name = turns['throws'][throwAmount - 1]['segment']['name'].lower()
 
        if field_name == '25':
            field_name = 'sbull'

        # ppi("Type: " + str(type) + " - Field-name: " + str(field_name))

        if config.CALL_EVERY_DART_SINGLE_FILE == True:
            if play_sound_effect(field_name) == False:
                inner_outer = False
                if type == 'singleouter' or type == 'singleinner':
                    inner_outer = play_sound_effect(type)
                    if inner_outer == False:
                        play_sound_effect('single')
                else:
                    play_sound_effect(type)
            

        elif len(turns['throws']) <= 2:
            field_number = str(turns['throws'][throwAmount - 1]['segment']['number'])

            if type == 'single' or type == 'singleinner' or type == "singleouter":
                play_sound_effect(field_number)
            elif type == 'double' or type == 'triple':
                play_sound_effect(type)
                play_sound_effect(field_number, True)
            else:
                play_sound_effect('outside')
            
    # Check for matchshot
    if matchshot == True:
        isGameFin = True
        
        matchWon = {
                "event": "match-won",
                "player": currentPlayerName,
                "game": {
                    "mode": variant,
                    "dartsThrownValue": points
                } 
            }
        caller_server.broadcast(matchWon)

        if play_sound_effect('matchshot') == False:
            play_sound_effect('gameshot')

        if config.CALL_CURRENT_PLAYER:
            play_sound_effect(currentPlayerName, True)

        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_matchshot_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_matchshot', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_gameshot_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            else:
                play_sound_effect('ambient_gameshot', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            

        if config.RANDOM_CALLER_EACH_LEG:
            setup_caller()
        ppi('Gameshot and match')

    # Check for gameshot
    elif gameshot == True:
        isGameFin = True
        
        gameWon = {
                "event": "game-won",
                "player": currentPlayerName,
                "game": {
                    "mode": variant,
                    "dartsThrownValue": points
                } 
            }
        caller_server.broadcast(gameWon)

        gameshotState = play_sound_effect('gameshot')

        currentPlayerScoreLegs = m['scores'][currentPlayerIndex]['legs']
        # currentPlayerScoreSets = m['scores'][currentPlayerIndex]['sets']
        currentLeg = m['leg']
        currentSet = m['set']
        # maxLeg = m['legs']
        # maxSets = m['sets']

        # ppi('currentLeg: ' + str(currentLeg))
        # ppi('currentSet: ' + str(currentSet))

        isSet = False
        if 'sets' not in m:
            play_sound_effect('leg_' + str(currentLeg), gameshotState)
        else:
            if currentPlayerScoreLegs == 0:
                play_sound_effect('set_' + str(currentSet), gameshotState)
                isSet = True
            else:
                play_sound_effect('leg_' + str(currentLeg), gameshotState)    

        if config.CALL_CURRENT_PLAYER:
            play_sound_effect(currentPlayerName, True)

        if config.AMBIENT_SOUNDS != 0.0:
            if isSet == True:
                if play_sound_effect('ambient_setshot_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                    pass
                elif play_sound_effect('ambient_setshot', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                    pass
                elif play_sound_effect('ambient_gameshot_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                    pass
                else:
                    play_sound_effect('ambient_gameshot', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                    
            else:
                if play_sound_effect('ambient_gameshot_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                    pass
                else:
                    play_sound_effect('ambient_gameshot', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        if config.RANDOM_CALLER_EACH_LEG:
            setup_caller()
        ppi('Gameshot')

    # Check for matchon
    elif matchon == True:
        isGameFinished = False

        reset_checkouts_counter()


        currentMatchPlayers = []
        currentMatchHost = None
        if players != []:
            for p in players:
                if 'boardId' in p:
                    if currentMatchHost is None and m['host']['id'] == p['userId'] and p['boardId'] == config.AUTODART_USER_BOARD_ID:
                        currentMatchHost = True
                    else:
                        currentMatchPlayers.append(p)

        matchStarted = {
            "event": "match-started",
            "id": currentMatch,
            "me": config.AUTODART_USER_BOARD_ID,
            "meHost": currentMatchHost,
            "players": currentMatchPlayers,
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                "pointsStart": str(base),
                # TODO: fix
                "special": "TODO"
                }     
            }
        caller_server.broadcast(matchStarted)

        callPlayerNameState = False
        if config.CALL_CURRENT_PLAYER:
            callPlayerNameState = play_sound_effect(currentPlayerName)

        if play_sound_effect('matchon', callPlayerNameState, mod = False) == False:
            play_sound_effect('gameon', callPlayerNameState, mod = False)

        if config.AMBIENT_SOUNDS != 0.0:
            state = play_sound_effect('ambient_matchon_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            if state == False and play_sound_effect('ambient_matchon', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                if play_sound_effect('ambient_gameon_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                    play_sound_effect('ambient_gameon', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)


        ppi('Matchon')

    # Check for gameon
    elif gameon == True:
        isGameFinished = False

        reset_checkouts_counter()

        gameStarted = {
            "event": "game-started",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                "pointsStart": str(base),
                # TODO: fix
                "special": "TODO"
                }     
            }
        caller_server.broadcast(gameStarted)

        callPlayerNameState = False
        if config.CALL_CURRENT_PLAYER:
            callPlayerNameState = play_sound_effect(currentPlayerName)

        play_sound_effect('gameon', callPlayerNameState, mod = False)

        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_gameon_' + currentPlayerName, config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                play_sound_effect('ambient_gameon', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi('Gameon')
          
    # Check for busted turn
    elif busted == True:
        lastPoints = "B"
        isGameFinished = False

        busted = { 
                    "event": "busted",
                    "player": currentPlayerName,
                    "playerIsBot": str(currentPlayerIsBot),
                    "game": {
                        "mode": variant
                    }       
                }
        caller_server.broadcast(busted)

        play_sound_effect('busted', mod = False)

        if config.AMBIENT_SOUNDS != 0.0:
            play_sound_effect('ambient_noscore', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi('Busted')
    
    # Check for 1. Dart
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 1:
        isGameFinished = False

    # Check for 2. Dart
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 2:
        isGameFinished = False

    # Check for 3. Dart - Score-call
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 3:
        isGameFinished = False

        dartsThrown = {
            "event": "darts-thrown",
            "player": currentPlayerName,
            "playerIsBot": str(currentPlayerIsBot),
            "game": {
                "mode": variant,
                "pointsLeft": str(remainingPlayerScore),
                "dartNumber": "3",
                "dartValue": points,        
            }
        }
        caller_server.broadcast(dartsThrown)

        play_sound_effect(points)

        if config.AMBIENT_SOUNDS != 0.0:
            ambient_x_success = False

            throw_combo = ''
            for t in turns['throws']:
                throw_combo += t['segment']['name'].lower()
            # ppi(throw_combo)

            if turns['points'] != 0:
                ambient_x_success = play_sound_effect('ambient_' + str(throw_combo), config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                if ambient_x_success == False:
                    ambient_x_success = play_sound_effect('ambient_' + str(turns['points']), config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

            if ambient_x_success == False:
                if turns['points'] >= 150:
                    play_sound_effect('ambient_150more', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)   
                elif turns['points'] >= 120:
                    play_sound_effect('ambient_120more', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif turns['points'] >= 100:
                    play_sound_effect('ambient_100more', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif turns['points'] >= 50:
                    play_sound_effect('ambient_50more', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif turns['points'] >= 1:
                    play_sound_effect('ambient_1more', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                else:
                    play_sound_effect('ambient_noscore', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

            # Koordinaten der Pfeile
            coords = []
            for t in turns['throws']:
                if 'coords' in t:
                    coords.append({"x": t['coords']['x'], "y": t['coords']['y']})

            # ppi(str(coords))

            # Suche das Koordinatenpaar, das am weitesten von den beiden Anderen entfernt ist
            if len(coords) == 3:
                # Liste mit allen möglichen Kombinationen von Koordinatenpaaren erstellen
                combinations = [(coords[0], coords[1]), (coords[0], coords[2]), (coords[1], coords[2])]

                # Variablen für das ausgewählte Koordinatenpaar und die maximale Gesamtdistanz initialisieren
                selected_coord = None
                max_total_distance = 0

                # Gesamtdistanz für jede Kombination von Koordinatenpaaren berechnen
                for combination in combinations:
                    dist1 = math.sqrt((combination[0]["x"] - combination[1]["x"])**2 + (combination[0]["y"] - combination[1]["y"])**2)
                    dist2 = math.sqrt((combination[1]["x"] - combination[0]["x"])**2 + (combination[1]["y"] - combination[0]["y"])**2)
                    total_distance = dist1 + dist2
                    
                    # Überprüfen, ob die Gesamtdistanz größer als die bisher größte Gesamtdistanz ist
                    if total_distance > max_total_distance:
                        max_total_distance = total_distance
                        selected_coord = combination[0]

                group_score = 100.0
                if selected_coord != None:
                    
                    # Distanz von selected_coord zu coord2 berechnen
                    dist1 = math.sqrt((selected_coord["x"] - coords[1]["x"])**2 + (selected_coord["y"] - coords[1]["y"])**2)

                    # Distanz von selected_coord zu coord3 berechnen
                    dist2 = math.sqrt((selected_coord["x"] - coords[2]["x"])**2 + (selected_coord["y"] -  coords[2]["y"])**2)

                    # Durchschnitt der beiden Distanzen berechnen
                    avg_dist = (dist1 + dist2) / 2

                    group_score = (1.0 - avg_dist) * 100

                # ppi("Distance by max_dis_coord to coord2: " + str(dist1))
                # ppi("Distance by max_dis_coord to coord3: " + str(dist2))
                # ppi("Group-score: " + str(group_score))

                if group_score >= 98:
                    play_sound_effect('ambient_group_legendary', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)   
                elif group_score >= 95:
                    play_sound_effect('ambient_group_perfect', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif group_score >= 92:
                    play_sound_effect('ambient_group_very_nice', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif group_score >= 89:
                    play_sound_effect('ambient_group_good', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
                elif group_score >= 86:
                    play_sound_effect('ambient_group_normal', config.config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi("Turn ended")

    mirror_sounds()

    if isGameFin == True:
        isGameFinished = True