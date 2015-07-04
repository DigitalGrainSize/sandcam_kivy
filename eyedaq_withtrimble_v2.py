"""
eyedaq_withtrimble.py
program to 
1) view and capture an image of sediment
2) get site info from the user
3) save image to file with the site and time in the file name

Written by:
Daniel Buscombe, Feb-March 2015, updated June 2015
Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
please contact:
dbuscombe@usgs.gov

SYNTAX:
python eyedaq_withtrimble_v2.py

REQUIREMENTS:
python
kivy (http://kivy.org/#home)

"""

from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.gridlayout import GridLayout

from kivy.uix.accordion import *
from kivy.properties import *
from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import WindowBase
from kivy.core.window import Window
from kivy.graphics import Canvas, Translate, Fbo, ClearColor, ClearBuffers

from kivy.clock import Clock
#from kivy.uix.popup import Popup

from numpy import sqrt as sqrt
from numpy import abs as abs
import time, os
from shutil import move as mv

import sys
import textwrap

## pip install kivy-garden
## garden install graph
#from kivy.garden.graph import Graph, MeshLinePlot

from math import cos, sin

import serial

try:
   import fortune
except:
   print "fortune not installed"
   print "pip install fortune"

BAUDRATE2 = 4800

#cs2cs_args = "epsg:26949"
## get the transformation matrix of desired output coordinates
#try:
#   trans =  pyproj.Proj(init=cs2cs_args)
#except:
#   trans =  pyproj.Proj(cs2cs_args)


#=========================
#=========================
def cowsay(str, length=40):
    return build_bubble(str, length) + build_cow()

#=========================
def build_cow():
    return """
         \   ^__^ 
          \  (oo)\_______
             (__)\       )\/\\
                 ||----w |
                 ||     ||
    """

#=========================
def build_bubble(str, length=40):
    bubble = []

    lines = normalize_text(str, length)

    bordersize = len(lines[0])

    bubble.append("  " + "_" * bordersize)

    for index, line in enumerate(lines):
        border = get_border(lines, index)

        bubble.append("%s %s %s" % (border[0], line, border[1]))

    bubble.append("  " + "-" * bordersize)

    return "\n".join(bubble)

#=========================
def normalize_text(str, length):
    lines  = textwrap.wrap(str, length)
    maxlen = len(max(lines, key=len))
    return [ line.ljust(maxlen) for line in lines ]

#=========================
def get_border(lines, index):
    if len(lines) < 2:
        return [ "<", ">" ]

    elif index == 0:
        return [ "/", "\\" ]
    
    elif index == len(lines) - 1:
        return [ "\\", "/" ]
    
    else:
        return [ "|", "|" ]


#=========================
#=========================
def export_to_png(self, filename, *args):
    '''Saves an image of the widget and its children in png format at the
    specified filename. Works by removing the widget canvas from its
    parent, rendering to an :class:`~kivy.graphics.fbo.Fbo`, and calling
    :meth:`~kivy.graphics.texture.Texture.save`.
    '''
 
    if self.parent is not None:
        canvas_parent_index = self.parent.canvas.indexof(self.canvas)
        self.parent.canvas.remove(self.canvas)
 
    fbo = Fbo(size=self.size)
 
    with fbo:
        ClearColor(0, 0, 0, 1)
        ClearBuffers()
        Translate(-self.x, -self.y, 0)
 
    fbo.add(self.canvas)
    fbo.draw()
    fbo.texture.save(filename)
    fbo.remove(self.canvas)
 
    if self.parent is not None:
        self.parent.canvas.insert(canvas_parent_index, self.canvas)
 
    return True 

#=========================

def scan():
    #scan for available ports. return a list of tuples (num, name)
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.name))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available


#=========================
def init_serial(self):

   if os.name=='nt':
       print '==========================='
       print '==========================='
       print '==========================='
       print "Do you have an echosounder attached? Enter y or n only, then enter"   
       temp = raw_input() #waits here for keyboard input
       if temp == 'y':
          #enter your Echosounder COM port number
          print "Echosounder COM port # for echosounder. Enter # only, then enter"
          temp = raw_input() #waits here for keyboard input
          if temp == 'e':
   	     sys.exit()
          comnum2 = 'COM' + temp #concatenate COM and the port number to define serial port
       else:
          self.ser2 = 0
   
   else:
       comnum2 ='/dev/ttyUSB1'             

   try:
     global BAUDRATE2
     self.ser2 = serial.Serial()
     self.ser2.baudrate = BAUDRATE2
     self.ser2.port = comnum2
     self.ser2.timeout = 2
     self.ser2.open()
     if self.ser2.isOpen():
        print '==========================='
        print 'Echosounder is open'
        print '==========================='
        self.echosounderopen = 1
   except:
     self.ser2 = 0
     print '==========================='
     print "Echosounder failed to open"
     print '==========================='   
    
   return self.ser2  


#=========================
def get_depth(self):

    dat = {}
    
    try:
       dat['depth_ft'] = self.ser2.read(1000).split('DBT')[1].split(',f,')[0].split(',')[1]
       dat['depth_m'] = str(float(dat['depth_ft'])*0.3048)
       #print 'got depth'
    except:
       dat['depth_ft'] = 'NaN'
       dat['depth_m'] = 'NaN'    

    return dat
    

#=========================
## kv markup for building the app
Builder.load_file('eyedaq.kv')

#=========================
#=========================
class Log(TextInput):

    def on_double_tap(self):
        # make sure it performs it's original function
        super(Log, self).on_double_tap()

        def on_word_selection(*l):
            selected_word = self.selection_text
            print selected_word
                
        # let the word be selected wait for
        # next frame and get the selected word
        Clock.schedule_once(on_word_selection)
        
        
class CameraWidget(BoxLayout): 

    #=========================
    #def Play(self, *args):
    #    self.ids.camera.play = True
    #    now = time.asctime() #.replace(' ','_')
    #    self.textinput.text += 'Video resumed '+now+'\n'
             
    #=========================   
    #def Pause(self, *args):
    #    self.ids.camera.play = False
    #    now = time.asctime() #.replace(' ','_').replace(':','_')
    #    self.textinput.text += 'Video paused '+now+'\n'

    #=========================
    def TakePicture(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()

        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_sand_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Eyeball image collected'+'\n' #: '+filename+'\n'
        try:
           mv(filename,'eyeballimages') 
        except:
           self.textinput.text += 'ERROR: image could not be stored'

    #=========================    
    def TakePictureMud(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()
              
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_mud_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)  
        self.textinput.text += 'Mud image collected'+'\n' #: '+filename+'\n' 
        try:
           mv(filename,'mudimages')  
        except:
           self.textinput.text += 'ERROR: image could not be stored' 

    #=========================
    def TakePictureGravel(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()
              
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_gravel_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)       
        self.textinput.text += 'Gravel image collected'+'\n' #: '+filename+'\n'
        try: 
           mv(filename,'gravelimages') 
        except:
           self.textinput.text += 'ERROR: image could not be stored'
        
    #=========================
    def TakePictureRock(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()   
    
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_rock_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Rock image collected'+'\n' #: '+filename+'\n'
        try:
           mv(filename,'rockimages') 
        except:
           self.textinput.text += 'ERROR: image could not be stored'
       
    #========================= 
    def TakePictureSandRock(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()
              
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]

        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_sand_rock_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Sand/Rock image collected'+'\n' #: '+filename+'\n'
        try:
           mv(filename,'sandrockimages')    
        except:
           self.textinput.text += 'ERROR: image could not be stored'
      
    #=========================  
    def TakePictureSandGravel(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()
              
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_sand_gravel_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Sand/Gravel image collected'+'\n' #: '+filename+'\n'
        try:
           mv(filename,'sandgravelimages')    
        except:
           self.textinput.text += 'ERROR: image could not be stored'

    #=========================  
    def TakePictureGravelSand(self, *args):
        #if hasattr(self, 'laststationchange') & hasattr(self, 'lastimage'):
        #   #self.textinput.text += 'Elapsed: '+str(abs(self.laststationchange - self.lastimage))+'\n'
        #   if abs(self.laststationchange - self.lastimage) > 30:
        #      content1 = Button(text = 'Close')
        #      popup = Popup(title = 'It has been a while ... consider changing station? ', size_hint = (None, None), size = (400,400), auto_dismiss=True, content = content1)
        #      content1.bind(on_press = popup.dismiss)
        #      popup.open()
              
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        z = self.textinput3.text.split(':')[3].split(',')[0]
        d = self.textinput3.text.split(':')[4].split(',')[0]
        
        if hasattr(self, 'st_n'):
           # distance from station start
           dist = sqrt((float(n)-float(self.st_n))**2 + (float(e)-float(self.st_e))**2)

           if dist > float(self.textinput4.text): #increment station
              self.station_up()

        self.export_to_png = export_to_png

        now = time.asctime().replace(' ','_').replace(':','_')
        self.lastimage = time.clock()
        filename = 'st'+self.txt_inpt.text+'_gravel_sand_'+now+'_e'+e+'_n'+n+'_z'+z+'_d'+d+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Gravel/Sand image collected'+'\n' #: '+filename+'\n'
        try:
           mv(filename,'gravelsandimages')  
        except:
           self.textinput.text += 'ERROR: image could not be stored'  

    #=========================
    def change_st(self):
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'

        self.laststationchange = time.clock()

        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        # make note of current station        
        self.st_e = e
        self.st_n = n

        self.textinput5.text = self.st_e
        self.textinput6.text = self.st_n

        # get the last site visited and add 1, write to station file
        fsite = open('station_start.txt','wb')
        fsite.write(str(int(self.txt_inpt.text)+1)) 
        fsite.close()
        
    #=========================
    def station_up(self):
        self.txt_inpt.text = str(int(self.txt_inpt.text)+1)
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'
        self.laststationchange = time.clock()

        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        # make note of current station
        self.st_e = e
        self.st_n = n
 
        self.textinput5.text = self.st_e
        self.textinput6.text = self.st_n
        
        # get the last site visited and add 1, write to station file
        fsite = open('station_start.txt','wb')
        fsite.write(str(int(self.txt_inpt.text)+1)) 
        fsite.close()
        
    #=========================
    def station_down(self):
        self.txt_inpt.text = str(int(self.txt_inpt.text)-1)
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'
        self.laststationchange = time.clock()
     
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
    
        # make note of current station
        self.st_e = e
        self.st_n = n
        
        self.textinput5.text = self.st_e
        self.textinput6.text = self.st_n
        
        # get the last site visited and add 1, write to station file
        fsite = open('station_start.txt','wb')
        fsite.write(str(int(self.txt_inpt.text)+1)) 
        fsite.close()     
        
    #=========================
    def TakeTimeStamp(self):
        self.textinput.text += 'Time is '+time.asctime()+'\n'                              

    #=========================
    def MarkWaypoint(self):
        self.textinput.text += 'Mark Waypoint at '+time.asctime()+': '+self.textinput3.text 
 

    #=========================
    def starwars(self):
        try:
           self.textinput2.text += cowsay(fortune.get_random_fortune('starwars'))
        except:
           self.textinput2.text += "install fortune"                  

    #=========================
    def fortune(self):
        try:
           self.textinput2.text += cowsay(fortune.get_random_fortune('fortunes'))
        except:
           self.textinput2.text += "install fortune"                  


        pass

#=========================
#=========================
class Eyeball_DAQApp(App):

    #=========================
    def __init__(self, **kwargs):
       super(Eyeball_DAQApp, self).__init__(**kwargs)
       self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
       self._keyboard.bind(on_key_down = self._on_keyboard_down)
       self._keyboard.bind(on_key_up = self._on_keyboard_up)

    #=========================
    def _keyboard_closed(self):
       self._keyboard.unbind(on_key_down = self._on_keyboard_down)
       self._keyboard = None

    #=========================
    def _on_keyboard_down(self, *args):
       print args[1][1]

    #=========================
    def _on_keyboard_up(self, *args):
       print args[1][1]
       #if args[1][1] == 'u':
       
    #=========================
    def _update_pos(self, dt):

        if self.ser2!=0:
           try:
              dat = get_nmea(self)
	      d = dat['depth_m']
	   except:
	      d = 'NaN'
	else:
	   d = 'NaN'
	         	         
        with open('C:\Users\User\Desktop\capture.txt') as f:
          last = f.readline().split('\r')[-2]
   
        f.close()

        last = last.split('99=')[1]

        if ~last.startswith(' '):
           sd = float(last.split(';')[0].lstrip())/1000
           ha = 0.0009*float(last.split(';')[1].lstrip())/10
           va = 0.0009*float(last.split(';')[2].lstrip())/10

        ha = (ha - self.hca) % 360

        Za = va*0.0174532925

        n = self.np + sd * sin(Za) * cos(ha*0.0174532925)
        z = self.zp + sd * cos(Za)
        e = self.ep + sd * sin(Za) * sin(ha*0.0174532925)
        
        # distance to BM
        dist = sqrt((n-self.np)**2 + (e-self.ep)**2)

        if hasattr(self, 'textinput5'):
           try:
              # distance from station start
              dist2 = str(sqrt((float(n)-float(self.textinput6.text))**2 + (float(e)-float(self.textinput5.text))**2))
           except:
              dist2 = ' '

        self.textinput3.text = 'E: '+str(e)+', N: '+str(n)+', Z: '+str(z)+', D: '+str(d)+', Distance to gun: '+str(dist)+', Distance from station: '+dist2+'\n'

        #self.textinput3.text = 'E: '+str(e)+', N: '+str(n)+', Z: '+str(z)+', Distance to gun: '+str(dist)+', Distance from station: '+dist2+'\n'
        
        self.textinput.text += time.asctime() + ' ' +last + '\n'
        

    #=========================
    def _update_time(self, dt):
        self.item.title = 'Current time is '+time.asctime()

    #=========================
    #def _draw_me(self, dt):
    #    e = self.textinput3.text.split(':')[1].split(',')[0]
    #    n = self.textinput3.text.split(':')[2].split(',')[0]
    #    self.plot.points.append((float(e),float(n)))
    #    self.graph.xmax = 5+max(self.plot.points)[0]
    #    self.graph.xmin = min(self.plot.points)[0]-5
    #    self.graph.ymax = 5+max(self.plot.points)[1]
    #    self.graph.ymin = min(self.plot.points)[1]-5

    #    #xmax = random.randint(10, 100)
    #    #self.plot.points = [(x, sin(x / 10.)) for x in range(0, xmax)]
    #    #self.graph.xmax = xmax

    #=========================        
    def build(self):

        self.ser2 = init_serial(self)

        root = Accordion(orientation='horizontal')
        
        self.item = AccordionItem(title='Current time is '+time.asctime())

        image = CameraWidget(size_hint = (2.0, 1.0)) 

        # log
        layout = GridLayout(cols=1)
        self.textinput = Log(text='Data Acquisition Log\n', size_hint = (0.25, 1.5), markup=True)
        layout.add_widget(self.textinput)
        image.textinput = self.textinput
       
        # read nav station positions
        #with open('nav_stat.txt') as f:
        #   dump = f.read()
        #f.close()
        #dump = dump.split('\n')
        #for k in dump:
        #    if k.startswith('e'):
        #       self.ep = float(k.split('=')[1].lstrip())
        #    elif k.startswith('n'):
        #       self.np = float(k.split('=')[1].lstrip())
        #    elif k.startswith('z'):
        #       self.zp = float(k.split('=')[1].lstrip())   
        #    elif k.startswith('hca'):
        #       self.hca = float(k.split('=')[1].lstrip())

        print "============================================"
        print "============================================"
        print "=====NAV STATION SETUP : INPUT REQUIRED====="
        print "============================================"
        print "============================================"
        self.hca = input('Input horizontal correction angle ')
        self.ep = input('Input easting of BM  ')
        self.np = input('Input northing of BM ')
        self.zp = input('Input elevation of BM + height of station ')

        print "============================================"
        print "============================================"
        print "======PROGRAM SETTINGS : INPUT REQUIRED====="
        print "============================================"
        print "============================================"        
   
        self.textinput4 = Log(text=str(input('Distance (m) from present station beyond which station number is updated ')), size_hint = (0, 0), markup=False)
        layout.add_widget(self.textinput4)
        image.textinput4 = self.textinput4        
        
        ## for st_e and st_n
        self.textinput5 = Log(text='', size_hint = (0, 0), markup=False)
        layout.add_widget(self.textinput5)
        image.textinput5 = self.textinput5         

        self.textinput6 = Log(text='', size_hint = (0, 0), markup=False)
        layout.add_widget(self.textinput6)
        image.textinput6 = self.textinput6     
        
        # for map
        #layout.add_widget(Button(text='Map', width=100)) 
        #self.graph = Graph(xlabel='E', ylabel='N', x_ticks_minor=1,
        #x_ticks_major=25, y_ticks_major=10, y_ticks_minor=1,
        #y_grid_label=True, x_grid_label=True, padding=5,
        #x_grid=True, y_grid=True, xmin=self.ep-5, xmax=self.ep+5, ymin=self.np-5, ymax=self.np+5)

        #self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        #self.plot.points = [(self.ep,self.np)]
        #self.graph.add_plot(self.plot)
        #layout.add_widget(self.graph)
        #image.graph1 = self.plot
        
        # for quotes
        self.textinput2 = Log(text='', size_hint = (0.25, 0.75), markup=True)
        layout.add_widget(self.textinput2)
        image.textinput2 = self.textinput2
        
        self.textinput3 = Log(text='\n', size_hint = (0.25, 0.3), markup=True)
        layout.add_widget(self.textinput3)
        image.textinput3 = self.textinput3

        # add image to AccordionItem
        self.item.add_widget(image)
        #item.add_widget(self.textinput)
        self.item.add_widget(layout)
        
        Clock.schedule_interval(self._update_pos, 2)
        Clock.schedule_interval(self._update_time, 1)
        #Clock.schedule_interval(self._draw_me, 2)

        root.add_widget(self.item)
        
        return root

    #=========================
    def on_stop(self):
        # write session log to file
        with open(os.path.expanduser("~")+os.sep+'log_'+time.asctime().replace(' ','_').replace(':','_')+'.txt','wb') as f:
           f.write(self.textinput.text)
        f.close()

        with open('station_start.txt','rb') as f:
           st=str(f.read()).split('\n')[0]
        f.close()

        countmax=22; counter=0
        with open('eyedaq.kv','rb') as oldfile, open('eyedaq_new.kv','wb') as newfile:
           for line in oldfile:
              counter += 1
              if counter==countmax:
                 newfile.write("            text: '"+st+"'\n")
              else:
                 newfile.write(line)
        mv('eyedaq_new.kv','eyedaq.kv')

        # close the serial port
        if self.ser2!=0:
           self.ser2.close()
           print "================="
           print "Echosounder is closed"
           print "================="
           
        ## close the csv results files
        #bedf_csv.close()
        #print "output files closed"

#=========================
#=========================
if __name__ == '__main__':

    try:
       os.mkdir('eyeballimages')
       os.mkdir('gravelimages')
       os.mkdir('rockimages')
       os.mkdir('sandrockimages')
       os.mkdir('sandgravelimages')
    except:
       pass

    Eyeball_DAQApp().run()
    
    
   
