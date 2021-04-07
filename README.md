Knihovník
---------
This is the GitHub repository of the *Knihovník* application, which generates bibliographic data about books in photos. The application detects books in the image using the [YOLOv4](https://github.com/hunglc007/tensorflow-yolov4-tflite) neural network and uses the [Tesseract](https://github.com/tesseract-ocr/tesseract) program to detect text. It searches for books in the [Open Library](https://openlibrary.org/developers/dumps) book database and generates bibliographic data using [isbntools](https://github.com/xlcnd/isbnlib). During the development of the application, some parts proved to be problematic and would need to be further improved. *Knihovník* also provides a graphical user interface based on the [Kivy](https://kivy.org) library.

**Instalace**

Z releasu lze stáhnout připravený zip soubor. Po rozbalení stačí spustit program *knihovnik.exe* z adresáře knihovnik.

Instalace ze zdrojových kódů:

Nejdřív je třeba naklonovat zdrojové kódy:
```bash
$ git clone https://github.com/Benyeemin/maturitni_projekt_Benjamin_Verner
```
Pro správný chod aplikace je nutné nejprve nainstalovat program [Tesseract](https://github.com/tesseract-ocr/tesseract).
Např. na Ubuntu lze využít balíček tesseract-ocr, na Windows je možné instalovat pomocí [Chocolatey](https://chocolatey.org/):
```powershell
PS C:\> choco install -y tesseract 
```
Na unixových systémech je třeba ještě nainstalovat některé knihovny (které nejsou obsaženy v binárních pypi balíčcích pro linux):

knihovna [zbar](http://zbar.sourceforge.net/)

program xclip

Na Ubuntu lze použít následující příkaz:

$ sudo apt install libzbar0 xclip  tesseract-ocr

Pak je třeba vytvořit virtuální Python prostředí a nainstalovat potřebné balíčky, na kterých aplikace závisí:
```bash
$ python3 -m virtualenv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```
Knihovna Kivy obsahovala v době vydání chybu, která znemožňovala práci s kamerou. Pokud program nebude fungovat
(spadne), je možné tuto chybu vyřešit aplikací záplaty:
```bash
$ patch --strip 1 < kivy-openc2.diff
```
Dále je třeba vytvořit soubor *server\_connection\_info* a uložit do něj přístupové údaje k SQL databázi
obsahující seznam knih a autorů. 

V aktivovaném prostředí lze aplikaci spustit pomocí příkazu:
```bash
(venv) $ python application_ui.py
```
