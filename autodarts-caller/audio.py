import threading
import time
from utils import ppe
import platform
from pygame import mixer

plat = platform.system()
if plat == 'Windows':
    from pycaw.pycaw import AudioUtilities


class BackgroundAudio:
  background_audios: list = []
  audio_muter: threading.Thread = None
  def __init__(self,BACKGROUND_AUDIO_VOLUME):
    if BACKGROUND_AUDIO_VOLUME > 0.0:
        try:
            self.background_audios = AudioUtilities.GetAllSessions()
            self.audio_muter = threading.Thread(target=self.mute_background, args=[BACKGROUND_AUDIO_VOLUME])
            self.audio_muter.start()
        except Exception as e:
            ppe("Background-Muter failed!", e)
  def mute_audio_background(self,vol):
      session_fails = 0
      for session in self.background_audios:
          try:
              volume = session.SimpleAudioVolume
              if session.Process and session.Process.name() != "autodarts-caller.exe":
                  volume.SetMasterVolume(vol, None)
          # Exception as e:
          except:
              session_fails += 1
              # ppe('Failed to mute audio-process', e)

      return session_fails

  def unmute_audio_background(self,mute_vol):
      current_master = mute_vol
      steps = 0.1
      wait = 0.1
      while(current_master < 1.0):
          time.sleep(wait)          
          current_master += steps
          for session in self.background_audios:
              try:
                  if session.Process and session.Process.name() != "autodarts-caller.exe":
                      volume = session.SimpleAudioVolume
                      volume.SetMasterVolume(current_master, None)
              #  Exception as e:
              except:
                  continue
                  # ppe('Failed to unmute audio-process', e)
                  
  def mute_background(self,mute_vol):

      muted = False
      waitDefault = 0.1
      waitForMore = 1.0
      wait = waitDefault

      while True:
          time.sleep(wait)
          if mixer.get_busy() == True and muted == False:
              muted = True
              wait = waitForMore
              session_fails = self.mute_audio_background(mute_vol)

              if session_fails >= 3:
                  # ppi('refreshing background audio sessions')
                  self.background_audios = AudioUtilities.GetAllSessions()

          elif self.mixer.get_busy() == False and muted == True:    
              muted = False
              wait = waitDefault
              self.unmute_audio_background(mute_vol)  


