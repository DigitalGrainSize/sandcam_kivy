"""
eyedaq_withtrimble.py
program to 
1) view and capture an image of sediment
2) get site info from the user
3) save image to file with the site and time in the file name

Written by:
Daniel Buscombe, Feb-March 2015
Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
please contact:
dbuscombe@usgs.gov

SYNTAX:
python eyedaq_withtrimble.py

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

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import WindowBase
from kivy.core.window import Window
from kivy.graphics import Canvas, Translate, Fbo, ClearColor, ClearBuffers

from kivy.clock import Clock

import time, os
from shutil import move as mv

import sys
import textwrap

## pip install kivy-garden
## garden install graph
from kivy.garden.graph import Graph, MeshLinePlot

from math import cos, sin

#import pyproj, csv

try:
   import fortune
except:
   print "fortune not installed"
   print "pip install fortune"


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
    def Play(self, *args):
        self.ids.camera.play = True
        now = time.asctime() #.replace(' ','_')
        self.textinput.text += 'Video resumed '+now+'\n'
             
    #=========================   
    def Pause(self, *args):
        self.ids.camera.play = False
        now = time.asctime() #.replace(' ','_').replace(':','_')
        self.textinput.text += 'Video paused '+now+'\n'

    #=========================
    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_capture_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Image collected: '+filename+'\n'
        mv(filename,'eyeballimages') 

    #=========================    
    def TakePictureSand(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_sand_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)  
        self.textinput.text += 'Sand image collected: '+filename+'\n'  
        mv(filename,'sandimages')   

    #=========================
    def TakePictureGravel(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_gravel_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)       
        self.textinput.text += 'Gravel image collected: '+filename+'\n'      
        mv(filename,'gravelimages') 
        
    #=========================
    def TakePictureRock(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_rock_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Rock image collected: '+filename+'\n'
        mv(filename,'rockimages') 
       
    #========================= 
    def TakePictureSandRock(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_sand_rock_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Sand/Rock image collected: '+filename+'\n'   
        mv(filename,'sandrockimages')    
      
    #=========================  
    def TakePictureSandGravel(self, *args):
        self.export_to_png = export_to_png
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]

        now = time.asctime().replace(' ','_').replace(':','_')
        filename = 'st'+self.txt_inpt.text+'_sand_gravel_'+now+'_e'+e+'_n'+n+'.png'
        self.export_to_png(self.ids.camera, filename=filename)
        self.textinput.text += 'Sand/Gravel image collected: '+filename+'\n'
        mv(filename,'sandgravelimages')    

    #=========================
    def change_st(self):
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'

        # get the last site visited and add 1, write to station file
        fsite = open('station_start.txt','wb')
        fsite.write(str(int(self.txt_inpt.text)+1)) 
        fsite.close()
        
    #=========================
    def change_st_button(self):
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'

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
    def _update_pos(self, dt):

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

        self.textinput3.text = 'Easting: '+str(e)+', Northing: '+str(n)+', Elevation: '+str(z)+'\n'

    #=========================
    def _update_time(self, dt):
        self.item.title = 'Current time is '+time.asctime()

    #=========================
    def _draw_me(self, dt):
        e = self.textinput3.text.split(':')[1].split(',')[0]
        n = self.textinput3.text.split(':')[2].split(',')[0]
        self.plot.points.append((float(e),float(n)))
        self.graph.xmax = 5+max(self.plot.points)[0]
        self.graph.xmin = min(self.plot.points)[0]-5
        self.graph.ymax = 5+max(self.plot.points)[1]
        self.graph.ymin = min(self.plot.points)[1]-5

        #xmax = random.randint(10, 100)
        #self.plot.points = [(x, sin(x / 10.)) for x in range(0, xmax)]
        #self.graph.xmax = xmax

    #=========================        
    def build(self):

        root = Accordion(orientation='horizontal')
        
        self.item = AccordionItem(title='Current time is '+time.asctime())

        image = CameraWidget(size_hint = (2.0, 1.0)) 

        # log
        layout = GridLayout(cols=1)
        self.textinput = Log(text='Data Acquisition Log\n', size_hint = (0.5, 1.0), markup=True)
        layout.add_widget(self.textinput)
        image.textinput = self.textinput
       
        # read nav station positions
        with open('nav_stat.txt') as f:
           dump = f.read()
        f.close()
        dump = dump.split('\n')
        for k in dump:
            if k.startswith('e'):
               self.ep = float(k.split('=')[1].lstrip())
            elif k.startswith('n'):
               self.np = float(k.split('=')[1].lstrip())
            elif k.startswith('z'):
               self.zp = float(k.split('=')[1].lstrip())   
            elif k.startswith('hca'):
               self.hca = float(k.split('=')[1].lstrip())

        # for map
        #layout.add_widget(Button(text='Map', width=100)) 
        self.graph = Graph(xlabel='E', ylabel='N', x_ticks_minor=1,
        x_ticks_major=25, y_ticks_major=10, y_ticks_minor=1,
        y_grid_label=True, x_grid_label=True, padding=5,
        x_grid=True, y_grid=True, xmin=self.ep-5, xmax=self.ep+5, ymin=self.np-5, ymax=self.np+5)

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(self.ep,self.np)]
        self.graph.add_plot(self.plot)
        layout.add_widget(self.graph)
        image.graph1 = self.plot
        
        # for quotes
        self.textinput2 = Log(text='', size_hint = (0.5, 1.0), markup=True)
        layout.add_widget(self.textinput2)
        image.textinput2 = self.textinput2
        
        self.textinput3 = Log(text='\n', size_hint = (0.25, 0.25), markup=True)
        layout.add_widget(self.textinput3)
        image.textinput3 = self.textinput3

        # add image to AccordionItem
        self.item.add_widget(image)
        #item.add_widget(self.textinput)
        self.item.add_widget(layout)

        Clock.schedule_interval(self._update_pos, 1)
        Clock.schedule_interval(self._update_time, 1)
        Clock.schedule_interval(self._draw_me, 2)

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

#=========================
#=========================
if __name__ == '__main__':

    try:
       os.mkdir('eyeballimages')
       os.mkdir('sandimages')
       os.mkdir('gravelimages')
       os.mkdir('rockimages')
       os.mkdir('sandrockimages')
       os.mkdir('sandgravelimages')
    except:
       pass

    Eyeball_DAQApp().run()
    
    
   
