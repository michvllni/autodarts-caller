import requests
from utils import ppi,ppe
from sound import play_sound_effect, mirror_sounds
from globals import AUTODART_BOARDS_URL
from caller_configuration import CallerConfiguration

class Board:
    boardManagerAdress: str
    config: CallerConfiguration

    def __init__(self,CallerConfiguration: CallerConfiguration):
        self.config = CallerConfiguration
        self.receive_local_board_address()

    def start_board(self):
        try:
            res = requests.put(self.boardManagerAddress + '/api/detection/start')
            # res = requests.put(boardManagerAddress + '/api/start')
            # ppi(res)
        except Exception as e:
            ppe('Start board failed', e)

    def stop_board(self):
        try:    
            res = requests.put(self.boardManagerAddress + '/api/detection/stop')
            # res = requests.put(boardManagerAddress + '/api/stop')
            # ppi(res)
        except Exception as e:
            ppe('stop board failed', e)

    def reset_board(self):
        try:
            res = requests.post(self.boardManagerAddress + '/api/reset')
            # ppi(res)
        except Exception as e:
            ppe('Reset board failed', e)

    def calibrate_board(self):
        if play_sound_effect('control_calibrate', wait_for_last = False, volume_mult = 1.0) == False:
            play_sound_effect('control', wait_for_last = False, volume_mult = 1.0)
        mirror_sounds()

        try:
            res = requests.post(self.boardManagerAddress + '/api/config/calibration/auto')
            # ppi(res)
        except Exception as e:
            ppe('Calibrate board failed', e)
    
    def receive_local_board_address(self):
        try:        
            if self.boardManagerAddress == None:
                res = requests.get(AUTODART_BOARDS_URL + self.config.AUTODART_USER_BOARD_ID, headers={'Authorization': 'Bearer ' + self.config.keyCloakClient.access_token})
                board_ip = res.json()['ip']
                if board_ip != None and board_ip != '':  
                    self.boardManagerAddress = 'http://' + board_ip
                    ppi('Board-address: ' + self.boardManagerAddress) 
                else:
                    self.boardManagerAddress = None
                    ppi('Board-address: UNKNOWN') 
                
        except Exception as e:
            self.boardManagerAddress = None
            ppe('Fetching local-board-address failed', e)