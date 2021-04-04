# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivy.uix import filechooser
import pytesseract

block_cipher = None


a = Analysis(['C:\\Users\\Petr\\PycharmProjects\\BRAppFolder\\application_ui.py'],
             pathex=['C:\\Users\\Petr\\PycharmProjects\\BookRecognitionApp'],
             binaries=[('C:\Program Files\Tesseract-OCR\*', 'Tesseract'),
                       ('C:/Program Files/Tesseract-OCR/tessdata/*', 'Tesseract/tessdata'),
                       ('C:/Users/Petr/PycharmProjects/BookRecognitionApp/venv/Lib/site-packages/pyzbar/*dll','pyzbar/'),
                       ('C:/Users/Petr/PycharmProjects/yolov4-416/*','yolov4-416'),
                       ('C:/Users/Petr/PycharmProjects/yolov4-416/variables/*','yolov4-416/variables')],
             hiddenimports=['win32timezone','pytesseract','tensorflow'],
             datas=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Book Recognition',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='C:/Users/Petr/PycharmProjects/BRAppFolder/icon.ico')
coll = COLLECT(exe, Tree('C:/Users/Petr/PycharmProjects/BRAppFolder'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='book_recognition')
