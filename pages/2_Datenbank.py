import cv2 as cv
import streamlit as st
import importlib.util
import matplotlib.pyplot as plt
import numpy as np
import os.path
import os
import glob
from joblib import Parallel, delayed
from streamlit_js_eval import streamlit_js_eval
from PIL import Image, ImageFilter
import base64
from io import BytesIO

# Absoluter oder relativer Pfad zur Datei
#import bildverarbeitungFunction
file_path = os.path.join(os.path.dirname(__file__), '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/bildverarbeitungFunction.py')

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("bildverarbeitungFunction", file_path)
bvf = importlib.util.module_from_spec(spec)  # Alias `bvf` für das Modul
spec.loader.exec_module(bvf)

#image_width = 120

#---------------------------------------------------------
# Page Setup
st.set_page_config(
    layout="wide",
    page_title = "KI Textil",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)
#---------------------------------------------------------
#---------------------------------------------------------
#Funktion zum Erhalt der Datenbankauswahl
def getArrayfordatabank(datenbank, FlachsReal, SeideReal, rWolleReal, merzWolleReal, FlachsSynt, SeideSynt, rWolleSynt,
                        merzWolleSynt, TussahReal, WolleReal, ViskoseReal, TussahSynt, WolleSynt, ViskoseSynt):
    datenbank.clear()

    if FlachsReal == True:
        datenbank.append('FlachsReal')
    if SeideReal == True:
        datenbank.append('SeideReal')
    if rWolleReal == True:
        datenbank.append('rWolleReal')
    if merzWolleReal == True:
        datenbank.append('merzWolleReal')
    if FlachsSynt == True:
        datenbank.append('FlachsSynt')
    if SeideSynt == True:
        datenbank.append('SeideSynt')
    if rWolleSynt == True:
        datenbank.append('rWolleSynt')
    if merzWolleSynt == True:
        datenbank.append('merzWolleSynt')
    if TussahReal == True:
        datenbank.append('TussahReal')
    if WolleReal == True:
        datenbank.append('WolleReal')
    if ViskoseReal == True:
        datenbank.append('ViskoseReal')
    if TussahSynt == True:
        datenbank.append('TussahSynt')
    if WolleSynt == True:
        datenbank.append('WolleSynt')
    if ViskoseSynt == True:
        datenbank.append('ViskoseSynt')

    return datenbank

def changepicturetosee(link, screen):
    image = Image.open(link)
    try:
        if screen < 800:
            newimage = image.resize((120, 80))
        elif screen > 800 and screen < 1300:
            newimage = image.resize((150, 100))
        elif screen > 1300:
            newimage = image.resize((250, 200))
        return newimage
    except:
        return image



datenbank = []
datenbank_bilderPath = []
screen = streamlit_js_eval(js_expressions='screen.width') # Bildschirmgröße
DBKlassen = ["Flachs","Maulbeerseide","Rohbaumwolle","merzerisierte Baumwolle","Tussahseide","Viskose","Wolle"]
DBOrdner = ["Real","Synthetisch"]

if "datenbank" not in st.session_state:
    st.session_state.datenbank = []
    st.session_state.datenbank = datenbank
if "datenbank_bilderPath" not in st.session_state:
    st.session_state.datenbank_bilderPath = []
    st.session_state.datenbank_bilderPath = datenbank_bilderPath
if "datenbank_set" not in st.session_state:
    st.session_state.datenbank_set = False
    # wichtig für die PDF



#---------------------------------------------------------
#---------------------------------------------------------

st.title("Datenbank")

#---------------------------------------------------------
#---------------------------------------------------------
# Anleitung
# Lese das App-Theme aus
from streamlit_theme import st_theme
theme = st_theme()
backgroundcolor = theme['backgroundColor']
#st.write(theme['backgroundColor'])

# Fester Header
header = st.container()
header.subheader("Anleitung")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)


### Custom CSS for the sticky header
st.markdown(
    f"""
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {{
            position: sticky;
            top: 2.875rem;
            background-color: {backgroundcolor};
            z-index: 999;
        }}
        .fixed-header {{
            border-bottom: 0px solid black;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


#---------------------------------------------------------
# Initialisieren, falls noch nicht vorhanden
if "Anleitung_int_Datenbank" not in st.session_state:
    st.session_state.Anleitung_int_Datenbank = 0

Anleitung = [
        "Anleitung",
        "1. Wähle die gewünschten Daten aus, indem du die Checkboxen der jeweiligen Klassen aktivierst.",
        "2. Du kannst zwischen realen und synthetischen Daten wählen – alle auswählen, abwählen oder individuell kombinieren. Die Entscheidung liegt bei dir.",
        "3. Sobald unten angezeigt wird, dass die Daten erfolgreich ausgewählt wurden, kannst du zur nächsten Seite fortfahren.",
    ]


# Anzeige
header.info(Anleitung[st.session_state.Anleitung_int_Datenbank], icon="ℹ️", width="stretch")


with header.form("Anleitung"):

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.Anleitung_int_Datenbank > 0:
            zurück_hide = False
        else:
            zurück_hide = True
        if st.form_submit_button("← zurück", use_container_width=True, disabled=zurück_hide):
            st.session_state.Anleitung_int_Datenbank -= 1

    with col2:
        if st.session_state.Anleitung_int_Datenbank < len(Anleitung) - 1:
            if st.form_submit_button("vor →", use_container_width=True):
                st.session_state.Anleitung_int_Datenbank += 1


#---------------------------------------------------------
#---------------------------------------------------------

st.subheader("Willkommen bei der Datenbank von FibreAI.")
st.write("In der Datenbank kann sich angeschaut werden wieviele Querschnittsbilder bisher von den unterschiedlichen Faserarten erstellt wurden. Die Datenbank wird dabei regelmäßig aktualisiert und erweitert.")
st.subheader("Und wozu das ganze?")
st.write("Die Daten aus der Datenbank können für das Training eines neuen oder eigenen Modells genutzt werden.")

#Multiselect für die einzelnen Klassen, um Datenbank zu kreieren
st.subheader("Auswahl der einzelnen Klassen:")

# Reale Daten - WP_Textil
st.subheader("Reale Daten")
A1, A2, A3, A4, A5, A6, A7 = st.columns(7)
link = "/opt/lampp/htdocs/Webseite_SHK/streamlit/BildDatenbank/Real/"
with A1:
    newlink = link + "Flachs/FL0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image) #Flachs
with A2:
    newlink = link + "merzerisierte Baumwolle/MB0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with A3:
    newlink = link + "Rohbaumwolle/RB0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with A4:
    newlink = link + "Maulbeerseide/MS0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with A5:
    newlink = link + "Tussahseide/TS0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with A6:
    newlink = link + "Viskose/VS0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with A7:
    newlink = link + "Wolle/WO0001.tif"
    image = changepicturetosee(newlink, screen)
    st.image(image)

A1, A2, A3, A4, A5, A6, A7 = st.columns(7)
BilderPath = "/opt/lampp/htdocs/Webseite_SHK/streamlit/BildDatenbank/Real/"
with A1:
    bvf.templateStrings(DBKlassen, BilderPath + "Flachs")
with A2:
    bvf.templateStrings(DBKlassen, BilderPath + "merzerisierte Baumwolle")
with A3:
    bvf.templateStrings(DBKlassen, BilderPath + "Rohbaumwolle")
with A4:
    bvf.templateStrings(DBKlassen, BilderPath + "Maulbeerseide")
with A5:
    bvf.templateStrings(DBKlassen, BilderPath +  "Tussahseide")
with A6:
    bvf.templateStrings(DBKlassen, BilderPath + "Viskose")
with A7:
    bvf.templateStrings(DBKlassen, BilderPath + "Wolle")

A1, A2, A3, A4, A5, A6, A7 = st.columns(7)
with A1:
    FlachsReal = st.checkbox("Flachs\n\n(real)", value=True, key="FlachsReal")
with A2:
    merzWolleReal = st.checkbox("merzerisierte\n\nBaumwolle\n\n(real)", value=True,key="merzWolleReal")
with A3:
    rWolleReal = st.checkbox("Rohbaumwolle\n\n(real)", value=True,key="rWolleReal")
with A4:
    SeideReal = st.checkbox("Maulbeerseide\n\n(real)", value=True,key="SeideReal")
with A5:
    TussahReal = st.checkbox("Tussahseide\n\n(real)", value=False, key="TussahReal")
with A6:
    ViskoseReal = st.checkbox("Viskose\n\n(real)", value=False, key="ViskoseReal")
with A7:
    WolleReal = st.checkbox("Wolle\n\n(real)", value=False, key="WolleReal")

# Synthetische Daten - Synthetic
st.subheader("Synthetische Daten")
link = "/opt/lampp/htdocs/Webseite_SHK/streamlit/BildDatenbank/Synthetisch/"
B1, B2, B3, B4, B5, B6, B7 = st.columns(7)
with B1:
    newlink = link + "Flachs/FL0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B2:
    newlink = link + "merzerisierte Baumwolle/MW0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B3:
    newlink = link + "Rohbaumwolle/RW0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B4:
    newlink = link + "Maulbeerseide/MS0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B5:
    newlink = link + "Tussahseide/TS0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B6:
    newlink = link + "Viskose/VS0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)
with B7:
    newlink = link + "Wolle/WO0001.jpg"
    image = changepicturetosee(newlink, screen)
    st.image(image)


B1, B2, B3, B4, B5, B6, B7 = st.columns(7)
BilderPath = "/opt/lampp/htdocs/Webseite_SHK/streamlit/BildDatenbank/Synthetisch/"
with B1:
    bvf.templateStrings(DBKlassen, BilderPath + "Flachs")
with B2:
    bvf.templateStrings(DBKlassen, BilderPath + "merzerisierte Baumwolle")
with B3:
    bvf.templateStrings(DBKlassen, BilderPath + "Rohbaumwolle")
with B4:
    bvf.templateStrings(DBKlassen, BilderPath + "Maulbeerseide")
with B5:
    bvf.templateStrings(DBKlassen, BilderPath + "Tussahseide")
with B6:
    bvf.templateStrings(DBKlassen, BilderPath + "Viskose")
with B7:
    bvf.templateStrings(DBKlassen, BilderPath + "Wolle")


B1, B2, B3, B4, B5, B6, B7 = st.columns(7)
with B1:
    FlachsSynt = st.checkbox("Flachs\n\n(synthetisch)", value=False, key="FlachsSynt")
with B2:
    merzWolleSynt = st.checkbox("merzerisierte\n\nBaumwolle\n\n(synthetisch)", value=False, key="merzWolleSynt")
with B3:
    rWolleSynt = st.checkbox("Rohbaumwolle\n\n(synthetisch)", value=False, key="rWolleSynt")
with B4:
    SeideSynt = st.checkbox("Maulbeerseide\n\n(synthetisch)", value=False, key="SeideSynt")
# Synthetische Daten - weitere Klassen
with B5:
    TussahSynt = st.checkbox("Tussahseide\n\n(synthetisch)", value=False, key="TussahSynt")
with B6:
    ViskoseSynt = st.checkbox("Viskose(synthetisch)", value=False, key="ViskoseSynt")
with B7:
    WolleSynt = st.checkbox("Wolle\n\n(synthetisch)", value=False, key="WolleSynt")



#Wichtig für die Übergabe an Seite 3
datenbank = getArrayfordatabank(datenbank, FlachsReal, SeideReal, rWolleReal, merzWolleReal, FlachsSynt, SeideSynt, rWolleSynt, merzWolleSynt, TussahReal, WolleReal, ViskoseReal, TussahSynt, WolleSynt, ViskoseSynt)
st.session_state.datenbank = datenbank
datenbank_bilderPath = bvf.getdatenbankBilderPath(datenbank_bilderPath, datenbank,1)
st.session_state.datenbank_bilderPath = datenbank_bilderPath
if datenbank:
    st.session_state.datenbank_set = True

#Mitteilung für die Aushwal der Datenbank
if not datenbank:
    st.warning("Es wurde keine Bild-Datenbank ausgewählt, wähle bitte eine Datenbank aus.")
if datenbank:
    st.success("Es wurde mind. eine Bild-Datenbank ausgewählt, fahre auf der nächsten Seite fort.")

col1, col2 = st.columns(2)
with col1:
    st.write("Ausgewählte Datenbanken:", st.session_state.datenbank)
with col2:
    st.write("Datenbank-Bilderpath:", st.session_state.datenbank_bilderPath)

#-------------------------------------------------------------------------------------------
### Seitenleiste
image = Image.open("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png")
st.logo(image, icon_image=image, size="large")


