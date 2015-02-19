"""
eyedaq_basic.py
program to 
1) view and capture an image of sediment
2) get site info from the user
3) save image to file with the site and time in the file name

Written by:
Daniel Buscombe, Feb 2015
Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
please contact:
dbuscombe@usgs.gov

SYNTAX:
python eyedaq_basic.py

REQUIREMENTS:
python
kivy (http://kivy.org/#home)

"""

from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
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

import time, os, shutil
from DGS import dgs
 
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
 

Builder.load_string('''
<CameraWidget>:
    orientation: 'vertical'
    image: camera
    label: label
    txt_inpt: txt_inpt
        
    Camera:
        id: camera
        resolution: 399, 299     
             
    BoxLayout:
        id: label
        orientation: 'horizontal'
        size_hint_y: None
        height: '48dp'
        Button:
            text: 'Play'
            on_release: root.Play()

        TextInput:
            id: txt_inpt
            text: 'Station'
            multiline: False
            focus: True
            on_text_validate: root.change_st()
            
        Button:
            text: 'Sand'
            on_press: root.TakePictureSand()  
            background_color: (1.0, 1.0, 0.0, 1.0)        

        Button:
            text: 'Rock'
            on_press: root.TakePictureRock() 
            background_color: (1.0, 0.0, 0.0, 1.0)  
                        
        Button:
            text: 'Custom 1'
            on_press: root.TakePictureSandRock() 
            background_color: (0.0, 0.2, 0.2, 1.0) 
             
        Button:
            text: 'Custom 3'
            background_color: (0.0, 0.6, 0.9, 1.0) 
                        
        Button:
            text: 'Waypoint'
            on_press: root.MarkWaypoint()                          
                        
    BoxLayout:
        id: label
        orientation: 'horizontal'
        size_hint_y: None
        height: '48dp'
        Button:
            text: 'Pause'
            on_release: root.Pause()

        Button:
            text: 'Record'
            on_press: root.TakePicture()  
            background_color: (0.5, 0.1, 0.25, 1.0) 
            
        Button:
            text: 'Gravel'
            on_press: root.TakePictureGravel()  
            background_color: (0.0, 0.0, 1.0, 1.0)
            
        Button:
            text: 'Mud'
            background_color: (0.0, 1.0, 1.0, 1.0)        
            
        Button:
            text: 'Custom 2 '
            on_press: root.TakePictureSandGravel()
            background_color: (0.0, 0.6, 0.9, 1.0) 
                                 
        Button:
            text: 'Custom 4'
            background_color: (0.0, 0.2, 0.2, 1.0) 
            
        Button:
            text: 'Timestamp'
            on_press: root.TakeTimeStamp()                          
''')

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
    image = ObjectProperty()
    label = ObjectProperty()
    source = StringProperty()
    textinput = ObjectProperty()
    txt_inpt = ObjectProperty(None)    
        
    def Play(self, *args):
        self.ids.camera.play = True
        now = time.asctime() #.replace(' ','_')
        self.textinput.text += 'Video resumed '+now+'\n'
                
    def Pause(self, *args):
        self.ids.camera.play = False
        now = time.asctime() #.replace(' ','_').replace(':','_')
        self.textinput.text += 'Video paused '+now+'\n'

    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_capture_'+now+'.png')
        self.textinput.text += 'Image collected: '+now+'\n'

        density = 10
        res = 1 # mm/pixel
        doplot = 0 # don't make plots
        
        mn,srt,sk,krt,pd = dgs('st'+self.txt_inpt.text+'_capture_'+now+'.png',density,doplot,res)
        
        shutil.move('st'+self.txt_inpt.text+'_capture_'+now+'.png','eyeballimages/processed')
        
        self.textinput.text += 'Mean Size: '+str(mn)+'\n'
        
    def TakePictureSand(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_sand_'+now+'.png')  
        self.textinput.text += 'Sand image collected: '+now+'\n'  
        shutil.move('st'+self.txt_inpt.text+'_sand_'+now+'.png','sandimages')   

    def TakePictureGravel(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_gravel_'+now+'.png')        
        self.textinput.text += 'Gravel image collected: '+now+'\n'      
        shutil.move('st'+self.txt_inpt.text+'_gravel_'+now+'.png','gravelimages') 
        
    def TakePictureRock(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_rock_'+now+'.png') 
        self.textinput.text += 'Rock image collected: '+now+'\n'
        shutil.move('st'+self.txt_inpt.text+'_rock_'+now+'.png','rockimages') 
        
    def TakePictureSandRock(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_sand_rock_'+now+'.png') 
        self.textinput.text += 'Sand/Rock image collected: '+now+'\n'   
        shutil.move('st'+self.txt_inpt.text+'_sand_rock_'+now+'.png','sandrockimages')    
        
    def TakePictureSandGravel(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_').replace(':','_')
        self.export_to_png(self.ids.camera, filename='st'+self.txt_inpt.text+'_sand_gravel_'+now+'.png') 
        self.textinput.text += 'Sand/Gravel image collected: '+now+'\n'
        shutil.move('st'+self.txt_inpt.text+'_sand_gravel_'+now+'.png','sandgravelimages')    

    def change_st(self):
        self.textinput.text += 'Station is '+self.txt_inpt.text+'\n'

    def TakeTimeStamp(self):
        self.textinput.text += 'Time is '+time.asctime()+'\n'                              

    def MarkWaypoint(self):
        self.textinput.text += 'Mark Waypoint at '+time.asctime()+': 36.0986958,-112.1097129\n'                              

        pass

class Eyeball_DAQApp(App):
 
    def build(self):
        root = Accordion(orientation='horizontal')

        item= AccordionItem(title='Current time is '+time.asctime())
        image = CameraWidget(size_hint = (1.0, 1.0)) 

        textinput = Log(text='Data Acquisition Log\n', size_hint = (0.5, 1.0), markup=True)
        image.textinput = textinput

        # add image to AccordionItem
        item.add_widget(image)
        item.add_widget(textinput)
        root.add_widget(item)

        return root

if __name__ == '__main__':

    try:
       os.mkdir('eyeballimages')
       os.mkdir('eyeballimages/processed')
       os.mkdir('sandimages')
       os.mkdir('gravelimages')
       os.mkdir('rockimages')
       os.mkdir('sandrockimages')
       os.mkdir('sandgravelimages')
    except:
       pass
    Eyeball_DAQApp().run()
    
    
    
    
