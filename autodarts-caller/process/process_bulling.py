from sound import play_sound_effect, mirror_sounds
from server import CallerServer

def process_bulling(m, CallerServer: CallerServer):
    currentPlayerIndex = m['player']
    currentPlayer = m['players'][currentPlayerIndex]
    currentPlayerName = str(currentPlayer['name']).lower()
    currentPlayerIsBot = (m['players'][currentPlayerIndex]['cpuPPR'] is not None)
    gameshot = m['gameWinner'] != -1

    if gameshot == True:
        bullingEnd = {
            "event": "bulling-end",
            "player": currentPlayerName,
            "playerIsBot": str(currentPlayerIsBot)
        }
        CallerServer.broadcast(bullingEnd)

        name = play_sound_effect((m['players'][m['gameWinner']]['name']).lower())
        if name:
            play_sound_effect('bulling_end', wait_for_last=True)
    else:
        if m['round'] == 1 and m['gameScores'] is None:  
            bullingStart = {
                "event": "bulling-start",
                "player": currentPlayerName,
                "playerIsBot": str(currentPlayerIsBot)
            }
            CallerServer.broadcast(bullingStart)

            play_sound_effect('bulling_start')
        
    mirror_sounds()

