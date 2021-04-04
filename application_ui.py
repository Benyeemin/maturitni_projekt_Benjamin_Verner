import pytesseract, time, sqlite3, psycopg2, pyzbar, cv2, isbnlib
from kivy.app import App
from kivy.lang import Builder
from contextlib import closing
from isbntools.app import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard
import image_processing
import information_fetcher
import SQL_search as sqlsearch
from jnius import autoclass
import Cython

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

Builder.load_string('''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        Camera:
            id: camera
            resolution: (640, 480)
            play: True
        Button:
            text: 'Read from book covers'
            size_hint_y: None
            height: '48dp'
            on_press:
                root.capture()
                read_from_image()
                root.manager.current = 'FinalScreen'
        Button:
            text: 'Scan barcode'
            size_hint_y: None
            height: '48dp'
            on_press:
                root.barcode_capture()
                read_from_barcode()
                root.manager.current = 'FinalScreen'

<FinalScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: output
        Button:
            text: 'Copy to clipboard'
            size_hint_y: None
            height: '48dp'
            on_press: root.copy_to_clipboard()
        Button:
            text: 'Show the output'
            size_hint_y: None
            height: '48dp'
            on_press: root.show_output()
        Button:
            text: 'Go back'
            size_hint_y: None
            height: '48dp'
            on_press: root.return_to_main_screen()
        Button:
            text: 'End'
            size_hint_y: None
            height: '48dp'
            on_press: app.stop()
''')

class MainScreen(Screen):
    img_name = ''

    def capture(self):
        camera = self.ids['camera']
        MainScreen.img_name = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png(f"IMG_{self.img_name}.png")

    def barcode_capture(self):
        camera = self.ids['camera']
        MainScreen.img_name = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png(f"IMG_{self.img_name}.png")

class FinalScreen(Screen):
    output = ''

    def show_output(self):
        self.ids.output.text = self.output

    def copy_to_clipboard(self):
        Clipboard.copy(self.output)

class Application(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='MainScreen'))
        sm.add_widget(FinalScreen(name='FinalScreen'))
        return sm


def read_from_image():
    FinalScreen.output = ''
    book_number = 0
    text_list = image_processing.find_books()
    for text in text_list:
        if len(text_list) > 0:
            book_number += 1
            book_title, book_author = sqlsearch.search(text)
            string = information_fetcher.info_from_image(book_title, book_author, book_number)
            FinalScreen.output += '\n' + string
    if book_number == 0:
        FinalScreen.output = '0 books found. Please recapture the image.'

def read_from_barcode():
    FinalScreen.output = ''
    book_number = 0
    barcodes = image_processing.find_barcodes()
    for barcode in barcodes:
        book_number += 1
        string = information_fetcher.info_from_barcode(barcode, book_number)
        FinalScreen.output += '\n' + string
    if book_number == 0:
        FinalScreen.output = '0 barcodes found.'

Application().run()