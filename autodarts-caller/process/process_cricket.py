from globals import SUPPORTED_CRICKET_FIELDS
from sound import play_sound_effect, mirror_sounds
from caller_configuration import caller_configuration
from utils import ppi
from caller import setup_caller
from server import caller_server

def process_match_cricket(m, config: caller_configuration, caller_server: caller_server):
    currentPlayerIndex = m['player']
    currentPlayer = m['players'][currentPlayerIndex]
    currentPlayerName = str(currentPlayer['name']).lower()
    currentPlayerIsBot = (m['players'][currentPlayerIndex]['cpuPPR'] is not None)
    turns = m['turns'][0]
    variant = m['variant']

    isGameOn = False
    isGameFin = False
    global isGameFinished
    global lastPoints

    # Call every thrown dart
    if config.CALL_EVERY_DART and turns != None and turns['throws'] != [] and len(turns['throws']) >= 1: 
        throwAmount = len(turns['throws'])
        type = turns['throws'][throwAmount - 1]['segment']['bed'].lower()
        field_name = turns['throws'][throwAmount - 1]['segment']['name'].lower()
        field_number = turns['throws'][throwAmount - 1]['segment']['number']

        if field_name == '25':
            field_name = 'sbull'
            
        # ppi("Type: " + str(type) + " - Field-name: " + str(field_name))

        # TODO non single file
        if field_number in SUPPORTED_CRICKET_FIELDS and play_sound_effect(field_name) == False:
            inner_outer = False
            if type == 'singleouter' or type == 'singleinner':
                inner_outer = play_sound_effect(type)
                if inner_outer == False:
                    play_sound_effect('single')
            else:
                play_sound_effect(type)

    # Check for matchshot
    if m['winner'] != -1 and isGameFinished == False:
        isGameFin = True

        throwPoints = 0
        lastPoints = ''
        for t in turns['throws']:
            number = t['segment']['number']
            if number in SUPPORTED_CRICKET_FIELDS:
                throwPoints += (t['segment']['multiplier'] * number)
                lastPoints += 'x' + str(t['segment']['name'])
        lastPoints = lastPoints[1:]
        
        matchWon = {
                "event": "match-won",
                "player": currentPlayerName,
                "game": {
                    "mode": variant,
                    "dartsThrownValue": throwPoints                    
                } 
            }
        caller_server.broadcast(matchWon)

        if play_sound_effect('matchshot') == False:
            play_sound_effect('gameshot')
        play_sound_effect(currentPlayerName, True)
        
        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_matchshot_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_matchshot', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_gameshot_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            else:
                play_sound_effect('ambient_gameshot', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        
        setup_caller()
        ppi('Gameshot and match')

    # Check for gameshot
    elif m['gameWinner'] != -1 and isGameFinished == False:
        isGameFin = True

        throwPoints = 0
        lastPoints = ''
        for t in turns['throws']:
            number = t['segment']['number']
            if number in SUPPORTED_CRICKET_FIELDS:
                throwPoints += (t['segment']['multiplier'] * number)
                lastPoints += 'x' + str(t['segment']['name'])
        lastPoints = lastPoints[1:]
        
        gameWon = {
                "event": "game-won",
                "player": currentPlayerName,
                "game": {
                    "mode": variant,
                    "dartsThrownValue": throwPoints
                } 
            }
        caller_server.broadcast(gameWon)

        play_sound_effect('gameshot')
        play_sound_effect(currentPlayerName, True)
        
        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_gameshot_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            else:
                play_sound_effect('ambient_gameshot', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        
        if config.RANDOM_CALLER_EACH_LEG:
            setup_caller()
        ppi('Gameshot')
    
    # Check for matchon
    elif m['gameScores'][0] == 0 and m['scores'] == None and turns['throws'] == [] and m['round'] == 1 and m['leg'] == 1 and m['set'] == 1:
        isGameOn = True
        isGameFinished = False
        
        matchStarted = {
            "event": "match-started",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                # TODO: fix
                "special": "TODO"
                }     
            }
        caller_server.broadcast(matchStarted)

        play_sound_effect(currentPlayerName, False)
        if play_sound_effect('matchon', True) == False:
            play_sound_effect('gameon', True)
        
        # play only if it is a real match not just legs!
        # if config.AMBIENT_SOUNDS != 0.0 and ('legs' in m and 'sets'):
        #     if play_sound_effect('ambient_matchon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS) == False:
        #         play_sound_effect('ambient_gameon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS)
        if config.AMBIENT_SOUNDS != 0.0:
            state = play_sound_effect('ambient_matchon_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            if state == False and play_sound_effect('ambient_matchon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                if play_sound_effect('ambient_gameon_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                    play_sound_effect('ambient_gameon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)    
        
        ppi('Matchon')

    # Check for gameon
    elif m['gameScores'][0] == 0 and m['scores'] == None and turns['throws'] == [] and m['round'] == 1:
        isGameOn = True
        isGameFinished = False
        
        gameStarted = {
            "event": "game-started",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                # TODO: fix
                "special": "TODO"
                }     
            }
        caller_server.broadcast(gameStarted)

        play_sound_effect(currentPlayerName, False)
        play_sound_effect('gameon', True)

        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_gameon_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                play_sound_effect('ambient_gameon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi('Gameon')

    # Check for busted turn
    elif turns['busted'] == True:
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

        play_sound_effect('busted')
        if config.AMBIENT_SOUNDS != 0.0:
            play_sound_effect('ambient_noscore', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        ppi('Busted')

    # Check for 1. Dart
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 1:
        isGameFinished = False

    # Check for 2. Dart
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 2:
        isGameFinished = False

    # Check for 3. Dart - points call
    elif turns != None and turns['throws'] != [] and len(turns['throws']) == 3:
        isGameFinished = False

        throwPoints = 0
        lastPoints = ''
        for t in turns['throws']:
            number = t['segment']['number']
            if number in SUPPORTED_CRICKET_FIELDS:
                throwPoints += (t['segment']['multiplier'] * number)
                lastPoints += 'x' + str(t['segment']['name'])
        lastPoints = lastPoints[1:]

        dartsThrown = {
            "event": "darts-thrown",
            "player": currentPlayerName,
            "playerIsBot": str(currentPlayerIsBot),
            "game": {
                "mode": variant,
                "dartNumber": "3",
                "dartValue": throwPoints,        

            }
        }
        caller_server.broadcast(dartsThrown)

        play_sound_effect(str(throwPoints))
        if config.AMBIENT_SOUNDS != 0.0:
            if throwPoints == 0:
                play_sound_effect('ambient_noscore', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif throwPoints == 180:
                play_sound_effect('ambient_180', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif throwPoints >= 153:
                play_sound_effect('ambient_150more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)   
            elif throwPoints >= 120:
                play_sound_effect('ambient_120more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif throwPoints >= 100:
                play_sound_effect('ambient_100more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif throwPoints >= 50:
                play_sound_effect('ambient_50more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi("Turn ended")
    
    # Playerchange
    if isGameOn == False and turns != None and turns['throws'] == [] or isGameFinished == True:
        dartsPulled = {
            "event": "darts-pulled",
            "player": str(currentPlayer['name']),
            "game": {
                "mode": variant,
                # TODO: fix
                "pointsLeft": "0",
                # TODO: fix
                "dartsThrown": "3",
                "dartsThrownValue": lastPoints,
                "busted": str(turns['busted'])
                # TODO: fix
                # "darts": [
                #     {"number": "1", "value": "60"},
                #     {"number": "2", "value": "60"},
                #     {"number": "3", "value": "60"}
                # ]
            }
        }
        caller_server.broadcast(dartsPulled)

        if config.CALL_CURRENT_PLAYER and config.CALL_CURRENT_PLAYER_ALWAYS:
            play_sound_effect(currentPlayerName)

        if config.AMBIENT_SOUNDS != 0.0:
            play_sound_effect('ambient_playerchange', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        
        ppi("Next player")

    mirror_sounds()
    if isGameFin == True:
        isGameFinished = True