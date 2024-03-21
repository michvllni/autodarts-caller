from utils import versionize_speaker,ppi,ppe
import os
import shutil
from download import download
import csv
import re
import random

from defaults import DEFAULT_EMPTY_PATH,DEFAULT_DOWNLOADS_NAME,DEFAULT_CALLER,DEFAULT_CALLERS_BANNED_FILE
from globals import CALLER_PROFILES,TEMPLATE_FILE_ENCODING,SUPPORTED_SOUND_FORMATS,CALLER_LANGUAGES,CALLER_GENDERS
from sound import play_sound_effect,mirror_sounds
from caller_configuration import CallerConfiguration

def download_callers(config:CallerConfiguration): 

    if config.DOWNLOADS:
        download_list = CALLER_PROFILES

        # versionize, exclude bans, force download-name
        dl_name = config.DOWNLOADS_NAME
        if dl_name is not None:
            dl_name = dl_name.lower()
    
        downloads_filtered = {}
        for speaker_name, (speaker_download_url, speaker_version) in download_list.items():
            spn = speaker_name.lower()

            speaker_versionized = versionize_speaker(speaker_name, speaker_version)
            speaker_versionized_lower = speaker_versionized.lower()

            if dl_name == spn or dl_name == speaker_versionized.lower():
                downloads_filtered = {}   
                downloads_filtered[speaker_versionized] = speaker_download_url
                break

            if speaker_versionized_lower not in caller_profiles_banned and spn not in caller_profiles_banned:  
                # ppi("spn: " + spn)
                # ppi("dl_name: " + dl_name)
                # ppi("speaker_versionized: " + speaker_versionized.lower())
                downloads_filtered[speaker_versionized] = speaker_download_url

        download_list = downloads_filtered

        
        if dl_name != DEFAULT_DOWNLOADS_NAME:
            ppi("Downloader: filter for name: " + str(dl_name))
        else:
            # filter for language
            if config.DOWNLOADS_LANGUAGE > 0:
                ppi("Downloader: filter for language: " + str(config.DOWNLOADS_LANGUAGE))
                downloads_filtered = {}
                for speaker_name, speaker_download_url in download_list.items():
                    caller_language_key = grab_caller_language(speaker_name)
                    if caller_language_key != config.DOWNLOADS_LANGUAGE:
                        continue
                    downloads_filtered[speaker_name] = speaker_download_url
                download_list = downloads_filtered

            # filter for limit
            if config.DOWNLOADS_LIMIT > 0 and len(download_list) > 0 and config.DOWNLOADS_LIMIT < len(download_list):
                ppi("Downloader: limit to: " + str(config.DOWNLOADS_LIMIT))
                download_list = {k: download_list[k] for k in list(download_list.keys())[config.DOWNLOADS_LIMIT:]}



        if len(download_list) > 0:
            if os.path.exists(config.AUDIO_MEDIA_PATH) == False: os.mkdir(config.AUDIO_MEDIA_PATH)

        # Download and parse every caller-profile
        for cpr_name, cpr_download_url in download_list.items():
            try:
                
                # Check if caller-profile already present in users media-directory, yes ? -> stop for this caller-profile
                caller_profile_exists = os.path.exists(os.path.join(config.AUDIO_MEDIA_PATH, cpr_name))
                if caller_profile_exists == True:
                    # ppi('Caller-profile ' + cpr_name + ' already exists -> Skipping download')
                    continue

                # ppi("DOWNLOADING voice-pack: " + cpr_name + " ..")

                # clean download-area!
                shutil.rmtree(config.DOWNLOADS_PATH, ignore_errors=True)
                if os.path.exists(config.DOWNLOADS_PATH) == False: 
                    os.mkdir(config.DOWNLOADS_PATH)
                
                # Download caller-profile and extract archive
                dest = os.path.join(config.DOWNLOADS_PATH, 'download.zip')

                # kind="zip", 
                path = download(cpr_download_url, dest, progressbar=True, replace=False, timeout=15.0, verbose=config.DEBUG)
                # LOCAL-Download
                # shutil.copyfile('C:\\Users\\Luca\\Desktop\\download.zip', os.path.join(DOWNLOADS_PATH, 'download.zip'))

                ppi("Extracting voice-pack..")

                shutil.unpack_archive(dest, config.DOWNLOADS_PATH)
                os.remove(dest)
        
                # Find sound-file-archive und extract it
                zip_filename = [f for f in os.listdir(config.DOWNLOADS_PATH) if f.endswith('.zip')][0]
                dest = os.path.join(config.DOWNLOADS_PATH, zip_filename)
                shutil.unpack_archive(dest, config.DOWNLOADS_PATH)
                os.remove(dest)

                # Find folder and rename it properly
                sound_folder = [dirs for root, dirs, files in sorted(os.walk(config.DOWNLOADS_PATH))][0][0]
                src = os.path.join(config.DOWNLOADS_PATH, sound_folder)
                dest = os.path.splitext(dest)[0]
                os.rename(src, dest)

                # Find template-file and parse it
                template_file = [f for f in os.listdir(config.DOWNLOADS_PATH) if f.endswith('.csv')][0]
                template_file = os.path.join(config.DOWNLOADS_PATH, template_file)
                san_list = list()
                with open(template_file, 'r', encoding=TEMPLATE_FILE_ENCODING) as f:
                    tts = list(csv.reader(f, delimiter=';'))
                    for event in tts:
                        sanitized = list(filter(None, event))
                        if len(sanitized) == 1:
                            sanitized.append(sanitized[0].lower())
                        san_list.append(sanitized)
                    # ppi(san_list)

                # Find origin-file
                origin_file = None
                files = [f for f in os.listdir(config.DOWNLOADS_PATH) if f.endswith('.txt')]
                if len(files) >= 1:
                    origin_file = os.path.join(config.DOWNLOADS_PATH, files[0])

                # Move template- and origin-file to sound-dir
                if origin_file != None:
                    shutil.move(origin_file, dest)
                shutil.move(template_file, dest)   

                # Find all supported sound-files and remember names 
                sounds = []
                for root, dirs, files in os.walk(dest):
                    for file in sorted(files):
                        if file.endswith(tuple(SUPPORTED_SOUND_FORMATS)):
                            sounds.append(os.path.join(root, file))
                # ppi(sounds)

                # Rename sound-files and copy files according the defined caller-keys
                for i in range(len(san_list)):
                    current_sound = sounds[i]
                    current_sound_splitted = os.path.splitext(current_sound)
                    current_sound_extension = current_sound_splitted[1]

                    try:
                        row = san_list[i]
                        caller_keys = row[1:]
                        # ppi(caller_keys)

                        for ck in caller_keys:
                            multiple_file_name = os.path.join(dest, ck + current_sound_extension)
                            exists = os.path.exists(multiple_file_name)
                            # ppi('Test existance: ' + multiple_file_name)

                            counter = 0
                            while exists == True:
                                counter = counter + 1
                                multiple_file_name = os.path.join(dest, ck + '+' + str(counter) + current_sound_extension)
                                exists = os.path.exists(multiple_file_name)
                                # ppi('Test (' + str(counter) + ') existance: ' + multiple_file_name)

                            shutil.copyfile(current_sound, multiple_file_name)
                    except Exception as ie:
                        ppe('Failed to process entry "' + row[0] + '"', ie)
                    finally:
                        os.remove(current_sound)

                shutil.move(dest, config.AUDIO_MEDIA_PATH)
                ppi('Voice-pack added: ' + cpr_name)

            except Exception as e:
                ppe('Failed to process voice-pack: ' + cpr_name, e)
            finally:
                shutil.rmtree(config.DOWNLOADS_PATH, ignore_errors=True)

def ban_caller(CALLER,only_change,BLACKLIST_PATH):
    global caller_title
    # ban/change not possible as caller is specified by user or current caller is 'None'
    if (CALLER != DEFAULT_CALLER and CALLER != '' and caller_title != '' and caller_title != None):
        return
    
    if only_change:
        ccc_success = play_sound_effect('control_change_caller', wait_for_last = False, volume_mult = 1.0, mod = False)
        if not ccc_success:
            play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)
        
    else:
        cbc_success = play_sound_effect('control_ban_caller', wait_for_last = False, volume_mult = 1.0, mod = False)
        if not cbc_success:
            play_sound_effect('control', wait_for_last = False, volume_mult = 1.0, mod = False)

        if BLACKLIST_PATH != DEFAULT_EMPTY_PATH:
            global caller_profiles_banned
            caller_profiles_banned.append(caller_title)
            path_to_callers_banned_file = os.path.join(BLACKLIST_PATH, DEFAULT_CALLERS_BANNED_FILE)   
            with open(path_to_callers_banned_file, 'w') as bcf:
                for cpb in caller_profiles_banned:
                    bcf.write(cpb.lower() + '\n')

    mirror_sounds()
    setup_caller()

    if play_sound_effect('hi', wait_for_last = False):
        mirror_sounds()

def load_callers_banned(preview=False,BLACKLIST_PATH=DEFAULT_EMPTY_PATH):
    global caller_profiles_banned
    caller_profiles_banned = []
    
    if BLACKLIST_PATH == DEFAULT_EMPTY_PATH:
        return
    
    path_to_callers_banned_file = os.path.join(BLACKLIST_PATH, DEFAULT_CALLERS_BANNED_FILE)
    
    if os.path.exists(path_to_callers_banned_file):
        try:
            with open(path_to_callers_banned_file, 'r') as bcf:
                caller_profiles_banned = list(set(line.strip() for line in bcf))
                if preview:
                    banned_info = f"Banned voice-packs: {len(caller_profiles_banned)} [ - "
                    for cpb in caller_profiles_banned:
                        banned_info += cpb + " - "
                    banned_info += "]"
                    ppi(banned_info)
        except FileExistsError:
            pass
    else:
        # directory = os.path.dirname(path_to_callers_banned_file)
        # os.makedirs(directory, exist_ok=True)
        try:
            with open(path_to_callers_banned_file, 'x'):
                ppi(f"'{path_to_callers_banned_file}' created successfully.")
        except Exception as e:
            ppe(f"Failed to create '{path_to_callers_banned_file}'", e)

def load_callers(config:CallerConfiguration):
    # load shared-sounds
    shared_sounds = {}
    if config.AUDIO_MEDIA_PATH_SHARED != DEFAULT_EMPTY_PATH: 
        for root, dirs, files in os.walk(config.AUDIO_MEDIA_PATH_SHARED):
            for filename in files:
                if filename.endswith(tuple(SUPPORTED_SOUND_FORMATS)):
                    full_path = os.path.join(root, filename)
                    base = os.path.splitext(filename)[0]
                    key = base.split('+', 1)[0]
                    if key in shared_sounds:
                        shared_sounds[key].append(full_path)
                    else:
                        shared_sounds[key] = [full_path]

    load_callers_banned()
        
    # load callers
    callers = []
    for root, dirs, files in os.walk(config.AUDIO_MEDIA_PATH):
        file_dict = {}
        for filename in files:
            if filename.endswith(tuple(SUPPORTED_SOUND_FORMATS)):
                full_path = os.path.join(root, filename)
                base = os.path.splitext(filename)[0]
                key = base.split('+', 1)[0]
                if key in file_dict:
                    file_dict[key].append(full_path)
                else:
                    file_dict[key] = [full_path]
        if file_dict:
            callers.append((root, file_dict))
        
    # add shared-sounds to callers
    for ss_k, ss_v in shared_sounds.items():
        for (root, c_keys) in callers:
            if ss_k in c_keys:
                # for sound_variant in ss_v:
                #     c_keys[ss_k].append(sound_variant)
                if config.CALL_EVERY_DART == True and config.CALL_EVERY_DART_SINGLE_FILE == True:
                    c_keys[ss_k] = ss_v
                else:
                    for sound_variant in ss_v:
                        c_keys[ss_k].append(sound_variant)
            else:
                c_keys[ss_k] = ss_v


    return callers

def grab_caller_name(caller_root):
    return os.path.basename(os.path.normpath(caller_root[0])).lower()

def grab_caller_language(caller_name):
    first_occurrences = []
    caller_name = '-' + caller_name + '-'
    for key in CALLER_LANGUAGES:
        for tag in CALLER_LANGUAGES[key]:
            tag_with_dashes = '-' + tag + '-'
            index = caller_name.find(tag_with_dashes)
            if index != -1:  # find returns -1 if the tag is not found
                first_occurrences.append((index, key))

    if not first_occurrences:  # if the list is empty
        return None

    # Sort the list of first occurrences and get the language of the tag that appears first
    first_occurrences.sort(key=lambda x: x[0])
    return first_occurrences[0][1]

def grab_caller_gender(caller_name):
    first_occurrences = []
    caller_name = '-' + caller_name + '-'
    for key in CALLER_GENDERS:
        for tag in CALLER_GENDERS[key]:
            tag_with_dashes = '-' + tag + '-'
            index = caller_name.find(tag_with_dashes)
            if index != -1:  # find returns -1 if the tag is not found
                first_occurrences.append((index, key))

    if not first_occurrences:  # if the list is empty
        return None

    # Sort the list of first occurrences and get the gender of the tag that appears first
    first_occurrences.sort(key=lambda x: x[0])
    return first_occurrences[0][1]

def filter_most_recent_version(path_list):
    def get_last_component(path):
        return os.path.basename(os.path.normpath(path))

    def is_versioned(entry):
        return bool(re.search(r'-v\d+$', entry))

    def highest_version(base_entry):
        versions = [int(re.search(r'-v(\d+)$', x[0]).group(1)) for x in path_list if base_entry + "-v" in x[0]]
        return max(versions, default=None)

    base_entries = set()
    for item in path_list:
        entry = get_last_component(item[0])
        if not is_versioned(entry):
            base_entries.add(entry)

    filtered_list = []
    for item in path_list:
        entry = get_last_component(item[0])
        base_entry = re.sub(r'-v\d+$', '', entry)
        highest_ver = highest_version(base_entry)
        if highest_ver is not None and entry == base_entry + "-v" + str(highest_ver):
            filtered_list.append(item)
        elif highest_ver is None:
            filtered_list.append(item)
    
    return filtered_list

def setup_caller(config:CallerConfiguration):
    global caller
    global caller_title
    global caller_title_without_version
    global caller_profiles_banned
    global server
    
    caller = None
    caller_title = ''
    caller_title_without_version = ''

    callers = load_callers()
    ppi(str(len(callers)) + ' voice-pack(s) found.')

    if config.CALLER != DEFAULT_CALLER and config.CALLER != '':
        wished_caller = config.CALLER.lower()
        for c in callers:
            caller_name = os.path.basename(os.path.normpath(c[0])).lower()
            ppi(caller_name, None, '')
            if caller == None and caller_name == wished_caller:
                caller = c

    else:
        for c in callers: 
            caller_name = grab_caller_name(c)
            ppi(caller_name, None, '')

        if config.RANDOM_CALLER == False:
            caller = callers[0]
        else:
            callers_filtered = []
            for c in callers:
                caller_name = grab_caller_name(c)

                if caller_name in caller_profiles_banned or caller_name.split("-v")[0] in caller_profiles_banned:
                    continue

                if config.RANDOM_CALLER_LANGUAGE != 0:
                    caller_language_key = grab_caller_language(caller_name)
                    if caller_language_key != config.RANDOM_CALLER_LANGUAGE:
                        continue
    
                if config.RANDOM_CALLER_GENDER != 0:
                    caller_gender_key = grab_caller_gender(caller_name)
                    if caller_gender_key != config.RANDOM_CALLER_GENDER:
                        continue
                callers_filtered.append(c)

            if len(callers_filtered) > 0:
                # reduce to most recent version
                callers_filtered = filter_most_recent_version(callers_filtered)
                caller = random.choice(callers_filtered)

    if(caller != None):
        for sound_file_key, sound_file_values in caller[1].items():
            sound_list = list()
            for sound_file_path in sound_file_values:
                sound_list.append(sound_file_path)
            caller[1][sound_file_key] = sound_list

        caller_title = str(os.path.basename(os.path.normpath(caller[0])))
        caller_title_without_version = caller_title.split("-v")[0].lower()
        ppi("Your current caller: " + caller_title + " knows " + str(len(caller[1].values())) + " Sound-file-key(s)")
        # ppi(caller[1])
        caller = caller[1]


        # files = []
        # for key, value in caller.items():
        #     for sound_file in value:
        #         files.append(quote(sound_file, safe=""))
        # get_event = {
        #     "event": "get",
        #     "caller": caller_title_without_version,
        #     "files": files
        # }
        # if server != None:
        #   broadcast(get_event)

        welcome_event = {
            "event": "welcome",
            "caller": caller_title_without_version,
            "specific": config.CALLER != DEFAULT_CALLER and config.CALLER != '',
            "banable": config.BLACKLIST_PATH != DEFAULT_EMPTY_PATH
        }
        if server != None:
            broadcast(welcome_event)
