from caller_configuration import CallerConfiguration
from sound import play_sound_effect, mirror_sounds
from utils import ppi
from server import CallerServer

def process_match_rtw(m, config: CallerConfiguration, CallerServer: CallerServer):
    global isGameFinished

    variant = m['variant']
    currentPlayerIndex = m['player']
    currentPlayerName = m['players'][currentPlayerIndex]['name'].lower()
    currentPlayerIsBot = (m['players'][currentPlayerIndex]['cpuPPR'] is not None)
    numberOfPlayers = len(m['players'])
    isRandomOrder = m['settings']['order'] == 'Random-Bull'
    winningPlayerIndex = int(m['winner'])
    winningPlayerName = ''
    if winningPlayerIndex != -1:
        winningPlayerName = m['players'][winningPlayerIndex]['name'].lower()
    order = m['settings']['order']
    turn = m['turns'][0]
    points = turn['points']
    currentTarget = 0
    if order == '1-20-Bull':
        currentTarget = m['round']
    elif order == '20-1-Bull':
        currentTarget = 21 - m['round']
    if currentTarget == 0 or currentTarget == 21:
        currentTarget = 25

    gameon = (0 == m['gameScores'][0] and turn['throws'] == [])
    matchover = (winningPlayerIndex != -1 and isGameFinished == False)

    # Darts pulled (Playerchange and Possible-checkout)
    if gameon == False and turn != None and turn['throws'] == [] or isGameFinished == True:
        dartsPulled = {
            "event": "darts-pulled",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                # TODO: fix
                "dartsThrown": "3",
                "dartsThrownValue": points,
                # TODO: fix
                # "darts": [
                #     {"number": "1", "value": "60"},
                #     {"number": "2", "value": "60"},
            
                #     {"number": "3", "value": "60"}
                # ]
            }
        }
        # ppi(dartsPulled)
        CallerServer.broadcast(dartsPulled)
    elif config.CALL_EVERY_DART == True and turn is not None and turn['throws'] and not isRandomOrder:
        lastThrow = turn['throws'][-1]
        targetHit = lastThrow['segment']['number']

        hit = lastThrow['segment']['bed']

        if targetHit == currentTarget:
            if hit == 'Single' or hit == 'SingleInner' or hit == 'SingleOuter':
                if play_sound_effect('rtw_target_hit_single',True) == False:
                    if play_sound_effect(hit,True) == False:
                        play_sound_effect(str(1),True)
            elif hit == 'Double':
                if play_sound_effect('rtw_target_hit_double',True) == False:
                    if play_sound_effect(hit,True) == False:
                        play_sound_effect(str(2),True)
            elif hit == 'Triple':
                if play_sound_effect('rtw_target_hit_triple',True) == False:
                    if play_sound_effect(hit,True) == False:
                        play_sound_effect(str(3),True)
        else:
            if play_sound_effect('rtw_target_missed',True) == False:
                play_sound_effect(str(0),True)

    # Check for 3. Dart - points call
    if turn != None and turn['throws'] != [] and len(turn['throws']) == 3:
        dartsThrown = {
            "event": "darts-thrown",
            "player": currentPlayerName,
            "playerIsBot": str(currentPlayerIsBot),
            "game": {
                "mode": variant,
                "dartNumber": "3",
                "dartValue": points,        

            }
        }
        CallerServer.broadcast(dartsThrown)

        play_sound_effect(str(points),True)
        if config.AMBIENT_SOUNDS != 0.0:
            if int(points) == 0:
                play_sound_effect('ambient_noscore', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif int(points) == 9:
                play_sound_effect('ambient_180', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif int(points) >= 7:
                play_sound_effect('ambient_150more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)   
            elif int(points) >= 6:
                play_sound_effect('ambient_120more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif int(points) >= 5:
                play_sound_effect('ambient_100more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
            elif int(points) >= 4:
                play_sound_effect('ambient_50more', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi("Turn ended")
    
    if matchover:
        isGameFinished = True
        matchWon = {
            "event": "match-won",
            "player": m['players'][winningPlayerIndex],
            "game": {
                "mode": variant,
                "dartsThrownValue": "0"
            } 
        }
        CallerServer.broadcast(matchWon)

        if play_sound_effect('matchshot') == False:
            play_sound_effect('gameshot')

        if config.CALL_CURRENT_PLAYER:
            play_sound_effect(winningPlayerName, True)

        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_matchshot_' + winningPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_matchshot', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            elif play_sound_effect('ambient_gameshot_' + winningPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False):
                pass
            else:
                play_sound_effect('ambient_gameshot', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi('Gameshot and match')
        
    if m['gameScores'][0] == 0 and m['scores'] == None and turn['throws'] == [] and m['round'] == 1:
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
        CallerServer.broadcast(gameStarted)

        play_sound_effect(currentPlayerName, False)
        play_sound_effect('gameon', True)

        if config.AMBIENT_SOUNDS != 0.0:
            if play_sound_effect('ambient_gameon_' + currentPlayerName, config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False) == False:
                play_sound_effect('ambient_gameon', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)

        ppi('Gameon')

    # only call next target number if random order
    if isRandomOrder:
        play_sound_effect(str(m['state']['targets'][currentPlayerIndex][int(currentTarget)]['number']), True)

    if turn['throws'] == []:
        play_sound_effect('ambient_playerchange', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        if config.CALL_CURRENT_PLAYER and config.CALL_CURRENT_PLAYER_ALWAYS and numberOfPlayers > 1:
            play_sound_effect(currentPlayerName, True)
    
    mirror_sounds()
