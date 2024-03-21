from urllib.parse import quote, unquote
from pygame import mixer
import random
import time
from utils import ppe, ppi
from defaults import DEFAULT_CALLER_VOLUME

def check_sounds(sounds_list):
    global caller
    all_sounds_available = True
    try:
        for s in sounds_list:
            caller[s]
    except Exception as e:
        all_sounds_available = False
    return all_sounds_available

def play_sound(sound="", wait_for_last=False, volume_mult = 1, mod="",AUDIO_CALLER_VOLUME=DEFAULT_CALLER_VOLUME,WEB=0):
    volume = 1.0
    if AUDIO_CALLER_VOLUME is not None:
        volume = AUDIO_CALLER_VOLUME * volume_mult

    if WEB > 0:
        global mirror_files
        global caller_title_without_version
        
        mirror_file = {
                    "caller": caller_title_without_version,
                    "path": quote(sound, safe=""),
                    "wait": wait_for_last,
                    "volume": volume,
                    "mod": mod
                }
        mirror_files.append(mirror_file)

    if WEB == 0 or WEB == 2:
        if wait_for_last == True:
            while mixer.get_busy():
                time.sleep(0.01)

        s = mixer.Sound(sound)
        s.set_volume(volume)
        s.play()

    ppi('Playing: "' + sound + '"')

def play_sound_effect(sound_file_key="", wait_for_last = False, volume_mult = 1.0, mod = True):
    try:
        global caller
        play_sound(random.choice(caller[sound_file_key]), wait_for_last, volume_mult, mod)
        return True
    except Exception as e:
        ppe('Can not play sound for sound-file-key "' + sound_file_key + '" -> Ignore this or check existance; otherwise convert your file appropriate', e)
        return False
    
def mirror_sounds():
    global mirror_files
    if len(mirror_files) != 0: 
        # Example
        # {
        #     "event": "mirror",
        #     "files": [
        #         {
        #             "path": "C:\sounds\luca.mp3",
        #             "wait": False,
        #         },
        #         {
        #             "path": "C:\sounds\you_require.mp3",
        #             "wait": True,
        #         },
        #         {
        #             "path": "C:\sounds\40.mp3",
        #             "wait": True,
        #         }
        #     ]
        # }
        mirror = {
            "event": "mirror",
            "files": mirror_files
        }
        broadcast(mirror)
        mirror_files = []
