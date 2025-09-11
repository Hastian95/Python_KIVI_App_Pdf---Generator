from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.properties import ListProperty, StringProperty, NumericProperty
from reportlab.lib import colors
import os
import json
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
from kivymd.uix.snackbar import Snackbar
from kivy.uix.screenmanager import Screen

# rejestracja czcionki obsługującej polskie znaki
pdfmetrics.registerFont(
    TTFont('Arial', r"C:\Windows\Fonts\arial.ttf")
)



from kivy.core.window import Window
Window.size = (360, 640)  # symulacja typowego telefonu

#Obsługa zapisywania plików


PROJECTS_FILE = "projects.json"

def load_projects():
    """Wczytuje projekty z pliku JSON (lub tworzy pustą strukturę)."""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"projects": []}
    return {"projects": []}

def save_projects(data):
    """Zapisuje projekty do pliku JSON."""
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class StartScreen(Screen):
    def create_project(self):
        project_name = self.ids.project_name.text.strip()

        # Walidacja pustego pola
        if not project_name:
            self.ids.project_name.error = True
            self.ids.project_name.helper_text = "Wpisz nazwę projektu"
            self.ids.project_name.helper_text_mode = "on_error"
            return

        # Walidacja długości (max 30 znaków)
        if len(project_name) > 30:
            self.ids.project_name.error = True
            self.ids.project_name.helper_text = "Maks. 30 znaków"
            self.ids.project_name.helper_text_mode = "on_error"
            return

        # Reset błędu
        self.ids.project_name.error = False

        # ---- Zapisywanie projektu do JSON ----
        data = load_projects()

        # sprawdzamy, czy taki projekt już istnieje
        if any(p["name"] == project_name for p in data["projects"]):
            self.ids.project_name.error = True
            self.ids.project_name.helper_text = "Taka nazwa już istnieje"
            self.ids.project_name.helper_text_mode = "on_error"
            return

        # dodajemy nowy projekt
        data["projects"].append({"name": project_name})
        save_projects(data)

        print(f"Tworzę projekt: {project_name}")
        self.manager.current = "report"



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

        ResponsiveLabel:
            text: "Witaj w Generatorze Raportów"
            halign: 'center'
            base_size: dp(32)   # bazowy rozmiar tekstu (dla ekranu 1280x720)
        
        MDTextField:
            id: project_name
            hint_text: "Nazwa projektu"
            max_text_length: 30
            multiline: False
            mode: "rectangle"
            size_hint_x: None
            width: dp(250)
            pos_hint: {"center_x": 0.5}
        
        ResponsiveButton:
            text: "Stwórz nowy projekt"
            on_release: root.create_project()
            pos_hint: {"center_x": 0.5}
            base_size: dp(20)
            

        ResponsiveButton:
            md_bg_color: 44/255, 68/255, 81/255, 0.33
            text: "Twoje projekty"
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = 'old'
            base_size: dp(20)

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
    BoxLayout:                   
        orientation: "vertical"  
    
        Widget:                # pusty "odstęp"
            size_hint_y: None
            height: dp(60)     # tyle miejsca od góry
        
        
        MDBoxLayout:                    
            size_hint_y: None           
            height: dp(60)              
            spacing: dp(10)             
            padding: dp(20)             
            size_hint_x: None           
            width: self.minimum_width   
            pos_hint: {'center_x': 0.5} 
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
            
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            padding: dp(20)
            size_hint_x: None
            width: self.minimum_width
            pos_hint: {'center_y': 0.1}
            pos_hint: {'center_x': 0.5}
                
                 # ✏️ narzędzia do rysowania
            MDIconButton:
                icon: "pencil"
                on_release: paint_widget.set_tool("free")  # tryb swobodnego rysowania
            
            MDIconButton:
                icon: "ray-start-end"
                on_release: paint_widget.set_tool("line")  # prosta linia
            
            MDIconButton:
                icon: "checkbox-blank-outline"
                on_release: paint_widget.set_tool("rect")  # prostokąt
            
            MDIconButton:
                icon: "circle-outline"
                on_release: paint_widget.set_tool("circle")  # okrąg 
            # ⬅️ Nowy suwak do zmiany grubości linii
        MDBoxLayout:                    
            size_hint_y: None
            height: dp(60)
            spacing: dp(20)
            padding: dp(20)
            #size_hint_x: 0.5
            #width: self.minimum_width
            pos_hint: {'center_x': 0.5}
            orientation: 'horizontal'
            
            MDSlider:
                id: slider_width
                min: 1
                max: 10
                step: 1
                size_hint_x: 0.7
                
                on_value:
                    slider_label.text = str(int(self.value))
                    app.root.get_screen('preview').ids.paint_widget.set_line_width(self.value)
            
            MDLabel:
                id: slider_label
                size_hint_x: None
                text: "2"
                width: dp(50)
                font_size: dp(20)
                halign: 'center'
                size_hint_x: 0.3  
            
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
                on_release:
                    paint_widget.clear_canvas()
                    root.reject_photo()
                    
            MDIconButton:
                icon: "check"
                on_release: root.accept_photo()
        
            # 🧹 czyszczenie rysunku
            MDIconButton:
                icon: "delete"
                on_release: paint_widget.clear_canvas()
            MDIconButton:
                icon: "undo"
                on_release: paint_widget.undo()
<SummaryScreen>:
    name: 'summary'

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        # 📷 zdjęcie u góry
        Image:
            id: accepted_image
            size_hint_y: 0.4
            allow_stretch: True
            keep_ratio: True

        # 🔽 przewijane pola tekstowe
        ScrollView:
            size_hint_y: 0.35   # nie cała połowa, żeby jeszcze było miejsce na ikony
            do_scroll_x: False

            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

                MDTextField:
                    id: description_input_legend
                    hint_text: "Tytuł strony"
                    max_text_length: 30
                    multiline: False
                    size_hint_y: None
                    height: dp(60)

                MDTextField:
                    id: description_input
                    hint_text: "Dodaj opis zdjęcia..."
                    multiline: True
                    size_hint_y: None
                    height: dp(120)

        # ✅ ikony i przyciski zawsze na dole
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(20)
            padding: dp(20)
            pos_hint: {'center_x': 0.5}

            MDIconButton:
                icon: "close"
                on_release:
                    app.root.get_screen("preview").ids.paint_widget.clear_canvas()
                    app.root.current = "report"

            MDIconButton:
                icon: "check"
                on_release: root.accept_summary()

            MDRaisedButton:
                text: "Eksportuj do PDF"
                on_release: root.save_pdf()


<OldReportScreen>:
    name: 'old'
    BoxLayout:
        orientation: "vertical"

        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: 0.9, 0.9, 0.9, 1
            padding: dp(10)
            spacing: dp(10)

            MDIconButton:
                icon: "arrow-left"
                size_hint: None, None
                size: dp(30), dp(30)
                pos_hint: {"center_y": 0.5}
                on_release: root.manager.current = 'start'

            MDLabel:
                text: "Cofnij"
                valign: 'center'
                halign: 'left'

        ScrollView:
            MDList:
                id: projects_list

'''

#Skalowanie ekranu powitalnego

def get_scale(base_width=360, base_height=640):
    """Zwraca współczynnik skalowania względem bazowej rozdzielczości."""
    scale_w = Window.width / base_width
    scale_h = Window.height / base_height
    return min(scale_w, scale_h)


class ResponsiveLabel(MDLabel):
    base_size = dp(20)  # domyślny rozmiar bazowy

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.update_font_size)
        self.update_font_size()

    def update_font_size(self, *args):
        scale = get_scale()
        self.font_size = self.base_size * scale


class ResponsiveButton(MDRaisedButton):
    base_size = dp(16)  # domyślny rozmiar bazowy czcionki

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.update_font_size)
        self.update_font_size()

    def update_font_size(self, *args):
        scale = get_scale()
        self.font_size = self.base_size * scale

class OldReportScreen(Screen):
    def on_pre_enter(self, *args):
        """Za każdym razem gdy wchodzimy na ekran, ładujemy projekty z JSON"""
        self.load_projects()

    def load_projects(self):
        data = load_projects()

        # Czyścimy starą listę
        self.ids.projects_list.clear_widgets()

        # Dodajemy każdy projekt jako element listy
        for project in data.get("projects", []):
            item = OneLineIconListItem(
                text=project["name"],
                on_release=lambda x, name=project["name"]: self.open_project(name)
            )
            icon = IconLeftWidget(icon="folder")
            item.add_widget(icon)
            self.ids.projects_list.add_widget(item)

    def open_project(self, project_name):
        print(f"Otwieram projekt: {project_name}")
        # 👉 tutaj możesz załadować dane projektu, np. przełączyć na inny ekran
        # self.manager.current = "report"

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
            frame = cv2.flip(frame, 0)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.current_frame = frame_rgb
            # Konwersja do tekstury Kivy (BGR -> RGB + flip pionowy)
            frame = cv2.flip(frame, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(frame_rgb.shape[1], frame_rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
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
        # Przyjmujemy 'frame' w RGB (tak jak ustawił CameraWidget)
        # Jeśli dostajesz BGR z innego miejsca, konwertuj tu: frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # tekstura oczekuje RGB
        data = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        self.ids.preview_image.texture = texture

        # przechowujemy obraz w RGB
        self.current_frame = frame

        # przelicz nakładkę rysowania
        Clock.schedule_once(self._update_paint_overlay, 0)

    def reject_photo(self):
        self.manager.current = 'report'

    def accept_photo(self):
        import numpy as np
        app = MDApp.get_running_app()
        paint_widget = self.ids.paint_widget

        # 1) Eksport rysunku jako RGBA (H, W, 4)
        fbo_image = paint_widget.export_as_image()
        tex = fbo_image.texture
        size = tex.size
        pixels = tex.pixels
        drawing = np.frombuffer(pixels, dtype=np.uint8).reshape((int(size[1]), int(size[0]), 4))

        # Kivy's pixel order is RGBA already — drawing is RGBA
        rgba = drawing  # (H, W, 4), kanały: R,G,B,A

        # 2) Przygotuj zdjęcie jako RGB (już trzymamy current_frame jako RGB)
        photo = self.current_frame  # RGB (H, W, 3)

        # 3) Dopasuj rozmiary i flip (jeśli potrzeba)
        rgba_resized = cv2.resize(rgba, (photo.shape[1], photo.shape[0]))
        rgba_resized = cv2.flip(rgba_resized, 0)  # jeśli rysunek jest odwrócony

        # 4) Rozdziel kanały rysunku: rgb + alpha (0..1)
        rgb_d = rgba_resized[:, :, :3].astype(np.float32)
        alpha = rgba_resized[:, :, 3].astype(np.float32) / 255.0
        alpha = alpha[:, :, None]  # kształt (H, W, 1)

        # 5) Kompozycja per-pixel: wynik = photo*(1-alpha) + drawing*alpha
        photo_f = photo.astype(np.float32)
        out = (photo_f * (1.0 - alpha) + rgb_d * alpha).astype(np.uint8)

        # 6) final_frame jest RGB
        final_frame = out

        # Wyślij do Summary (trzymamy RGB wszędzie)
        summary_screen = app.root.get_screen('summary')
        summary_screen.set_image_and_description(final_frame)
        app.root.current = 'summary'

class SummaryScreen(Screen):
    def set_image_and_description(self, frame):
        # frame — oczekiwane RGB
        frame_rgb = frame
        data = frame_rgb.tobytes()
        texture = Texture.create(size=(frame_rgb.shape[1], frame_rgb.shape[0]), colorfmt='rgb')
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        self.ids.accepted_image.texture = texture

        # Zapisujemy jako RGB
        self.current_frame = frame_rgb

        # Wyczyść opis
        self.ids.description_input.text = ""
        self.ids.description_input_legend.text = ""

    def reject_summary(self):
        # Przykładowo wróć do ekranu kamery albo podglądu
        self.manager.current = 'report'

    def accept_summary(self):
        description = self.ids.description_input.text.strip()
        description_legend = self.ids.description_input_legend.text.strip()
        filename = f"zdjecie_{int(time.time())}.jpg"
        cv2.imwrite(filename, self.current_frame)
        print(f"📷 Zapisano zdjęcie: {filename}")
        print(f"📝 Tytuł: {description_legend}")
        print(f"📝 Opis: {description}")
        # Tu możesz dodać zapis opisu do bazy lub pliku
        self.manager.current = 'start'  # lub inny ekran końcowy

    def save_pdf(self):
        import cv2
        # frame jest RGB
        frame = self.current_frame
        frame = cv2.flip(frame, 0)  # tylko jeśli chcesz odwrócić pionowo (zgodnie z resztą)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # już RGB

        is_success, buffer = cv2.imencode(".png", rgb_image)
        if not is_success:
            print("Błąd konwersji obrazu do PNG")
            return

        image_bytes = io.BytesIO(buffer.tobytes())

        # Opis tekstowy
        description = self.ids.description_input.text.strip()
        description_legend = self.ids.description_input_legend.text.strip()

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

        # Oblicz maksymalną długość tytułu
        def get_max_title_length(c, font_size, max_width):
            # Oblicz szerokość jednego znaku
            char_width = c.stringWidth('a', 'Arial', font_size)
            # Oblicz liczbę znaków, które zmieszczą się w jednej linii
            max_chars = max_width // char_width
            return int(max_chars)

        # Obliczamy maksymalną długość tytułu w jednej linii
        title_font_size = 25
        max_title_length = get_max_title_length(c, title_font_size, width - 100)

        # Skracamy tytuł, jeśli jest za długi
        if len(description_legend) > max_title_length:
            description_legend = description_legend[:max_title_length]
            self.ids.description_input_legend.text = description_legend
            self.ids.description_input_legend.disabled = True  # Zablokowanie edycji

        # Dodaj opis pod obrazkiem
        text_x = 50
        text_y = img_y - 80

        c.setFont("Arial", title_font_size)
        c.drawString(text_x, text_y, "Tytuł:")
        c.setFont("Arial", 16)
        text_lines = description_legend.split('\n')
        for i, line in enumerate(text_lines):
            c.drawString(text_x, text_y - 25 * (i + 1), line)

        # Dodaj opis pod obrazkiem
        text_x = 50
        text_y = img_y - 140

        # Oblicz maksymalną liczbę linii opisu
        max_lines = (height - img_y - 180) // 25  # 180 = marginesy i tytuł
        max_lines = int(max_lines)

        # Skracamy opis do odpowiedniej liczby linii
        lines = []
        line = ""
        for word in description.split():
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, "Arial", 16) < (width - 100):  # Sprawdzenie szerokości
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        # Ograniczamy liczbę linii
        lines = lines[:max_lines]

        c.setFont("Arial", 25)
        c.drawString(text_x, text_y, "Opis:")
        c.setFont("Arial", 16)
        lines = description.split('\n')
        for i, line in enumerate(lines):
            c.drawString(text_x, text_y - 25 * (i + 1), line)

        c.showPage()
        c.save()

        print(f"✅ PDF zapisany jako {pdf_filename}")


class PaintWidget(Widget):

    current_color = ListProperty([1, 0, 0, 1])  # domyślnie czerwony
    line_width = NumericProperty(2)
    tool = StringProperty("free")  # domyślnie "free" = pędze
    actions = []
    def set_color(self, rgba):
        self.current_color = rgba
    def clear_canvas(self):
        self.canvas.clear()
    def undo(self):
        if self.actions:
            last = self.actions.pop()
            self.canvas.remove(last)
    def set_tool(self, tool_name):
            self.tool = tool_name

    def set_line_width(self, width):
        self.line_width = int(width)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        with self.canvas:
            Color(*self.current_color)

            if self.tool == "free":
                line = Line(points=(touch.x, touch.y), width=self.line_width)
                touch.ud["line"] = line
                self.actions.append(line)

            elif self.tool == "line":
                touch.ud["start_pos"] = (touch.x, touch.y)
                line_shape = Line(points=[touch.x, touch.y, touch.x, touch.y],
                                  width=self.line_width)
                touch.ud["shape"] = line_shape
                self.actions.append(line_shape)

            elif self.tool == "circle":
                circle_shape = Line(circle=(touch.x, touch.y, 1),
                                    width=self.line_width)
                touch.ud["shape"] = circle_shape
                touch.ud["circle_center"] = (touch.x, touch.y)
                self.actions.append(circle_shape)

            elif self.tool == "rect":
                touch.ud["start_pos"] = (touch.x, touch.y)
                rect_shape = Line(rectangle=(touch.x, touch.y, 1, 1),
                                  width=self.line_width)
                touch.ud["shape"] = rect_shape
                self.actions.append(rect_shape)
        return True
    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)

        if self.tool == "free" and "line" in touch.ud:
            touch.ud["line"].points += [touch.x, touch.y]

        elif self.tool == "line" and "shape" in touch.ud:
            x0, y0 = touch.ud["start_pos"]
            touch.ud["shape"].points = [x0, y0, touch.x, touch.y]

        elif self.tool == "rect" and "shape" in touch.ud:
            x0, y0 = touch.ud["start_pos"]  # pobieramy zapamiętany punkt początkowy
            w = touch.x - x0
            h = touch.y - y0
            touch.ud["shape"].rectangle = (x0, y0, w, h)

        elif self.tool == "circle" and "shape" in touch.ud:
            cx, cy = touch.ud["circle_center"]
            r = ((touch.x - cx) ** 2 + (touch.y - cy) ** 2) ** 0.5
            touch.ud["shape"].circle = (cx, cy, r)
        return True
   # def on_touch_move(self, touch):
   #     if 'line' in touch.ud:
   #         touch.ud['line'].points += [touch.x, touch.y]
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
