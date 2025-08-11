from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import cv2
import time
import numpy as np
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Line
from kivy.core.image import Image as CoreImage                                  
from kivy.uix.image import Image as KivyImage
from io import BytesIO
import os

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
    PhotoPreviewScreen:
    SummaryScreen:
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
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(60)
        md_bg_color: 0.9, 0.9, 0.9, 1
        padding: dp(10)
        spacing: dp(10)
        on_touch_down:
            root.manager.current = 'start'
    
        MDIconButton:
            icon: "arrow-left"
            size_hint: None, None
            size: dp(30), dp(30)
            padding: 0  # usuń padding, który przesuwa ikonę
            pos_hint: {"center_y": 0.5}

        MDLabel:
            text: "Cofnij"
            valign: 'center'
            halign: 'left'
    
    CameraWidget:       

<PhotoPreviewScreen>:
    name: 'preview'
    RelativeLayout:
        id: preview_layout

        Image:
            id: preview_image
            allow_stretch: True
            keep_ratio: True
            size_hint: 1, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        PaintWidget:
            id: paint_widget
            size_hint: 1, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

    MDBoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(30)
        padding: dp(20)
        size_hint_x: None
        width: self.minimum_width
        pos_hint: {'center_x': 0.5}
        MDIconButton:
            icon: "close"
            on_release: root.reject_photo()
        MDIconButton:
            icon: "check"
            on_release: root.accept_photo()

<SummaryScreen>:
    name: 'summary'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        Image:
            id: accepted_image
            size_hint_y: 0.6
            allow_stretch: True
            keep_ratio: True

        MDTextField:
            id: description_input
            hint_text: "Dodaj opis zdjęcia..."
            multiline: True
            size_hint_y: 0.25

        MDBoxLayout:
            size_hint_y: 0.15
            size_hint_x: None           # dajemy None, by ustawić własną szerokość
            width: self.minimum_width   # szerokość dopasowana do dzieci + spacing + padding
            pos_hint: {'center_x': 0.5}
            
            spacing: dp(20)
            padding: dp(20)
            MDIconButton:
                icon: "close"
                on_release: root.reject_summary()
            MDIconButton:
                icon: "check"
                on_release: root.accept_summary() 
                
            MDRaisedButton:
                text: "Eksportuj do PDF"
                on_release: root.save_pdf()            
            
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
    
        MDIconButton:
            icon: "arrow-left"
            size_hint: None, None
            size: dp(30), dp(30)
            padding: 0  # usuń padding, który przesuwa ikonę
            pos_hint: {"center_y": 0.5}

        MDLabel:
            text: "Cofnij"
            valign: 'center'
            halign: 'left'     
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
        self.add_widget(Widget(size_hint_y=None, height=80))
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
            app = MDApp.get_running_app()
            preview_screen = app.root.get_screen('preview')
            preview_screen.set_image(self.current_frame)
            app.root.current = 'preview'

    def on_parent(self, widget, parent):
        # Zwolnienie kamery przy zamknięciu widżetu
        if parent is None:
            self.capture.release()

class StartScreen(Screen):
    pass

class ReportScreen(Screen):
    pass
class PhotoPreviewScreen(Screen):
    def set_image(self, frame):
        frame = cv2.flip(frame, 0)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        data = frame_rgb.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        self.ids.preview_image.texture = texture
        self.current_frame = frame

    def reject_photo(self):
        self.manager.current = 'report'

    def accept_photo(self):
        import numpy as np
        app = MDApp.get_running_app()
        paint_widget = self.ids.paint_widget

        # Eksportuj rysunek jako tekstura → numpy array (RGBA)
        fbo_image = paint_widget.export_as_image()
        texture = fbo_image.texture
        size = texture.size
        pixels = texture.pixels
        drawing = np.frombuffer(pixels, dtype=np.uint8).reshape((int(size[1]), int(size[0]), 4))
        drawing = cv2.cvtColor(drawing, cv2.COLOR_RGBA2BGRA)  # zamiana RGBA → BGRA

        # Przygotuj zdjęcie jako BGRA (czyli z kanałem przezroczystości)
        photo = cv2.cvtColor(self.current_frame.copy(), cv2.COLOR_BGR2BGRA)

        # Dopasuj rysunek do rozmiaru zdjęcia (jeśli rozmiary inne)
        drawing = cv2.resize(drawing, (photo.shape[1], photo.shape[0]))

        # Połącz rysunek ze zdjęciem
        combined = cv2.addWeighted(photo, 1.0, drawing, 1.0, 0)

        # Zamień z BGRA na BGR (czyli gotowe zdjęcie)
        final_frame = cv2.cvtColor(combined, cv2.COLOR_BGRA2BGR)

        # Wyślij do ekranu podsumowania
        summary_screen = app.root.get_screen('summary')
        summary_screen.set_image_and_description(final_frame)
        app.root.current = 'summary'

class SummaryScreen(Screen):
    def set_image_and_description(self, frame):
        # Konwersja obrazu do tekstury i ustawienie w Image widget
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        data = frame_rgb.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        self.ids.accepted_image.texture = texture
        self.current_frame = frame

        # Wyczyść pole opisu przy wejściu
        self.ids.description_input.text = ""

    def reject_summary(self):
        # Przykładowo wróć do ekranu kamery albo podglądu
        self.manager.current = 'report'

    def accept_summary(self):
        description = self.ids.description_input.text.strip()
        filename = f"zdjecie_{int(time.time())}.jpg"
        cv2.imwrite(filename, self.current_frame)
        print(f"📷 Zapisano zdjęcie: {filename}")
        print(f"📝 Opis: {description}")
        # Tu możesz dodać zapis opisu do bazy lub pliku
        self.manager.current = 'start'  # lub inny ekran końcowy

    def save_pdf(self):
        import cv2
        # Pobierz obraz z aktualnej klatki (numpy array BGR)
        frame = self.current_frame  # BGR numpy array
        frame = cv2.flip(frame, 0)
        # Konwertuj BGR do RGB (bo reportlab wymaga RGB)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Zamień numpy array na bytes (w formacie PNG)
        is_success, buffer = cv2.imencode(".png", rgb_image)
        if not is_success:
            print("Błąd konwersji obrazu do PNG")
            return

        image_bytes = io.BytesIO(buffer.tobytes())

        # Opis tekstowy
        description = self.ids.description_input.text.strip()

        # Utwórz PDF na A4
        pdf_filename = f"raport_{int(time.time())}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)

        width, height = A4  # (595, 842) w punktach PDF

        # Wstaw obraz na środku i trochę z góry (zmień według potrzeby)
        image = ImageReader(image_bytes)
        image_width, image_height = rgb_image.shape[1], rgb_image.shape[0]

        # Skalowanie obrazka, by zmieścił się w A4 (np max 500x500 punktów)
        max_dim = 500
        scale = min(max_dim / image_width, max_dim / image_height, 1)

        img_w = image_width * scale
        img_h = image_height * scale

        img_x = (width - img_w) / 2
        img_y = height - img_h - 100  # 100 pkt od góry strony

        c.drawImage(image, img_x, img_y, width=img_w, height=img_h)

        # Dodaj opis pod obrazkiem
        text_x = 50
        text_y = img_y - 80

        c.setFont("Helvetica", 12)
        c.drawString(text_x, text_y, "Opis:")
        c.setFont("Helvetica", 10)
        text_lines = description.split('\n')
        for i, line in enumerate(text_lines):
            c.drawString(text_x, text_y - 15 * (i + 1), line)

        c.showPage()
        c.save()

        print(f"✅ PDF zapisany jako {pdf_filename}")

class PaintWidget(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 0, 0, 1)  # czerwony kolor
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]

    def export_as_image_texture(self):
        # Eksportuj narysowane elementy jako tekstura
        return self.export_as_image().texture
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