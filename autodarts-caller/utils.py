import os
import sys
import psutil
from defaults import DEFAULT_EMPTY_PATH

def ppi(message, info_object = None, prefix = '\r\n'):
    global logger
    logger.info(prefix + str(message))
    if info_object != None:
        logger.info(str(info_object))
    
def ppe(message, error_object,DEBUG):
    global logger
    ppi(message)
    if DEBUG:
        logger.exception("\r\n" + str(error_object))

def get_executable_directory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(os.path.realpath(__file__))
    else:
        raise RuntimeError("Unable to determine executable directory.")

def same_drive(path1, path2):
    drive1 = os.path.splitdrive(path1)[0]
    drive2 = os.path.splitdrive(path2)[0]
    return drive1 == drive2

def check_paths(main_directory, audio_media_path, audio_media_path_shared, blacklist_path):
    try:
        main_directory = get_executable_directory()
        errors = None

        audio_media_path = os.path.normpath(audio_media_path)
        
        if audio_media_path_shared != DEFAULT_EMPTY_PATH:
            audio_media_path_shared = os.path.normpath(audio_media_path_shared)
        if blacklist_path != DEFAULT_EMPTY_PATH:
            blacklist_path = os.path.normpath(blacklist_path)

        if same_drive(audio_media_path, main_directory) == True and os.path.commonpath([audio_media_path, main_directory]) == main_directory:
            errors = 'AUDIO_MEDIA_PATH (-M) is a subdirectory of MAIN_DIRECTORY.'

        if audio_media_path_shared != '':
            if same_drive(audio_media_path_shared, main_directory) == True and os.path.commonpath([audio_media_path_shared, main_directory]) == main_directory:
                errors = 'AUDIO_MEDIA_PATH_SHARED (-MS) is a subdirectory of MAIN_DIRECTORY. This is NOT allowed.'
            elif same_drive(audio_media_path_shared, audio_media_path) == True and os.path.commonpath([audio_media_path_shared, audio_media_path]) == audio_media_path:
                errors = 'AUDIO_MEDIA_PATH_SHARED (-MS) is a subdirectory of AUDIO_MEDIA_PATH. This is NOT allowed.'
            elif same_drive(audio_media_path, audio_media_path_shared) == True and os.path.commonpath([audio_media_path, audio_media_path_shared]) == audio_media_path_shared:
                errors = 'AUDIO_MEDIA_PATH (-M) is a subdirectory of AUDIO_MEDIA_SHARED (-MS). This is NOT allowed.'
            elif same_drive(audio_media_path, audio_media_path_shared) == True and audio_media_path == audio_media_path_shared:
                errors = 'AUDIO_MEDIA_PATH (-M) is equal to AUDIO_MEDIA_SHARED (-MS). This is NOT allowed.'

        if blacklist_path != '':
            if same_drive(blacklist_path, main_directory) == True and os.path.commonpath([blacklist_path, main_directory]) == main_directory:
                errors = 'BLACKLIST_FILE_PATH (-BLP) is a subdirectory of MAIN_DIRECTORY. This is NOT allowed.'

    except Exception as e:
        errors = f'Path validation failed: {e}'

    if errors is not None:
        ppi("main_directory: " + main_directory)
        ppi("audio_media_path: " + str(audio_media_path))
        ppi("audio_media_path_shared: " + str(audio_media_path_shared))
        ppi("blacklist_path: " + str(blacklist_path))

    return errors

def check_already_running():
    max_count = 3 # app (binary) uses 2 processes => max is (2 + 1) as this one here counts also.
    count = 0
    me, extension = os.path.splitext(os.path.basename(sys.argv[0]))
    ppi("Process is " + me)
    for proc in psutil.process_iter(['pid', 'name']):
        proc_name = proc.info['name'].lower()
        proc_name, extension = os.path.splitext(proc_name)
        if proc_name == me:
            count += 1
            if count >= max_count:
                ppi(f"{me} is already running. Exit")
                sys.exit()  
    # ppi("Start info: " + str(count))


def versionize_speaker(speaker_name, speaker_version):
    speaker_versionized = speaker_name
    if speaker_version > 1:
        speaker_versionized = f"{speaker_versionized}-v{speaker_version}"
    return speaker_versionized