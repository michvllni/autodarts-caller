#!/bin/bash


# -----------------------------------------
# ARGUMENTS
# Please fill out following arguments. There are required ones and optional ones. 
# If you do not want to fill an optional argument just leave it blank after the equal-sign ("=").
# In case you need specific argument explaination visit https://github.com/lbormann/darts-caller#arguments


# REQUIRED:

# -U
autodarts_email=

# -P
autodarts_password=

# -B
autodarts_board_id=

# -M
media_path=





# OPTIONAL:

# -MS
media_path_shared=

# -V
caller_volume=

# -C
caller=

# -R
random_caller=

# -RL
random_caller_language=

# -RG
random_caller_gender=

# -CCP
call_current_player=

# -CBA
call_bot_actions=

# -E
call_every_dart=

# -PCC
possible_checkout_call=

# -PCCYO
possible_checkout_call_yourself_only=

# -A
ambient_sounds=

# -AAC
ambient_sounds_after_calls=

# -DL
downloads=

# -DLLA
downloads_language=

# -DLN
downloads_name=

# -ROVP
remove_old_voice_packs=

# -LPB
local_playback=

# -WEBDH
web_caller_disable_https=

# -HP
host_port=

# -DEB
debug=

# -MIF
mixer_frequency=

# -MIS
mixer_size=

# -MIC
mixer_channels=

# -MIB
mixer_buffersize=













# Only change if it says 'python3 is not a recognized command or something like that - you could use python instead'
py="python3"



# END
# DO NOT CHANGE ANYTHING BY THIS LINE!
# ------------------------------------------

args="-U $autodarts_email -P $autodarts_password -B $autodarts_board_id -M $media_path"
if [ -n "$media_path_shared" ]; then
  args="$args -MS $media_path_shared"
fi
if [ -n "$caller_volume" ]; then
  args="$args -V $caller_volume"
fi
if [ -n "$caller" ]; then
  args="$args -C $caller"
fi
if [ -n "$random_caller" ]; then
  args="$args -R $random_caller"
fi
if [ -n "$random_caller_language" ]; then
  args="$args -RL $random_caller_language"
fi
if [ -n "$random_caller_gender" ]; then
  args="$args -RG $random_caller_gender"
fi
if [ -n "$call_current_player" ]; then
  args="$args -CCP $call_current_player"
fi
if [ -n "$call_bot_actions" ]; then
  args="$args -CBA $call_bot_actions"
fi
if [ -n "$call_every_dart" ]; then
  args="$args -E $call_every_dart"
fi
if [ -n "$possible_checkout_call" ]; then
  args="$args -PCC $possible_checkout_call"
fi
if [ -n "$possible_checkout_call_yourself_only" ]; then
  args="$args -PCCYO $possible_checkout_call_yourself_only"
fi
if [ -n "$ambient_sounds" ]; then
  args="$args -A $ambient_sounds"
fi
if [ -n "$ambient_sounds_after_calls" ]; then
  args="$args -AAC $ambient_sounds_after_calls"
fi
if [ -n "$downloads" ]; then
  args="$args -DL $downloads"
fi
if [ -n "$downloads_language" ]; then
  args="$args -DLLA $downloads_language"
fi
if [ -n "$downloads_name" ]; then
  args="$args -DLN $downloads_name"
fi
if [ -n "$remove_old_voice_packs" ]; then
  args="$args -ROVP $remove_old_voice_packs"
fi
#if [ -n "$background_audio_volume" ]; then
#  args="$args -BAV $background_audio_volume"
#fi
if [ -n "$local_playback" ]; then
  args="$args -LPB $local_playback"
fi
if [ -n "$web_caller_disable_https" ]; then
  args="$args -WEBDH $web_caller_disable_https"
fi
if [ -n "$host_port" ]; then
  args="$args -HP $host_port"
fi
if [ -n "$debug" ]; then
  args="$args -DEB $debug"
fi
if [ -n "$mixer_frequency" ]; then
  args="$args -MIF $mixer_frequency"
fi
if [ -n "$mixer_size" ]; then
  args="$args -MIS $mixer_size"
fi
if [ -n "$mixer_channels" ]; then
  args="$args -MIC $mixer_channels"
fi
if [ -n "$mixer_buffersize" ]; then
  args="$args -MIB $mixer_buffersize"
fi

echo "Arguments: $args"

"$py" darts-caller.py $args
