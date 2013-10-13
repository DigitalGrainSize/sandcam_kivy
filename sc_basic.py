"""
sc_get_gs.py
program to 
1) view and capture an image of sediment
2) get site and sample info from the user
3) save image to file with the site and sample in the file name
4) crop and make greyscale and save another file

Written by:
Daniel Buscombe, Oct 2013
Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
please contact:
dbuscombe@usgs.gov

SYNTAX:
python sc_get_gs.py

REQUIREMENTS:
python
kivy (http://kivy.org/#home)
python imaging library (https://pypi.python.org/pypi/PIL)

"""

import kivy
kivy.require('1.7.2')
 
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.uix.textinput import TextInput

import Image, os

def cropcentral(im):
    originX = 180
    originY = 1
    cropBox = (originX, originY, originX + 900, originY + 700)
    return im.crop(cropBox)

class SedimentCamApp(App):
          # Function to take a screenshot
          def doscreenshot(self,*largs):
                outname='site_'+self.site.text+'sample_'+self.sample.text+'_im%(counter)04d.png'
                Window.screenshot(name=outname)
                # get newest file
                filelist = os.listdir(os.getcwd())
                filelist = filter(lambda x: not os.path.isdir(x), filelist)
                newest = max(filelist, key=lambda x: os.stat(x).st_mtime)
                # read that file in as greyscale, crop and save under new name
                im = Image.open(newest).convert("L")
                region = cropcentral(im)
                newfile = newest.split('.')[0]+'_g.png'
                region.save(newfile)

          def build(self):

                # create a floating layout as base
                camlayout = FloatLayout(size=(600, 600))
                cam = Camera()        #Get the camera
                cam=Camera(resolution=(1024,1024), size=(300,300))
                cam.play=True         #Start the camera
                camlayout.add_widget(cam)

                button=Button(text='Take Picture',size_hint=(0.12,0.12))
                button.bind(on_press=self.doscreenshot)
                camlayout.add_widget(button)    #Add button to Camera Layout

                # create a text input box for site name
                s1 = Scatter(size_hint=(None, None), pos_hint={'x':.01, 'y':.9})
                self.site = TextInput(size_hint=(None, None), size=(150, 50), multiline=False)

                # create a text input box for sample (flag) name
                s2 = Scatter(size_hint=(None, None), pos_hint={'x':.01, 'y':.8})
                self.sample = TextInput(size_hint=(None, None), size=(150, 50), multiline=False)

                # add the text widgets to the window
                s1.add_widget(self.site)
                camlayout.add_widget(s1) 
                s2.add_widget(self.sample)
                camlayout.add_widget(s2) 

                return camlayout
             
if __name__ == '__main__':
    SedimentCamApp().run() 

