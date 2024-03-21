import os
import sys
from pathlib import Path
import platform
import argparse
from pygame import mixer
import logging
import ssl
import certifi
from werkzeug.serving import make_ssl_devcert

from utils import ppi, ppe, check_paths, check_already_running
from globals import AUTODART_URL, SUPPORTED_GAME_VARIANTS, CALLER_LANGUAGES, CALLER_GENDERS
from defaults import DEFAULT_HOST_IP, DEFAULT_EMPTY_PATH, DEFAULT_CALLER_VOLUME, DEFAULT_CALLER, DEFAULT_RANDOM_CALLER, DEFAULT_RANDOM_CALLER_EACH_LEG, DEFAULT_RANDOM_CALLER_LANGUAGE, DEFAULT_RANDOM_CALLER_GENDER, DEFAULT_CALL_CURRENT_PLAYER, DEFAULT_CALL_CURRENT_PLAYER_ALWAYS, DEFAULT_CALL_EVERY_DART, DEFAULT_CALL_EVERY_DART_SINGLE_FILES, DEFAULT_POSSIBLE_CHECKOUT_CALL, DEFAULT_POSSIBLE_CHECKOUT_CALL_SINGLE_FILES, DEFAULT_POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY, DEFAULT_AMBIENT_SOUNDS, DEFAULT_AMBIENT_SOUNDS_AFTER_CALLS, DEFAULT_DOWNLOADS, DEFAULT_DOWNLOADS_LIMIT, DEFAULT_DOWNLOADS_LANGUAGE, DEFAULT_DOWNLOADS_NAME, DEFAULT_BACKGROUND_AUDIO_VOLUME, DEFAULT_WEB_CALLER, DEFAULT_WEB_CALLER_SCOREBOARD, DEFAULT_WEB_CALLER_PORT, DEFAULT_WEB_CALLER_DISABLE_HTTPS, DEFAULT_HOST_PORT, DEFAULT_DEBUG, DEFAULT_CERT_CHECK, DEFAULT_MIXER_FREQUENCY, DEFAULT_MIXER_SIZE, DEFAULT_MIXER_CHANNELS, DEFAULT_MIXER_BUFFERSIZE, DEFAULT_DOWNLOADS_PATH, DEFAULT_CALLERS_BANNED_FILE
from audio import BackgroundAudio
from caller_configuration import CallerConfiguration
from caller import load_callers_banned, download_callers, setup_caller
from web_caller import WebCaller
from server import CallerServer

if __name__ == "__main__":
    os.environ['SSL_CERT_FILE'] = certifi.where()
    plat = platform.system()

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    sh.setFormatter(formatter)
    logger=logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(sh)

    main_directory = os.path.dirname(os.path.realpath(__file__))
    parent_directory = os.path.dirname(main_directory)


    VERSION = '2.11.0'

    check_already_running()
        
    ap = argparse.ArgumentParser()
    
    ap.add_argument("-U", "--autodarts_email", required=True, help="Registered email address at " + AUTODART_URL)
    ap.add_argument("-P", "--autodarts_password", required=True, help="Registered password address at " + AUTODART_URL)
    ap.add_argument("-B", "--autodarts_board_id", required=True, help="Registered board-id at " + AUTODART_URL)
    ap.add_argument("-M", "--media_path", required=True, help="Absolute path to your media")
    ap.add_argument("-MS", "--media_path_shared", required=False, default=DEFAULT_EMPTY_PATH, help="Absolute path to shared media folder (every caller get sounds)")
    ap.add_argument("-V", "--caller_volume", type=float, default=DEFAULT_CALLER_VOLUME, required=False, help="Sets calling-volume between 0.0 (silent) and 1.0 (max)")
    ap.add_argument("-C", "--caller", default=DEFAULT_CALLER, required=False, help="Sets a specific caller (voice-pack) for calling")
    ap.add_argument("-R", "--random_caller", type=int, choices=range(0, 2), default=DEFAULT_RANDOM_CALLER, required=False, help="If '1', the application will randomly choose a caller each game. It only works when your base-media-folder has subfolders with its files")
    ap.add_argument("-L", "--random_caller_each_leg", type=int, choices=range(0, 2), default=DEFAULT_RANDOM_CALLER_EACH_LEG, required=False, help="If '1', the application will randomly choose a caller each leg instead of each game. It only works when 'random_caller=1'")
    ap.add_argument("-RL", "--random_caller_language", type=int, choices=range(0, len(CALLER_LANGUAGES) + 1), default=DEFAULT_RANDOM_CALLER_LANGUAGE, required=False, help="If '0', the application will allow every language.., else it will limit caller selection by specific language")
    ap.add_argument("-RG", "--random_caller_gender", type=int, choices=range(0, len(CALLER_GENDERS) + 1), default=DEFAULT_RANDOM_CALLER_GENDER, required=False, help="If '0', the application will allow every gender.., else it will limit caller selection by specific gender")
    ap.add_argument("-CCP", "--call_current_player", type=int, choices=range(0, 2), default=DEFAULT_CALL_CURRENT_PLAYER, required=False, help="If '1', the application will call who is the current player to throw")
    ap.add_argument("-CCPA", "--call_current_player_always", type=int, choices=range(0, 2), default=DEFAULT_CALL_CURRENT_PLAYER_ALWAYS, required=False, help="If '1', the application will call every playerchange")
    ap.add_argument("-E", "--call_every_dart", type=int, choices=range(0, 2), default=DEFAULT_CALL_EVERY_DART, required=False, help="If '1', the application will call every thrown dart")
    ap.add_argument("-ESF", "--call_every_dart_single_files", type=int, choices=range(0, 2), default=DEFAULT_CALL_EVERY_DART_SINGLE_FILES, required=False, help="If '1', the application will call a every dart by using single, dou.., else it uses two separated sounds: single + x (score)")
    ap.add_argument("-PCC", "--possible_checkout_call", type=int, default=DEFAULT_POSSIBLE_CHECKOUT_CALL, required=False, help="If '1', the application will call a possible checkout starting at 170")
    ap.add_argument("-PCCSF", "--possible_checkout_call_single_files", type=int, choices=range(0, 2), default=DEFAULT_POSSIBLE_CHECKOUT_CALL_SINGLE_FILES, required=False, help="If '1', the application will call a possible checkout by using yr_2-yr_170, else it uses two separated sounds: you_require + x")
    ap.add_argument("-PCCYO", "--possible_checkout_call_yourself_only", type=int, choices=range(0, 2), default=DEFAULT_POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY, required=False, help="If '1' the caller will only call if there is a checkout possibility if the current player is you")
    ap.add_argument("-A", "--ambient_sounds", type=float, default=DEFAULT_AMBIENT_SOUNDS, required=False, help="If > '0.0' (volume), the application will call a ambient_*-Sounds")
    ap.add_argument("-AAC", "--ambient_sounds_after_calls", type=int, choices=range(0, 2), default=DEFAULT_AMBIENT_SOUNDS_AFTER_CALLS, required=False, help="If '1', the ambient sounds will appear after calling is finished") 
    ap.add_argument("-DL", "--downloads", type=int, choices=range(0, 2), default=DEFAULT_DOWNLOADS, required=False, help="If '1', the application will try to download a curated list of caller-voices")
    ap.add_argument("-DLL", "--downloads_limit", type=int, default=DEFAULT_DOWNLOADS_LIMIT, required=False, help="If '1', the application will try to download a only the X newest caller-voices. -DLN needs to be activated.")
    ap.add_argument("-DLLA", "--downloads_language", type=int, choices=range(0, len(CALLER_LANGUAGES) + 1), default=DEFAULT_DOWNLOADS_LANGUAGE, required=False, help="If '0', the application will download speakers of every language.., else it will limit speaker downloads by specific language")
    ap.add_argument("-DLN", "--downloads_name", default=DEFAULT_DOWNLOADS_NAME, required=False, help="Sets a specific caller (voice-pack) for download")
    ap.add_argument("-BLP", "--blacklist_path", required=False, default=DEFAULT_EMPTY_PATH, help="Absolute path to storage directory for blacklist-file")
    ap.add_argument("-BAV","--background_audio_volume", required=False, type=float, default=DEFAULT_BACKGROUND_AUDIO_VOLUME, help="Set background-audio-volume between 0.1 (silent) and 1.0 (no mute)")
    ap.add_argument("-WEB", "--web_caller", required=False, type=int, choices=range(0, 3), default=DEFAULT_WEB_CALLER, help="If '1' the application will host an web-endpoint, '2' it will do '1' and default caller-functionality.")
    ap.add_argument("-WEBSB", "--web_caller_scoreboard", required=False, type=int, choices=range(0, 2), default=DEFAULT_WEB_CALLER_SCOREBOARD, help="If '1' the application will host an web-endpoint, right to web-caller-functionality.")
    ap.add_argument("-WEBP", "--web_caller_port", required=False, type=int, default=DEFAULT_WEB_CALLER_PORT, help="Web-Caller-Port")
    ap.add_argument("-WEBDH", "--web_caller_disable_https", required=False, type=int, choices=range(0, 2), default=DEFAULT_WEB_CALLER_DISABLE_HTTPS, help="If '0', the web caller will use http instead of https. This is unsecure, be careful!")
    ap.add_argument("-HP", "--host_port", required=False, type=int, default=DEFAULT_HOST_PORT, help="Host-Port")
    ap.add_argument("-DEB", "--debug", type=int, choices=range(0, 2), default=DEFAULT_DEBUG, required=False, help="If '1', the application will output additional information")
    ap.add_argument("-CC", "--cert_check", type=int, choices=range(0, 2), default=DEFAULT_CERT_CHECK, required=False, help="If '0', the application won't check any ssl certification")
    ap.add_argument("-MIF", "--mixer_frequency", type=int, required=False, default=DEFAULT_MIXER_FREQUENCY, help="Pygame mixer frequency")
    ap.add_argument("-MIS", "--mixer_size", type=int, required=False, default=DEFAULT_MIXER_SIZE, help="Pygame mixer size")
    ap.add_argument("-MIC", "--mixer_channels", type=int, required=False, default=DEFAULT_MIXER_CHANNELS, help="Pygame mixer channels")
    ap.add_argument("-MIB", "--mixer_buffersize", type=int, required=False, default=DEFAULT_MIXER_BUFFERSIZE, help="Pygame mixer buffersize")
    
    args = vars(ap.parse_args())

    global RANDOM_CALLER_GENDER
    global RANDOM_CALLER_LANGUAGE
    
    AUTODART_USER_EMAIL = args['autodarts_email']                          
    AUTODART_USER_PASSWORD = args['autodarts_password']              
    AUTODART_USER_BOARD_ID = args['autodarts_board_id']        
    AUDIO_MEDIA_PATH = Path(args['media_path'])
    if args['media_path_shared'] != DEFAULT_EMPTY_PATH:
        AUDIO_MEDIA_PATH_SHARED = Path(args['media_path_shared'])
    else:
        AUDIO_MEDIA_PATH_SHARED = DEFAULT_EMPTY_PATH
    AUDIO_CALLER_VOLUME = args['caller_volume']
    CALLER = args['caller']
    RANDOM_CALLER = args['random_caller']   
    RANDOM_CALLER_EACH_LEG = args['random_caller_each_leg']   
    RANDOM_CALLER_LANGUAGE = args['random_caller_language'] 
    if RANDOM_CALLER_LANGUAGE < 0: RANDOM_CALLER_LANGUAGE = DEFAULT_RANDOM_CALLER_LANGUAGE
    RANDOM_CALLER_GENDER = args['random_caller_gender'] 
    if RANDOM_CALLER_GENDER < 0: RANDOM_CALLER_GENDER = DEFAULT_RANDOM_CALLER_GENDER
    CALL_CURRENT_PLAYER = args['call_current_player']
    CALL_CURRENT_PLAYER_ALWAYS = args['call_current_player_always']
    CALL_EVERY_DART = args['call_every_dart']
    CALL_EVERY_DART_SINGLE_FILE = args['call_every_dart_single_files']
    POSSIBLE_CHECKOUT_CALL = args['possible_checkout_call']
    if POSSIBLE_CHECKOUT_CALL < 0: POSSIBLE_CHECKOUT_CALL = 0
    POSSIBLE_CHECKOUT_CALL_SINGLE_FILE = args['possible_checkout_call_single_files']
    POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY = args['possible_checkout_call_yourself_only']
    AMBIENT_SOUNDS = args['ambient_sounds']
    AMBIENT_SOUNDS_AFTER_CALLS = args['ambient_sounds_after_calls']
    DOWNLOADS = args['downloads']
    DOWNLOADS_LANGUAGE = args['downloads_language']
    if DOWNLOADS_LANGUAGE < 0: DOWNLOADS_LANGUAGE = DEFAULT_DOWNLOADS_LANGUAGE
    DOWNLOADS_LIMIT = args['downloads_limit']
    if DOWNLOADS_LIMIT < 0: DOWNLOADS_LIMIT = DEFAULT_DOWNLOADS_LIMIT
    DOWNLOADS_PATH = DEFAULT_DOWNLOADS_PATH
    DOWNLOADS_NAME = args['downloads_name']
    if args['blacklist_path'] != DEFAULT_EMPTY_PATH:
        BLACKLIST_PATH = Path(args['blacklist_path'])
    else:
        BLACKLIST_PATH = DEFAULT_EMPTY_PATH
    BACKGROUND_AUDIO_VOLUME = args['background_audio_volume']
    WEB = args['web_caller']
    WEB_SCOREBOARD = args['web_caller_scoreboard']
    WEB_PORT = args['web_caller_port']
    WEB_DISABLE_HTTPS = args['web_caller_disable_https']
    HOST_PORT = args['host_port']
    DEBUG = args['debug']
    CERT_CHECK = args['cert_check']
    MIXER_FREQUENCY = args['mixer_frequency']
    MIXER_SIZE = args['mixer_size']
    MIXER_CHANNELS = args['mixer_channels']
    MIXER_BUFFERSIZE = args['mixer_buffersize']

    config = CallerConfiguration(
                VERSION = VERSION,
                AUTODART_USER_EMAIL = AUTODART_USER_EMAIL,
                AUTODART_USER_PASSWORD = AUTODART_USER_PASSWORD,
                AUTODART_USER_BOARD_ID = AUTODART_USER_BOARD_ID,
                AUDIO_MEDIA_PATH = AUDIO_MEDIA_PATH,
                AUDIO_MEDIA_PATH_SHARED = AUDIO_MEDIA_PATH_SHARED,
                BLACKLIST_PATH = BLACKLIST_PATH,
                CALLER_VOLUME = AUDIO_CALLER_VOLUME,
                CALLER = CALLER,
                RANDOM_CALLER = RANDOM_CALLER,
                RANDOM_CALLER_EACH_LEG = RANDOM_CALLER_EACH_LEG,
                RANDOM_CALLER_LANGUAGE = RANDOM_CALLER_LANGUAGE,
                RANDOM_CALLER_GENDER = RANDOM_CALLER_GENDER,
                CALL_CURRENT_PLAYER = CALL_CURRENT_PLAYER,
                CALL_CURRENT_PLAYER_ALWAYS = CALL_CURRENT_PLAYER_ALWAYS,
                CALL_EVERY_DART = CALL_EVERY_DART,
                CALL_EVERY_DART_SINGLE_FILE = CALL_EVERY_DART_SINGLE_FILE,
                POSSIBLE_CHECKOUT_CALL = POSSIBLE_CHECKOUT_CALL,
                POSSIBLE_CHECKOUT_CALL_SINGLE_FILE = POSSIBLE_CHECKOUT_CALL_SINGLE_FILE,
                POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY = POSSIBLE_CHECKOUT_CALL_YOURSELF_ONLY,
                AMBIENT_SOUNDS = AMBIENT_SOUNDS,
                AMBIENT_SOUNDS_AFTER_CALLS = AMBIENT_SOUNDS_AFTER_CALLS,
                DOWNLOADS = DOWNLOADS,
                DOWNLOADS_LIMIT = DOWNLOADS_LIMIT,
                DOWNLOADS_LANGUAGE = DOWNLOADS_LANGUAGE,
                DOWNLOADS_NAME = DOWNLOADS_NAME,
                BACKGROUND_AUDIO_VOLUME = BACKGROUND_AUDIO_VOLUME,
                WEB_CALLER = WEB,
                WEB_CALLER_SCOREBOARD = WEB_SCOREBOARD,
                WEB_CALLER_PORT = WEB_PORT,
                WEB_CALLER_DISABLE_HTTPS = WEB_DISABLE_HTTPS,
                HOST_PORT = HOST_PORT,
                CERT_CHECK = CERT_CHECK,
                MIXER_FREQUENCY = MIXER_FREQUENCY,
                MIXER_SIZE = MIXER_SIZE,
                MIXER_CHANNELS = MIXER_CHANNELS,
                MIXER_BUFFERSIZE = MIXER_BUFFERSIZE,
                DOWNLOADS_PATH = DOWNLOADS_PATH,
                CALLERS_BANNED_FILE = DEFAULT_CALLERS_BANNED_FILE,
                HOST_IP = DEFAULT_HOST_IP,
                DEBUG = DEBUG
    )

    
    
    global server
    server = None

    global boardManagerAddress
    boardManagerAddress = None

    global lastMessage
    lastMessage = None

    global lastCorrectThrow
    lastCorrectThrow = None

    global currentMatch
    currentMatch = None

    global currentMatchPlayers
    currentMatchPlayers = []

    global currentMatchHost
    currentMatchHost = None

    global caller
    caller = None

    global caller_title
    caller_title = ''

    global caller_title_without_version
    caller_title_without_version = ''

    global caller_profiles_banned
    caller_profiles_banned = []

    global lastPoints
    lastPoints = None

    global isGameFinished
    isGameFinished = False

    global background_audios
    background_audios = None

    global mirror_files
    mirror_files = []

    global checkoutsCounter
    checkoutsCounter = {}

    global webCallerSyncs
    webCallerSyncs = {}

    global lobbyPlayers
    lobbyPlayers = []



    osType = plat
    osName = os.name
    osRelease = platform.release()
    ppi('\r\n', None, '')
    ppi('##########################################', None, '')
    ppi('       WELCOME TO AUTODARTS-CALLER', None, '')
    ppi('##########################################', None, '')
    ppi('VERSION: ' + VERSION, None, '')
    ppi('RUNNING OS: ' + osType + ' | ' + osName + ' | ' + osRelease, None, '')
    ppi('SUPPORTED GAME-VARIANTS: ' + " ".join(str(x) for x in SUPPORTED_GAME_VARIANTS), None, '')
    ppi('DONATION: bitcoin:bc1q8dcva098rrrq2uqhv38rj5hayzrqywhudvrmxa', None, '')
    ppi('\r\n', None, '')

    if WEB_DISABLE_HTTPS == False:
        if CERT_CHECK:
            ssl._create_default_https_context = ssl.create_default_context
        else:
            ssl._create_default_https_context = ssl._create_unverified_context
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            ppi("WARNING: SSL-cert-verification disabled!")

    if WEB == 0 or WEB == 2:
        try:
            mixer.pre_init(MIXER_FREQUENCY, MIXER_SIZE, MIXER_CHANNELS, MIXER_BUFFERSIZE)
            mixer.init()
        except Exception as e:
            WEB = 1
            ppe("Failed to initialize audio device! Make sure the target device is connected and configured as os default. Fallback to web-caller", e)
            # sys.exit()  

    path_status = check_paths(__file__, AUDIO_MEDIA_PATH, AUDIO_MEDIA_PATH_SHARED, BLACKLIST_PATH)
    if path_status is not None: 
        ppi('Please check your arguments: ' + path_status)
        sys.exit()  
    
    background_audio = BackgroundAudio(BACKGROUND_AUDIO_VOLUME)
    
    try:
        load_callers_banned(preview = True)
        download_callers(config)
    except Exception as e:
        ppe("Voice-pack fetching failed!", e)

    try:
        setup_caller()
        if caller == None:
            ppi('A caller with name "' + str(CALLER) + '" does NOT exist! Please compare your input with list of available voice-packs.')
            sys.exit()  
    except Exception as e:
        ppe("Setup caller failed!", e)
        sys.exit()  

    try:  
        path_to_crt = None
        path_to_key = None
        ssl_context = None
        if WEB_DISABLE_HTTPS == False:
            path_to_crt = os.path.join(AUDIO_MEDIA_PATH, "dummy.crt")
            path_to_key = os.path.join(AUDIO_MEDIA_PATH, "dummy.key")
            if os.path.exists(path_to_crt) and os.path.exists(path_to_key):
                ssl_context = (path_to_crt, path_to_key)
            else:
                ssl_context = make_ssl_devcert(str(AUDIO_MEDIA_PATH / "dummy"), host=DEFAULT_HOST_IP)

        CallerServer = CallerServer( DEFAULT_HOST_IP, HOST_PORT, path_to_key, path_to_crt, config)

        if WEB > 0 or WEB_SCOREBOARD:
            web_caller = WebCaller('autodarts-caller', DEFAULT_HOST_IP, WEB_PORT, ssl_context, config)

        CallerServer.connect_autodarts()

        CallerServer.websocket_server_thread.join()

        if WEB > 0 or WEB_SCOREBOARD:
            web_caller.flask_app_thread.join() 

        config.keyCloakClient.stop()

    except Exception as e:
        ppe("Connect failed: ", e)