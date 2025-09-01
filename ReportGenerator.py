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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# rejestracja czcionki obsługującej polskie znaki
pdfmetrics.registerFont(
    TTFont('Arial', r"C:\Windows\Fonts\arial.ttf")
)



from kivy.core.window import Window
Window.size = (360, 640)  # symulacja typowego telefonu

KV = '''

<CameraClick>:
    orientation: 'vertical'

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
            size_hint: None, None
            size: 0, 0
            pos: 0, 0

    MDBoxLayout:
        size_hint_y: None
        height: dp(60)
        spacing: dp(10)
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
 
        # 🧹 czyszczenie rysunku
        MDIconButton:
            icon: "delete"
            on_release: paint_widget.clear_canvas()

        # 🎨 wybór kolorów
        MDIconButton:
            icon: "circle"
            theme_icon_color: "Custom"
            icon_color: 1, 0, 0, 1
            on_release: paint_widget.set_color((1, 0, 0, 1))  # czerwony

        MDIconButton:
            icon: "circle"
            theme_icon_color: "Custom"
            icon_color: 0, 1, 0, 1
            on_release: paint_widget.set_color((0, 1, 0, 1))  # zielony

        MDIconButton:
            icon: "circle"
            theme_icon_color: "Custom"
            icon_color: 0, 0, 1, 1
            on_release: paint_widget.set_color((0, 0, 1, 1))  # niebieski

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

    def on_kv_post(self, base_widget):
        # reaguj na zmiany obrazu i layoutu
        img = self.ids.preview_image
        img.bind(texture=self._update_paint_overlay,
                 size=self._update_paint_overlay,
                 pos=self._update_paint_overlay,
                 keep_ratio=self._update_paint_overlay,
                 allow_stretch=self._update_paint_overlay)
        Clock.schedule_once(self._update_paint_overlay, 0)

    def _update_paint_overlay(self, *args):
        img = self.ids.preview_image
        pw = self.ids.paint_widget
        tex = img.texture
        if not tex:
            return

        tex_w, tex_h = tex.size
        wid_w, wid_h = img.size
        wid_x, wid_y = img.pos
        if not tex_w or not tex_h or not wid_w or not wid_h:
            return

        # rozmiar zdjęcia na ekranie, gdy keep_ratio=True (letterbox)
        scale = min(wid_w / tex_w, wid_h / tex_h) if img.keep_ratio else max(wid_w / tex_w, wid_h / tex_h)
        disp_w, disp_h = tex_w * scale, tex_h * scale
        left = wid_x + (wid_w - disp_w) / 2.0
        bottom = wid_y + (wid_h - disp_h) / 2.0

        # dopasuj PaintWidget do obszaru *rzeczywistego* zdjęcia
        pw.size = (disp_w, disp_h)
        pw.pos = (left, bottom)

    def set_image(self, frame):
        # (jeśli potrzebujesz flipa, zostaw; inaczej usuń)
        frame = cv2.flip(frame, 0)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        data = frame_rgb.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        self.ids.preview_image.texture = texture
        self.current_frame = frame
        # po ustawieniu tekstury przelicz nakładkę
        Clock.schedule_once(self._update_paint_overlay, 0)
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
        drawing = cv2.flip(drawing,0)

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
        max_w, max_h = width - 100, height - 200
        scale = min(max_w / image_width, max_h / image_height, 1)

        img_w = image_width * scale
        img_h = image_height * scale

        img_x = (width - img_w) / 2
        img_y = height - img_h - 100  # 100 pkt od góry strony

        c.drawImage(image, img_x, img_y, width=img_w, height=img_h)

        # Dodaj opis pod obrazkiem
        text_x = 50
        text_y = img_y - 80

        c.setFont("Arial", 15)
        c.drawString(text_x, text_y, "Opis:")
        c.setFont("Arial", 10)
        text_lines = description.split('\n')
        for i, line in enumerate(text_lines):
            c.drawString(text_x, text_y - 15 * (i + 1), line)

        c.showPage()
        c.save()

        print(f"✅ PDF zapisany jako {pdf_filename}")

class PaintWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_color = (1, 0, 0, 1)  # domyślnie czerwony
        self.line_width = 2

    def set_color(self, rgba):
        self.current_color = rgba

    def clear_canvas(self):
        self.canvas.clear()

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.current_color)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)

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
        if self.capture.isOpened():
            self.capture.release()

ReportApp().run()
