"""
eyedaq_withgps_v2.py
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
python eyedaq_withgps_v2.py

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

import time, os
from shutil import move as mv

import sys
import textwrap

## pip install kivy-garden
## garden install graph
#from kivy.garden.graph import Graph, MeshLinePlot

# following are temporary for the map updating
#from math import cos, sin
#import random

from numpy import sqrt as sqrt
from numpy import abs as abs
##import numpy as np
import pyproj, csv, serial
from pynmea import nmea

try:
   import fortune
except:
   print "fortune not installed"
   print "pip install fortune"


#comnum= 'COM8' #'/dev/ttyUSB0'

#lat = 0
#long = 0
#pos_x = 0
#pos_y = 0
#alt = 0
#i = 0 #x units for altitude measurment
BAUDRATE = 9600
BAUDRATE2 = 4800


cs2cs_args = "epsg:26949"
# get the transformation matrix of desired output coordinates
try:
   trans =  pyproj.Proj(init=cs2cs_args)
except:
   trans =  pyproj.Proj(cs2cs_args)


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
       #opens the serial port based on the COM number you choose
       print '==========================='
       print '==========================='
       print '==========================='
       print "Found Ports:"
       for n,s in scan():
          print "%s" % s
       print " "

       #enter your GPS COM port number
       print '==========================='
       print '==========================='
       print '==========================='
       print "GPS COM port # for GPS. Enter # only, then enter"
       temp = raw_input() #waits here for keyboard input
       if temp == 'e':
   	   sys.exit()
       comnum = 'COM' + temp #concatenate COM and the port number to define serial port
   
   else:
       comnum='/dev/ttyUSB0'

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
     global BAUDRATE
     self.ser = serial.Serial()
     self.ser.baudrate = BAUDRATE
     self.ser.port = comnum
     self.ser.timeout = 0.5
     self.ser.open()
     if self.ser.isOpen():
        print '==========================='
        print 'GPS is open'
        print '==========================='
        self.gpsopen = 1
   except:
     self.ser = 0
     print '==========================='
     print "GPS failed to open"
     print '==========================='
     

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
     
     
   return self.ser, self.ser2  

#=========================
def get_nmea(self):
    gotpos = 0; counter = 0
       
    while (gotpos==0) &(counter<3):
       line = self.ser.read(1000) # read 1000 bytes
       parts = line.split('\r\n') # split by line return

       gpgga_parts = []; gpgsa_parts = [];
       gprmc_parts = []; gpvtg_parts = []; gpgsv_parts = []
       newparts = [] # create new variable which contains cleaned strings
       for k in range(len(parts)):
          if parts[k].startswith('$'): #select if starts with $
             if len(parts[k].split('*'))>1: #select if contains *
                if parts[k].count('$')==1: # select if only contains 1 $
                    newparts.append(parts[k])

       for k in range(len(newparts)):
         if "GPGGA" in newparts[k]:
            gpgga_parts.append(newparts[k])
         elif "GPGSA" in newparts[k]:
            gpgsa_parts.append(newparts[k])                
         elif "GPRMC" in newparts[k]:
            gprmc_parts.append(newparts[k])          
         elif "GPVTG" in newparts[k]:
            gpvtg_parts.append(newparts[k])
         elif "GPGSV" in newparts[k]:
            gpgsv_parts.append(newparts[k])

       if gpgga_parts:
          gotpos=1
          gpgga_parts = gpgga_parts[-1]; 
       if gprmc_parts:
          gprmc_parts = gprmc_parts[-1]; 
       if gpgsa_parts:
          gpgsa_parts = gpgsa_parts[-1]
       if gpvtg_parts:
          gpvtg_parts = gpvtg_parts[-1]
       if gpgsv_parts:
          gpgsv_parts = gpgsv_parts[-1]
                        
       counter += 1
      
    gpgga = nmea.GPGGA(); gpgsa = nmea.GPGSA()
    gprmc = nmea.GPRMC(); gpvtg = nmea.GPVTG(); gpgsv = nmea.GPGSV()

    dat = {}
    
    try:
       dat['depth_ft'] = self.ser2.read(1000).split('DBT')[1].split(',f,')[0].split(',')[1]
       dat['depth_m'] = str(float(dat['depth_ft'])*0.3048)
       #print 'got depth'
    except:
       dat['depth_ft'] = 'NaN'
       dat['depth_m'] = 'NaN'    
    
    # GPGGA
    try:
        gpgga.parse(gpgga_parts)
        lats = gpgga.latitude
        longs= gpgga.longitude
					
        #convert degrees,decimal minutes to decimal degrees 
        lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
        lat = (float(lats[0]+lats[1])+lat1)
        long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
        long = (float(longs[0]+longs[1]+longs[2])+long1)
					
        #calc position
        dat['lat_1'] = str(lat);
        dat['lon_1'] = str(-long)
        #convert to az central state plane east/north
        e,n = trans(-long,lat)
        dat['e_1'] = str(e); dat['n_1'] = str(n)
        
        dat['alt'] = str(gpgga.antenna_altitude)
        dat['t'] = str(gpgga.timestamp);
        dat['qual'] = str(gpgga.gps_qual)
        dat['num_sats'] = str(gpgga.num_sats)
        dat['ref_id'] = str(gpgga.ref_station_id)
        dat['geo_sep'] = str(gpgga.geo_sep)
    except:
        dat['lat_1'] = 'NaN'; dat['lon_1'] = 'NaN'
        dat['alt'] = 'NaN'; dat['t'] = 'NaN'
        dat['qual'] = 'NaN'; dat['num_sats'] = 'NaN'
        dat['ref_id'] = 'NaN'; dat['geo_sep'] = 'NaN'
  
    # GPGSA
    try:
        gpgsa.parse(gpgsa_parts)
        dat['hdop'] = str(gpgsa.hdop); dat['pdop'] = str(gpgsa.pdop); dat['vdop'] = str(gpgsa.vdop)
        dat['mode'] = str(gpgsa.mode); dat['mode_type'] = str(gpgsa.mode_fix_type)
        dat['sv_id01'] = str(gpgsa.sv_id01); dat['sv_id02'] = str(gpgsa.sv_id02)
        dat['sv_id03'] = str(gpgsa.sv_id03); dat['sv_id04'] = str(gpgsa.sv_id04)
        dat['sv_id05'] = str(gpgsa.sv_id05); dat['sv_id06'] = str(gpgsa.sv_id06)
        dat['sv_id07'] = str(gpgsa.sv_id07); dat['sv_id08'] = str(gpgsa.sv_id08)
        dat['sv_id09'] = str(gpgsa.sv_id09); dat['sv_id10'] = str(gpgsa.sv_id10)
        dat['sv_id11'] = str(gpgsa.sv_id11); dat['sv_id12'] = str(gpgsa.sv_id12)    
    except:
        dat['hdop'] = 'NaN'; dat['pdop'] = 'NaN'; dat['vdop'] = 'NaN'
        dat['mode'] = 'NaN'; dat['mode_type'] = 'NaN'
        dat['sv_id01'] = 'NaN'; dat['sv_id02'] = 'NaN'
        dat['sv_id03'] = 'NaN'; dat['sv_id04'] = 'NaN'
        dat['sv_id05'] = 'NaN'; dat['sv_id06'] = 'NaN'
        dat['sv_id07'] = 'NaN'; dat['sv_id08'] = 'NaN'
        dat['sv_id09'] = 'NaN'; dat['sv_id10'] = 'NaN'
        dat['sv_id11'] = 'NaN'; dat['sv_id12'] = 'NaN'
            
    # GPGSV
    try:
        gpgsv.parse(gpgsv_parts)
        dat['az1'] = str(gpgsv.azimuth_1)
        dat['az2'] = str(gpgsv.azimuth_2)
        dat['elev_deg1'] = str(gpgsv.elevation_deg_1)
        dat['elev_deg2'] = str(gpgsv.elevation_deg_2)
        dat['num_sv'] = str(gpgsv.num_sv_in_view)
        dat['snr1'] = str(gpgsv.snr_1)
        dat['snr2'] = str(gpgsv.snr_2)
        dat['sv_prn1'] = str(gpgsv.sv_prn_num_1)
        dat['sv_prn2'] = str(gpgsv.sv_prn_num_2)
    except:
        dat['az1'] = 'NaN'; dat['az2'] = 'NaN'
        dat['elev_deg1'] = 'NaN'; dat['elev_deg2'] = 'NaN'
        dat['num_sv'] = 'NaN'; dat['snr1'] = 'NaN'
        dat['snr2'] = 'NaN'; dat['sv_prn1'] = 'NaN'; dat['sv_prn2'] = 'NaN'
            
    # GPRMC
    try:
        gprmc.parse(gprmc_parts)
        dat['date'] = str(gprmc.datestamp)
        dat['time_stamp'] = str(gprmc.timestamp)
        dat['spd'] = str(gprmc.spd_over_grnd)
        dat['true_course'] = str(gprmc.true_course)
        dat['mag_var'] = str(gprmc.mag_variation)
        dat['mag_var_dir'] = str(gprmc.mag_var_dir)
            
        lats = gprmc.lat; longs= gprmc.lon
					
        #convert degrees,decimal minutes to decimal degrees 
        lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
        lat = (float(lats[0]+lats[1])+lat1)
        long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
        long = (float(longs[0]+longs[1]+longs[2])+long1)
					
        #calc position
        dat['lat_2'] = str(lat); dat['lon_2'] = str(-long)

        #convert to az central state plane east/north
        e,n = trans(-long,lat)
        dat['e_2'] = str(e); dat['n_2'] = str(n)
        
    except:
        dat['date'] = 'NaN'; dat['time_stamp'] = 'NaN'
        dat['spd'] = 'NaN'; dat['true_course'] = 'NaN'
        dat['mag_var'] = 'NaN'; dat['mag_var_dir'] = 'NaN'
        dat['lat_2'] = 'NaN'; dat['lon_2'] = 'NaN'

    #GPVTG
    try:
        gpvtg.parse(gpvtg_parts)
        dat['true_track'] = str(gpvtg.true_track)
        dat['spd_grnd_kmh'] = str(gpvtg.spd_over_grnd_kmph)
        dat['spd_grnd_kts'] = str(gpvtg.spd_over_grnd_kts)
        dat['mag_track'] = str(gpvtg.mag_track)
    except:
        dat['true_track'] = 'NaN'; dat['spd_grnd_kmh'] = 'NaN'
        dat['spd_grnd_kts'] = 'NaN'; dat['mag_track'] = 'NaN'
        
    self.textinput.text += time.asctime() + ' ' +gpgga_parts + '\n'
    self.textinput.text += time.asctime() + ' ' +gpgsa_parts + '\n'
    self.textinput.text += time.asctime() + ' ' +gprmc_parts + '\n'
    self.textinput.text += time.asctime() + ' ' +gpvtg_parts + '\n'
    self.textinput.text += time.asctime() + ' ' +gpgsv_parts + '\n'

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
        #self.laststationchange = time.clock()
     
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
        #self.laststationchange = time.clock()
     
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
        #self.laststationchange = time.clock()
             
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
       
        if self.ser!=0:
           try:
              dat = get_nmea(self)
              e = dat['e_1']
              n = dat['n_1']
              z = dat['alt']
              
              if self.ser2!=0:
	         d = dat['depth_m']
              
              if hasattr(self, 'textinput5'):
                 try:
                    # distance from station start
                    dist2 = str(sqrt((float(n)-float(self.textinput6.text))**2 + (float(e)-float(self.textinput5.text))**2))
                 except:
                    dist2 = ' '              
              
              ##self.textinput3.text = 'E: '+str(e)+', N: '+str(n)+', Elevation: '+str(z)+'\n'
              self.textinput3.text = 'E: '+str(e)+', N: '+str(n)+', Z: '+str(z)+', D: '+str(d)+', Distance from station: '+dist2+'\n'
        
           
           except:
              
              self.textinput3.text = 'E: NaN, N: NaN, Z: NaN, D: NaN, Distance from station: NaN\n'
      

    #=========================
    def _update_time(self, dt):
        self.item.title = 'Current time is '+time.asctime()

    #=========================
    #def _draw_me(self, dt):
    #    try:
    #       e = self.textinput3.text.split(':')[1].split(',')[0]
    #       n = self.textinput3.text.split(':')[2].split(',')[0]
    #       self.plot.points.append((float(e),float(n)))
    #       self.graph.xmax = 10+max(self.plot.points)[0]
    #       self.graph.xmin = min(self.plot.points)[0]-10
    #       self.graph.ymax = 10+max(self.plot.points)[1]
    #       self.graph.ymin = min(self.plot.points)[1]-10
    #    except:
    #       pass
    #    #xmax = random.randint(10, 100)
    #    #self.plot.points = [(x, sin(x / 10.)) for x in range(0, xmax)]
    #    #self.graph.xmax = xmax

    #=========================        
    def build(self):

        self.ser, self.ser2 = init_serial(self)

        root = Accordion(orientation='horizontal')
        
        self.item = AccordionItem(title='Current time is '+time.asctime())

        image = CameraWidget(size_hint = (2.0, 1.0)) 

        # log
        layout = GridLayout(cols=1)
        self.textinput = Log(text='Data Acquisition Log\n', size_hint = (0.25, 1.5), markup=True)
        layout.add_widget(self.textinput)
        image.textinput = self.textinput
       
        ## read nav station positions
        #with open('nav_stat_gps.txt') as f:
        #   dump = f.read()
        #f.close()
        #dump = dump.split('\n')
        #for k in dump:
        #    if k.startswith('e'):
        #       ep = float(k.split('=')[1].lstrip())
        #    elif k.startswith('n'):
        #       np = float(k.split('=')[1].lstrip())
        #    elif k.startswith('z'):
        #       zp = float(k.split('=')[1].lstrip())         


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
        
        ## for map
        ##layout.add_widget(Button(text='Map', width=100)) 
        #self.graph = Graph(xlabel='E', ylabel='N', x_ticks_minor=1,
        #x_ticks_major=25, y_ticks_major=10, y_ticks_minor=1,
        #y_grid_label=True, x_grid_label=True, padding=5,
        #x_grid=True, y_grid=True, xmin=ep-10, xmax=ep+10, ymin=np-10, ymax=np+10)

        #self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        #self.plot.points = [(ep,np)]
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

        Clock.schedule_interval(self._update_pos, 5)
        Clock.schedule_interval(self._update_time, 1)
        #Clock.schedule_interval(self._draw_me, 10)

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
              
        ## close the csv results files
        #bedf_csv.close()
        #print "output files closed"

        # close the serial port
        if self.ser!=0:
           self.ser.close()
           print "================="
           print "GPS is closed"
           print "================="

        # close the serial port
        if self.ser2!=0:
           self.ser2.close()
           print "================="
           print "Echosounder is closed"
           print "================="

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
    
    
   
