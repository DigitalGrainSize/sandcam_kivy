import kivy
kivy.require ( '1.8.0 ' )
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import WindowBase
from kivy.core.window import Window
from kivy.graphics import Canvas, Translate, Fbo, ClearColor, ClearBuffers
 
from kivy.uix.accordion import Accordion, AccordionItem
 
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

kv = '''
cameraWidget:
    orientation: 'vertical'

    Camera:
        id: camera
        resolution: 399, 299

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: '48dp'
        Button:
            text: 'Start'
            on_release: camera.play = True

        Button:
            text: 'Stop'
            on_release: camera.play = False
            
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
                                                         
'''

          
class cameraWidget(BoxLayout):
    def time(self, *args):
        self.text = time.asctime()

    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='test2.png')
        
    def TakePictureSand(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='sand.png')        

    def TakePictureGravel(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='gravel.png')        

    def TakePictureRock(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='rock.png') 

    def TakePictureSandRock(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='sand_rock.png') 

    def TakePictureSandGravel(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='sand_gravel.png') 
                                        
class Eyeball_DAQApp(App):
    def build(self):
        root = Accordion()
        for x in range(2):
            item = AccordionItem(title='Title %d' % x)    
            item.add_widget(Builder.load_string(kv))
            root.add_widget(item)
        return root   
        #return Builder.load_string(kv)
        
if __name__ == '__main__':
    Eyeball_DAQApp().run()    
    
    
    
