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
 
 
'''
Trying to understand this hint
http://stackoverflow.com/questions/22755619/screenshot-gives-importerror-cannot-import-name-glreadpixels-error-in-kivy
'''
 
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
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: "Take picture"
        on_press: root.TakePicture()
        height: '48dp'

'''
class cameraWidget(BoxLayout):
    def TakePicture(self, *args):
        self.export_to_png = export_to_png
        self.export_to_png(self.ids.camera, filename='test2.png')
 
class MyApp(App):
    def build(self):
        return Builder.load_string(kv)
if __name__ == '__main__':
    MyApp().run()
    
