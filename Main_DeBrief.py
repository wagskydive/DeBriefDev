
import os
import glob2
from os import listdir
from os.path import isfile, join
import subprocess
import sys
import threading
import _thread
import subprocess
import shutil
import numpy as np

import random

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from omxplayer import OMXPlayer
from omxplayer.keys import *

import time
from time import sleep

from kivy.app import App
from kivy.graphics import *
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

Builder.load_file("Main_GuiLayout.kv")

running = True




##### Check For Media #####
MediaPresent = False



##### GLOBAL VARIABLES #####

homedirectory = "/home/pi/Documents/deBrief_button_concept/"

# >>>>Prerec and postrec only for creating subclips<<<<<
# prerec is the time before the playhead postrec after playhead
prerec = 4
postrec = 12
subcliplenght = prerec+postrec

globalfilename = 'Skydive_Spain_'

setinpressed = False
setoutpressed = False

argsomx = ['--display=5','--loop', '--orientation=0', '-b']      

omxisplaying = False

fastseekamount = 8

###### OMX PLAYER CLASS #####

class InitOMX():

  def __init__(self, path):
    subprocess.call('sudo killall omxplayer.bin', shell=True)
    self.path = path
    global filepath; filepath = self.path
    global omx; omx = OMXPlayer(self.path, args=argsomx)
    omx.set_aspect_mode('stretch')
    #if omx.playback_status == 'Playing' or omx.playback_status == 'Paused':
    global omxisplaying; omxisplaying = True
    

class InsertMedia():
  
  def __init__(self):
    medialist = len(os.listdir('/media/usb0'))
    while medialist < 1:
      medialist = len(os.listdir('/media/usb0'))
      global MediaPresent; MediaPresent = False
      #return bool(medialist)
      print (medialist, MediaPresent)
      #return False
      time.sleep(.5)
     
    while medialist > 0:
      medialist = len(os.listdir('/media/usb0'))
      global MediaPresent; MediaPresent = True
      print (medialist, MediaPresent)
      #return True
      time.sleep(.5)

screentogoto = "filechooserscreen"


class CheckForMedia(Widget):

  dowehavemedia = NumericProperty(0)
  
  def update(self, *args):
    medialist = len(os.listdir('/dev/disk/by-uuid'))

    if medialist < 3:
      #global screentogoto; screentogoto = "filechooserscreen"
      self.ids._screen_manager.current = "filechooserscreen"
    else:
      #global screentogoto; screentogoto = 'insertmediascreen'
      self.ids._screen_manager.current = 'insertmediascreen'

def FFMpeg_makedaytape(files, path):
  add_string = 'file '
  list_for_conc_txt = [add_string+path+x for x in files]
  print (list_for_conc_txt)
  temp_edl = (path+'temp_edl.txt')
  with open(temp_edl, mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(list_for_conc_txt))
  subprocess.call('ffmpeg -f concat -safe 0 -i '+temp_edl+' -c copy '+path+'___testfile.mp4', shell=True)





class DeBiefPlayer(BoxLayout):

  medialist = len(os.listdir('/dev/disk/by-uuid'))

  active_screen = StringProperty()
  newestfile = StringProperty()
  progressbarvalue = NumericProperty()
  Progressbar = ObjectProperty(None)
  inputDisplay = CheckForMedia()


    



  def updateusb(self):
    devices = len(os.listdir('/dev/disk/by-uuid'))
    screen1 = "filechooserscreen"
    screen2 = 'insertmediascreen'
    if devices > 2:
      #global screentogoto; screentogoto = "filechooserscreen"
      print (screen1)
      active_screen = screen1
      self.ids._screen_manager.current = "filechooserscreen"
    else:
      #global screentogoto; screentogoto = 'insertmediascreen'
      print (screen2)
      active_screen = screen2
      self.ids._screen_manager.current = 'insertmediascreen'

  def changescreen(self):
    devices = len(os.listdir('/dev/disk/by-uuid'))

    if devices > 2:
      #global screentogoto; screentogoto = "filechooserscreen"
      #self.ids._screen_manager.current = "filechooserscreen"
      InsertMediaButton_Press()
    else:
      #global screentogoto; screentogoto = 'insertmediascreen'
      self.ids._screen_manager.current = 'insertmediascreen'


    
    


    
    


  
  def get_newest_file(self):
    medialist = len(os.listdir('/dev/disk/by-uuid'))

    if medialist > 2:
      self.newestfile = str(max(glob2.glob('/media/**/*.[MmaA][pPvtTOo][4sSiIVv]'), key=os.path.getmtime))

      print (newestfile)

    else:
      self.newestfile = '/home/pi/Documents/deBrief_button_concept/KivyDevNaMac/GOPR9571.MP4'
      

  
  global MediaPresent
  
  ismediapresent = BooleanProperty(MediaPresent)
  print ('medialist variable is: '+str(medialist))



  def InsertMediaButton_Press(self):
    #self.ids.filechoosermain._update_files()
    print ('InsertMediaButton is pressed')
    filetoplay = '/home/pi/Documents/deBrief_button_concept/KivyDevNaMac/GOPR9571.MP4'
    if MediaPresent == True:
      filetoplay = max(glob2.glob('/media/**/*.[MmaA][pPvtTOo][4sSiIVv]'), key=os.path.getmtime)
    self.newestfile = os.path.dirname(filetoplay)
    self.ids._screen_manager.current = "filechooserscreen"

    InitOMX(filetoplay)

  def changedir(self):
    print ('Changedir button is pressed')   
    self.newestfile = homedirectory


  def QuitNowButton_Press(self):
    subprocess.call('sudo killall omxplayer.bin', shell=True)
    sys.exit()

    
######## - LEFT BOX - ########

  def SaveClipButton_Press(self):
      print ('Save Clip button is pressed')
      if omxisplaying == True:
        ### "save small clip" ####
        position = omx.position()
        if (setinpressed is True and setoutpressed is True):
          clipstart = str(inpoint)
          cliplenght = str(outpoint-inpoint) 
        else:
          clipstart = str(position-prerec)
          cliplenght = str(subcliplenght)        
        day = str(time.strftime("%Y/%m/%d/"))
        timestamp = str(time.strftime("%H%M%S"))
        filepath_input = str(filepath)
        filepath_output = str(homedirectory+day)
        if not os.path.exists(filepath_output):
                os.makedirs(filepath_output)
        global daydir; daydir = filepath_output
        command = str("ffmpeg -i "+filepath_input+" -ss "+clipstart+" -t "+cliplenght+" -vcodec copy -an "+filepath_output+globalfilename+timestamp+".mp4")
        subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

        global setinpressed; setinpressed = False
        global setoutpressed; setoutpressed = False

      
  def SetInButton_Press(self):
      print ('set IN button is pressed')
      if omxisplaying == True:
        global setinpressed; setinpressed = True
        global inpoint; inpoint = omx.position()
        print (setinpressed)
      
  def SetOutButton_Press(self):
      print ('set OUT button is pressed')
      if omxisplaying == True:
        global setoutpressed; setoutpressed = True
        global outpoint; outpoint = omx.position()
        print (setoutpressed)
    
######## - RIGHT BOX - ########
  def EjectButton_Press(self):
    print ('Eject button is pressed')
    subprocess.call('sudo killall omxplayer.bin', shell=True)
    global omxisplaying; omxisplaying = False
    usbtoeject = os.listdir('/media/pi')
    #print (usbtoeject[0])
    #print ('sudo eject /media/pi/'+usbtoeject[1])
    try:
    
      subprocess.call('sudo eject /media/pi/'+usbtoeject[0], shell=True)
    except IndexError as exception:
      #Handle exception
      pass
    else:
      pass
      
  def SaveStillButton_Press(self):
      print ('Save Still button is pressed')
      if omxisplaying == True:
        position = str(omx.position())
        print (position)
        day = str(time.strftime("%Y/%m/%d/"))
        timestamp = str(time.strftime("%H%M%S"))
        filepath_input = str(filepath)
        filepath_output = str(homedirectory+day)
        if not os.path.exists(filepath_output):
          os.makedirs(filepath_output)
        global daydir; daydir = filepath_output
        command = str('ffmpeg -ss '+position+' -i '+filepath_input+' -vframes 1 '+filepath_output+globalfilename+timestamp+'.jpg')
        subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

        
  def BrowseMediaButton_Press(self):
      print ('Browse button is pressed')

##  def FFMpeg_makedaytape(files, path):
##    add_string = 'file '
##    list_for_conc_txt = [add_string+path+x for x in files]
##    print (list_for_conc_txt)



  def MakeDayTapeButton_Press(self):
    day = str(time.strftime("%Y/%m/%d/"))
    timestamp = str(time.strftime("%H%M%S"))
    filepath_input = str(filepath)
    filepath_output = str(homedirectory+day)
    if not os.path.exists(filepath_output):
      os.makedirs(filepath_output)
    files = os.listdir(filepath_output)
    print (files)
    filesrandom = random.sample(files, len(files))
    print ('random after this')

    print (filesrandom)
    print ('added after this')
    FFMpeg_makedaytape(filesrandom, filepath_output)

    
  def BrowseServerButton_Press(self):
      print ('Browse Server button is pressed')

  def RotateViewFile_press(self):
    print ('rotate view file button is pressed')
    if omxisplaying == True:
      playingfile = omx.get_source()
      playingposition = omx.position()
      
      global argsomx
      if argsomx[2] == '--orientation=0':
        argsomx[2] = '--orientation=180'
      else:
        argsomx[2] = '--orientation=0'
      InitOMX(playingfile)
      time.sleep(.1)
      omx.set_position(playingposition)

###### fileChooser in main player screen #####


      
  def FileSelected_press(self):
    print ('File selected')
    filetoplay = self.ids.filechoosermain.selection
    global filepath; filepath = filetoplay[0]
    InitOMX(filetoplay[0])

 ##### SLIDER MOVE ######

  def Progressbar_Move(self):
#        Progressbar = ObjectProperty(None)
      
      val = self.ids.Progressbar.value
      print ('slider is moved to: '+str(val))

  def Progressbar_Up(self):
      val = self.ids.Progressbar.value
      print ('slider is up at: '+str(val))

 ##### BOX BOTTOM PART PLAY BUTTONS ######

  def PlayPrevFileButton_Press(self):
      print ('Play Previous File Button Pressed')
      if omxisplaying == True:
        pass
  def SeekBackFastButton_Press(self):
    print ('Seek Backward Fast Button Pressed')
    if omxisplaying == True:
      playing = omx.is_playing()
      omx.set_position(omx.position()-fastseekamount)
      if playing is False:
        time.sleep(.1)
        omx.action(23)

  def SeekBackMediumButton_Press(self):
    print ('Seek Forward Medium Button Pressed')
    if omxisplaying == True:
      timeleft = omx.duration()-omx.position()
      if timeleft > fastseekamount:
        playing = omx.is_playing()
        omx.set_position(omx.position()-(fastseekamount/2))
        if playing is False:
          time.sleep(.1)
          omx.action(23)

      
  def SeekBackSlowButton_Press(self):
    print ('Seek Backwards Slow Button Pressed')
    if omxisplaying == True:
      playing = omx.is_playing()
      omx.set_position(omx.position()-.2)
      if playing is False:
        time.sleep(.1)
        omx.action(23)
      else:
        omx.pause()
        time.sleep(.1)
        omx.action(23)
        
   
  def PlaySlowerButton_Press(self):
    print ('Play Slower Button Pressed')
    if omxisplaying == True:
      omx.play_pause()
  
  def PlayFasterButton_Press(self):
    print ('Play Faster Button Pressed')
    if omxisplaying == True:
      omx.play_pause()
  
  def PlayPauseButton_Press(self):
    print ('Play Pause Button Pressed')
    if omxisplaying == True:
      omx.play_pause()
      
  def SeekForwSlowButton_Press(self):
    print ('Seek Forward Slow Button Pressed')
    if omxisplaying == True:
      omx.pause()
      omx.action(23)
      
     
  def SeekForwMediumButton_Press(self):
    print ('Seek Forward Medium Button Pressed')
    if omxisplaying == True:
      timeleft = omx.duration()-omx.position()
      if timeleft > fastseekamount:
        playing = omx.is_playing()
        omx.set_position(omx.position()+(fastseekamount/2))
        if playing is False:
          time.sleep(.1)
          omx.action(23)


  def SeekForwFastButton_Press(self):
    print ('Seek Forward Fast Button Pressed')
    if omxisplaying == True:
      timeleft = omx.duration()-omx.position()
      if timeleft > fastseekamount:
        playing = omx.is_playing()
        omx.set_position(omx.position()+fastseekamount)
        if playing is False:
          time.sleep(.1)
          omx.action(23)


  def PlayNextFileButton_Press(self):
    print ('Play Next File Button Pressed')
    if omxisplaying == True:
      pass
      #omx.action(5)
      

class PlayerDeBriefApp(App):

  def build(self):
      return DeBiefPlayer()
##
##
##  def __init__(self):
##    if MediaPresent == True:
##      DeBiefPlayer().ids._screen_manager.current = "filechooserscreen"
##    else:
##      DeBiefPlayer().ids._screen_manager.current = 'insertmediascreen'
    
   
##Clock.schedule_interval(

if __name__== "__main__":

  _thread.start_new_thread( InsertMedia, () )

  PlayerDeBriefApp().run()

        
