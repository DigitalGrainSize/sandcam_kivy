"""
eyedaq_basic.py
program to 
1) view and capture an image of sediment
2) get site and sample info from the user
3) save image to file with the site and sample in the file name

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
import time 
 
def export_to_png(self, filename, *args):
    '''Saves an image of the widget and its children in png format at the
    specified filename. Works by removing the widget canvas from its
    parent, rendering to an :class:`~kivy.graphics.fbo.Fbo`, and calling
    :meth:`~kivy.graphics.texture.Texture.save`.

    .. note::

        The image includes only this widget and its children. If you want to
        include widgets elsewhere in the tree, you must call
        :meth:`~Widget.export_to_png` from their common parent, or use
        :meth:`~kivy.core.window.Window.screenshot` to capture the whole
        window.

    .. note::

        The image will be saved in png format, you should include the
        extension in your filename.

    .. versionadded:: 1.8.1
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
    image: camera
    label: label
    orientation: 'vertical'
        
    Camera:
        id: camera
        resolution: 399, 299     

    BoxLayout:
        id: label
        orientation: 'horizontal'
        size_hint_y: None
        height: '48dp'
        Button:
            text: 'Start'
            on_release: root.Play()

        Button:
            text: 'Stop'
            on_release: root.Pause()
            
        Button:
            text: 'Capture'
            on_press: root.TakePicture()   
            
        Button:
            text: 'Sand'
            on_press: root.TakePictureSand()  
            background_color: (1.0, 1.0, 0.0, 1.0)
            
        Button:
            text: 'Sand/Gravel'
            on_press: root.TakePictureSandGravel() 
            background_color: (0.0, 1.0, 1.0, 1.0)
                     
        Button:
            text: 'Gravel'
            on_press: root.TakePictureGravel()  
            background_color: (0.0, 0.0, 1.0, 1.0)

        Button:
            text: 'Sand/Rock'
            on_press: root.TakePictureSandRock() 
            background_color: (0.0, 1.0, 0.0, 1.0)
                        
        Button:
            text: 'Rock'
            on_press: root.TakePictureRock() 
            background_color: (1.0, 0.0, 0.0, 1.0)      
        
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
    
#    def on_touch_down(self, touch):

#        if self.image.collide_point(*touch.pos):
#            self.label.text = str(touch.pos)

#    def on_touch_up(self, touch):
#        self.label.text = 'Hello World'
#        if self.textinput is not None:
#            self.textinput.text += ' ... and {}'.format(touch.pos)

    def Play(self, *args):
        self.ids.camera.play = True
        now = time.asctime().replace(' ','_')
        self.textinput.text += 'Video resumed '+now+'\n'
                
    def Pause(self, *args):
        self.ids.camera.play = False
        now = time.asctime().replace(' ','_')
        self.textinput.text += 'Video paused '+now+'\n'

    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='capture_'+now+'.png')
        self.textinput.text += 'Image collected: '+now+'\n'
        
    def TakePictureSand(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='sand_'+now+'.png')  
        self.textinput.text += 'Sand image collected: '+now+'\n'     

    def TakePictureGravel(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='gravel_'+now+'.png')        
        self.textinput.text += 'Gravel image collected: '+now+'\n'      
        
    def TakePictureRock(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='rock_'+now+'.png') 
        self.textinput.text += 'Rock image collected: '+now+'\n'
        
    def TakePictureSandRock(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='sand_rock_'+now+'.png') 
        self.textinput.text += 'Sand/Rock image collected: '+now+'\n'      
        
    def TakePictureSandGravel(self, *args):
        self.export_to_png = export_to_png
        now = time.asctime().replace(' ','_')
        self.export_to_png(self.ids.camera, filename='sand_gravel_'+now+'.png') 
        self.textinput.text += 'Sand/Gravel image collected: '+now+'\n'   

        pass

class Eyeball_DAQApp(App):
 
    def build(self):
        root = Accordion(orientation='horizontal')

        item= AccordionItem(title=time.asctime())
        image = CameraWidget(size_hint = (1.0, 1.0)) 

        textinput = Log(text='Data Acquisition Log\n', size_hint = (0.5, 1.0))
        image.textinput = textinput

        # add image to AccordionItem
        item.add_widget(image)
        item.add_widget(textinput)
        root.add_widget(item)

        return root

if __name__ == '__main__':
    Eyeball_DAQApp().run()
    
    
    
    
