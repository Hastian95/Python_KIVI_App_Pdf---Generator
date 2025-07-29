from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
import cv2
import time

from kivy.core.window import Window
Window.size = (360, 640)  # symulacja typowego telefonu

KV = '''

<CameraClick>:
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
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()

ScreenManager:
    StartScreen:
    ReportScreen:
    OldReportScreen:

<StartScreen>:
    name: 'start'
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(40)
        padding: dp(100)
        halign: 'center'
        
        MDLabel:
            text: "Witaj w Generatorze Raportów"
            halign: 'center'
            font_style: 'H5'
        MDRaisedButton:
            text: "Stwórz nowy projekt"
            on_release: root.manager.current = 'report'
            pos_hint: {"center_x": 0.5}
        MDRaisedButton:
            md_bg_color: 44, 68, 81, 0.33
            text: "Twoje projekty"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = 'old'


<ReportScreen>:
    name: 'report'
    MDBoxLayout:
        size_hint_y: None
        height: dp(50)
        md_bg_color: 0.9, 0.9, 0.9, 1
        padding: dp(10)
        spacing: dp(10)
        on_touch_down:
            root.manager.current = 'start'
    
        MDIconButton:
            icon: "arrow-left"
            size_hint_x: None
            width: dp(30)
        
        MDLabel:
            text: "Cofnij"
            halign: 'center'
    
    CameraWidget:       
        
            
<OldReportScreen>:
    name: 'old'
    MDBoxLayout:
        size_hint_y: None
        height: dp(50)
        md_bg_color: 0.9, 0.9, 0.9, 1
        padding: dp(10)
        spacing: dp(10)
        on_touch_down:
            root.manager.current = 'start'
    
        MDIcon:
            icon: "arrow-left"
            size_hint_x: None
            width: dp(30)
        
        MDLabel:
            text: "Cofnij"
            halign: 'center'            
'''

class CameraWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.capture = cv2.VideoCapture(0)

        self.img_widget = Image()
        self.add_widget(self.img_widget)

        self.btn_capture = MDRaisedButton(
            text="📸 Zrób zdjęcie",
            pos_hint={'center_x': 0.5},
            size_hint_y=None,
            height='48dp',
            on_release=self.capture_image
        )
        self.add_widget(self.btn_capture)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            self.current_frame = frame
            # Konwersja do tekstury Kivy (BGR -> RGB + flip pionowy)
            frame = cv2.flip(frame, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.img_widget.texture = texture

    def capture_image(self, *args):
        if hasattr(self, 'current_frame'):
            filename = f"zdjecie_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.current_frame)
            print(f"📷 Zapisano zdjęcie: {filename}")

    def on_parent(self, widget, parent):
        # Zwolnienie kamery przy zamknięciu widżetu
        if parent is None:
            self.capture.release()

class StartScreen(Screen):
    pass

class ReportScreen(Screen):
    pass

class OldReportScreen(Screen):
    pass

class ReportApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_stop(self):
        pass

ReportApp().run()

#from kivymd.app import MDApp
#from kivy.core.window import Window
#from kivymd.uix.label import MDLabel,MDIcon
#from kivymd.uix.screen import MDScreen
#from kivymd.uix.button import MDFlatButton,MDRectangleFlatButton,MDIconButton,MDFloatingActionButton
#from kivymd.uix.textfield import MDTextField
#from kivymd.uix.dialog import MDDialog
#from kivymd.uix.list import OneLineListItem, MDList
#from kivymd.uix.scrollview import ScrollView
#
#from kivy.core.window import Window
#Window.size = (360, 640)  # symulacja typowego telefonu
#
#class DemoApp(MDApp):
#    def build(self):
#        screen = MDScreen()
#        scroll = ScrollView()
#        list_view = MDList()
#        item1 = OneLineListItem(text="Item 1")
#        item2 = OneLineListItem(text="Item 2")
#        list_view.add_widget(item1)
#        list_view.add_widget(item2)
#        scroll.add_widget(list_view)
#        screen.add_widget(scroll)
#
#        return screen
#
#DemoApp().run()

#https://www.youtube.com/watch?v=6uGZfBTl8Xc&list=PLhTjy8cBISEoQQLZ9IBlVlr4WjVoStmy-&index=5

#from kivymd.uix.label import MDLabel,MDIcon
#label = MDLabel(text="Hello world ! ;)", halign="center", theme_text_color='Hint',font_style="Overline")
#icon_label = MDIcon(icon="language-python", pos_hint={"center_x": 0.5, "center_y": 0.5})
#return icon_label

#def build(self):
#    screen = Screen()
#    btn_flat = MDRectangleFlatButton(text="Hello Susanne", pos_hint={"center_x": 0.5, "center_y": 0.5})
#    icon_btn = MDFloatingActionButton(icon="language-python", pos_hint={"center_x": 0.5, "center_y": 0.5})
#    self.theme_cls.primary_palette = "Orange"
#    self.theme_cls.primary_hue = "A700"  # "100" light or "A700 dark"
#    self.theme_cls.theme_style = "Dark"
#    screen.add_widget(icon_btn)
#    return screen



#    def build(self):
#        screen = MDScreen()
#        self.username = MDTextField(hint_text='Enter username',
#                               pos_hint={"center_x": 0.5, "center_y": 0.5},
#                               size_hint_x=None, width=Window.width * 0.4)
#        button = MDRectangleFlatButton(text="Show",pos_hint={"center_x": 0.5, "center_y": 0.4},
#                                       on_release = self.show_data)
#
#        screen.add_widget(self.username)
#        screen.add_widget(button)
#        return screen
#
#    def show_data(self, obj):
#        if self.username.text is "":
#            check_string = 'Please enter username!'
#        else:
#            check_string = self.username.text + " is free!"
#        close_button = MDFlatButton(text='CLOSE',on_release=self.close_dialog )
#        more_button = MDFlatButton(text='MORE', )
#        self.dialog = MDDialog(title='username',text=check_string, size_hint=(0.65,1),
#                          buttons=[close_button,more_button])
#        self.dialog.open()
#
#    def close_dialog(self,obj):
#        self.dialog.dismiss()