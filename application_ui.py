import time, sys
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

import image_processing
import information_fetcher
import detect
import method1_SQL as sqlsearch
import barcode_finder

if getattr(sys, 'frozen', False):
    OUTPUT_DIR=Path(sys._MEIPASS)
else:
    OUTPUT_DIR=Path(__file__).parent

Builder.load_string('''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        Camera:
            id: camera
            resolution: (640, 480)
            play: True
        Button:
            text: 'Read from camera'
            size_hint_y: None
            height: '48dp'
            on_release:
                root.capture()
                root.read_from_image()
                root.manager.current = 'FinalScreen'
        Button:
            text: 'Scan barcode'
            size_hint_y: None
            height: '48dp'
            on_release:
                root.capture()
                root.read_from_barcode()
                root.manager.current = 'FinalScreen'
        Button:
            text: 'select image'
            size_hint_y: None
            height: '48dp'
            on_release:
                root.show_load()
        Button:
            text: 'read from selected image'
            size_hint_y: None
            height: '48dp'
            on_release:
                root.read_from_image()
                root.manager.current = 'FinalScreen'
        Button:
            text: 'scan barcodes from selected image'
            size_hint_y: None
            height: '48dp'
            on_release:
                root.read_from_barcode()
                root.manager.current = 'FinalScreen'        
<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)
<FinalScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: output
            halign: 'center'
            text_size: self.width, None
        Button:
            text: 'Show next book'
            size_hint_y: None
            height: '48dp'
            on_release: root.next_book()
        Button:
            text: 'Copy to clipboard'
            size_hint_y: None
            height: '48dp'
            on_release: root.copy_to_clipboard()
        Button:
            text: 'Go back'
            size_hint_y: None
            height: '48dp'
            on_release: root.manager.current = 'MainScreen'
        Button:
            text: 'End'
            size_hint_y: None
            height: '48dp'
            on_release: app.stop()
    BoxLayout:
        Button:
            text: 'previous book'
            size_hint_y: None
            height: '48dp'
            on_release: root.previous_book()
        Button:
            text: 'next book'
            size_hint_y: None
            height: '48dp'
            on_release: root.next_book()
''')

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class MainScreen(Screen):
    img_name = ''
    img_path = ''

    def __init__(self, fsw):
        super(MainScreen, self).__init__(name='MainScreen')
        self.final_screen = fsw

    def dismiss_popup(self):
        self._popup.dismiss()

    def capture(self):
        camera = self.ids['camera']
        MainScreen.img_name = time.strftime("%Y%m%d_%H%M%S")
        MainScreen.img_path = str(OUTPUT_DIR / f"IMG_{self.img_name}.png")
        camera.export_to_png(MainScreen.img_path)

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        try:
            MainScreen.img_path = str(Path(str(path)) / str(filename[0]))
        except:
            pass
        self.dismiss_popup()

    def read_from_image(self):
        FinalScreen.output = []
        FinalScreen.book_number = 0
        #detection using cv2 : text_list = image_processing.find_books(MainScreen.img_path)
        text_list = detect.find_books(MainScreen.img_path)
        if text_list is not None:
            for text in text_list:
                if len(text) > 0:
                    FinalScreen.book_number += 1
                    book_title, book_author = sqlsearch.search(text)
                    if book_title is not None:
                        string = information_fetcher.info_from_image(book_title, book_author, FinalScreen.book_number)
                        FinalScreen.output.append('\n' + string)
                    else:
                        FinalScreen.output.append('Server connection error: check your internet connection.')
                        self.final_screen.ids.output.text = FinalScreen.output[0]
                        return
            if FinalScreen.book_number == 0:
                FinalScreen.output.append('0 books found.')
        else:
            FinalScreen.output.append('Invalid file.')
        self.final_screen.ids.output.text = FinalScreen.output[0]

    def read_from_barcode(self):
        FinalScreen.output = []
        FinalScreen.book_number = 0
        barcodes = barcode_finder.find_barcodes(MainScreen.img_path)
        if barcodes is not None:
            for barcode in barcodes:
                FinalScreen.book_number += 1
                string = information_fetcher.info_from_barcode(barcode, FinalScreen.book_number)
                FinalScreen.output.append('\n' + string)
            if FinalScreen.book_number == 0:
                FinalScreen.output.append('0 barcodes found.')
        else:
            FinalScreen.output.append('Invalid file.')
        self.final_screen.ids.output.text = FinalScreen.output[0]

class FinalScreen(Screen):
    output = []
    book_number = 0
    current_book = 1

    def copy_to_clipboard(self):
        Clipboard.copy(self.output[self.current_book-1])

    def next_book(self):
        if self.current_book < self.book_number:
            FinalScreen.current_book += 1
            self.ids.output.text = self.output[self.current_book-1]

    def previous_book(self):
        if self.current_book != 1:
            FinalScreen.current_book -= 1
            self.ids.output.text = self.output[self.current_book-1]


class Application(App):
    def build(self):
        sm = ScreenManager()
        fsw = FinalScreen(name='FinalScreen')
        sm.add_widget(MainScreen(fsw))
        sm.add_widget(fsw)
        return sm

Application().run()