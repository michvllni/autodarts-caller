from sound import play_sound_effect, mirror_sounds
from utils import ppi
from caller_configuration import CallerConfiguration
from server import CallerServer

def process_match_atc(m, config: CallerConfiguration, CallerServer: CallerServer):
    global isGameFinished

    variant = m['variant']
    needHits = m['settings']['hits']
    currentPlayerIndex = m['player']
    currentPlayer = m['players'][currentPlayerIndex]
    currentPlayerName = str(currentPlayer['name']).lower()
    numberOfPlayers = len(m['players'])
    isRandomOrder = m['settings']['order'] == 'Random-Bull'

    turns = m['turns'][0]
    matchshot = (m['winner'] != -1 and isGameFinished == False)

    currentTargetsPlayer = m['state']['currentTargets'][currentPlayerIndex]
    currentTarget = m['state']['targets'][currentPlayerIndex][int(currentTargetsPlayer)]

    # weird behavior by the api i guess?
    if currentTarget['count'] == 0 and int(currentTargetsPlayer) > 0 and turns['throws'] != []:
        currentTarget = m['state']['targets'][currentPlayerIndex][int(currentTargetsPlayer) -1]

    if turns is not None and turns['throws']:
        lastThrow = turns['throws'][-1]
        targetHit = lastThrow['segment']['number']

        hit = lastThrow['segment']['bed']
        target = currentTarget['bed']

        # ppi('hit: ' + hit + ' target: ' + target)
        is_correct_bed = False
        if hit != 'Outside' and target == 'Full':
            is_correct_bed = True
        elif hit == 'SingleInner' and (target == 'Inner Single' or target == 'Single'):
            is_correct_bed = True
        elif hit == 'SingleOuter' and (target == 'Outer Single' or target == 'Single'):
            is_correct_bed = True
        elif hit == 'Double' and target == 'Double':
            is_correct_bed = True
        elif hit == 'Triple' and target == 'Triple':
            is_correct_bed = True

        if targetHit == currentTarget['number'] and is_correct_bed:
            if play_sound_effect('atc_target_hit') == False:
                play_sound_effect(str(targetHit))
        else:
            if play_sound_effect('atc_target_missed') == False:
                play_sound_effect(str(targetHit))

    if matchshot:
        isGameFinished = True
        matchWon = {
            "event": "match-won",
            "player": currentPlayerName,
            "game": {
                "mode": variant,
                "dartsThrownValue": "0"
            } 
        }
        CallerServer.broadcast(matchWon)

        if play_sound_effect('matchshot') == False:
            play_sound_effect('gameshot')

        if config.CALL_CURRENT_PLAYER:
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

        ppi('Gameshot and match')

    # only call next if more hits then 1
    elif currentTarget['hits'] == needHits and turns['throws'] != [] and (needHits > 1 or isRandomOrder):
        play_sound_effect('atc_target_next', True)
        # only call next target number if random order
        if isRandomOrder:
            play_sound_effect(str(m['state']['targets'][currentPlayerIndex][int(currentTargetsPlayer)]['number']), True)

    if turns['throws'] == []:
        play_sound_effect('ambient_playerchange', config.AMBIENT_SOUNDS_AFTER_CALLS, volume_mult = config.AMBIENT_SOUNDS, mod = False)
        if config.CALL_CURRENT_PLAYER and config.CALL_CURRENT_PLAYER_ALWAYS and numberOfPlayers > 1:
            play_sound_effect(currentPlayerName, True)
    
    mirror_sounds()
