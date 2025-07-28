import os
import streamlit as st
import numpy as np
import math
import PIL
import glob
from PIL import Image
import base64
from io import BytesIO
import tensorflow as tf
from pathlib import Path
from tkinter import filedialog
import importlib.util
from ultralytics import YOLO
from fpdf import FPDF
import cv2
import time

# Absoluter oder relativer Pfad zur Datei
#import trainModelPython
file_path = os.path.join(os.path.dirname(__file__), '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/pdf.py')
# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("pdf", file_path)
ppdf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ppdf)


#------------------------------------------------------------------------------------------

# Absoluter oder relativer Pfad zur Datei
#import trainModelPython
file_path = os.path.join(os.path.dirname(__file__), '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/trainModelPython.py')

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("trainModelPython", file_path)
tmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tmp)

#------------------------------------------------------------------------------------------
# Page Setup
st.set_page_config(
    page_title="KI Textil",
    layout="wide",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)

#------------------------------------------------------------------------------------------
# Session State Initialisierung
# Modell laden
img_size = 64
imageWidth = 150
#st.session_state.pathtomodel = "/home/alen/.pyenv/runs/classify/train79"
DBKlassen = ["Flachs", "Maulbeerseide", "Rohbaumwolle", "merzerisierte Baumwolle", "Tussahseide", "Viskose", "Wolle"]

if "model_classes" not in st.session_state:
    st.session_state.model_classes = []
if "img_size" not in st.session_state:
    st.session_state.img_size = 64
    img_size = st.session_state.img_size
if "pathtomodel" not in st.session_state:
    st.session_state.pathtomodel = None
if "choose_folder" not in st.session_state:
    st.session_state.choose_folder = False
if "trainedModel" not in st.session_state:
    st.session_state.trainedModel = False
    st.session_state.ki_available = False
    st.session_state.ki_upload_available = False
    st.session_state.start_analyse = True
if "zielPath" not in st.session_state:
    st.session_state.zielPath = None
if "ki_upload" not in st.session_state:
    st.session_state.ki_upload = None
if "ki_faseranalyse_set" not in st.session_state:
    st.session_state.ki_faseranalyse_set = False

try:
    pathtomodel = st.session_state.pathtomodel
    #pathtomodel = os.path.join(pathtomodel, "weights", "best.pt")
    st.session_state.trainedModel = YOLO(pathtomodel)
    st.session_state.model_classes = DBKlassen
    st.session_state.ki_available = True
    st.session_state.ki_upload_available = True
    st.session_state.start_analyse = False
    img_size = st.session_state.img_size
except Exception as e:
    pathtomodel = ""
    st.session_state.trainedModel = None
    #st.write(f"Fehler beim Laden des Modells: {e}")
    st.session_state.ki_available = False
    st.session_state.ki_upload_available = False
    st.session_state.start_analyse = True
    st.session_state.img_size = 64

yolo_version = ""
data_dir = ""

if st.session_state.pathtomodel:
    #st.info(st.session_state.pathtomodel)
    data_dir, yolo_version = tmp.readYoloArgs(pathtomodel)
    pathtomodel = os.path.join(st.session_state.pathtomodel, "weights", "best.pt")
    st.session_state.trainedModel = YOLO(pathtomodel)
    st.session_state.ki_available = True
    st.session_state.ki_upload_available = True
    st.session_state.start_analyse = False
    img_size = st.session_state.img_size

#st.session_state.pathtomodel = "/home/alen/.pyenv/runs/classify/train91"

#------------------------------------------------------------------------------------------
# Funktionen

def changeClassNameinFaserAnalyse(classname):
    try:
        #st.write(classname)
        print(classname)
        if not isinstance(classname, str) or not classname.strip():
            return "Unbekannt"

        # ändert nur den Klassennamen in Faseranalyse
        newname = classname.split(" ")
        if len(newname) >= 3:
            firstname = newname[0] #Klassenname
            secondname = newname[1].capitalize() #Klassenname2 (bei merz. Baumwolle)
            thirdname = newname[2].capitalize() # Real, Synt
            class_name = firstname + " " + secondname
        elif len(newname) < 3:
            firstname = newname[0].capitalize()  # Klassenname
            secondname = newname[1].capitalize()  # Real, Synt
            class_name = firstname
        elif len(newname) == 1:
            class_name = newname[0].capitalize()
        else:
            class_name = "Unbekannt"

        return class_name
    except:
        return classname

def showClassImage(predicted):
    """Zeigt das Bild der vorhergesagten Klasse an."""
    imageWidth = 260
    if predicted:
        #st.image(f"/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/{predicted}.png", use_container_width=True)
        st.image(f"/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/{predicted}.png",
                 width=imageWidth)
    else:
        st.image("", use_container_width=True)

def startAnalyse(model, uploaded_image, img_size):
    """Führt die Analyse durch und zeigt Ergebnisse an."""
    try:
        # Sicherstellen, dass das Bild im RGB-Format ist

        uploaded_image = Image.open(uploaded_image).convert("RGB")
        #img = uploaded_image.resize((img_size, img_size))
        print("image Size = ", img_size)
        img = uploaded_image
        results = list(model(img))
        names_dict = results[0].names
        probs = results[0].probs.data.numpy().tolist()


    except Exception as e:
        st.error(f"Fehler bei der Vorhersage: {e}")
        probs = None
        predicted_class = None

    if probs is not None:
        #col1, col2 = st.columns(2)
        print("Probs: ",probs)
        predicted_class = str(names_dict[np.argmax(probs)])
        predicted_class = changeClassNameinFaserAnalyse(predicted_class)
        print("Predicted Class: ", predicted_class)
        #st.success(f"☑️ Vorhersage: {predicted_class}")
        text = [] #Ausgabe String
        for i, p in enumerate(probs):
            class_names = model.names[i]
            text.append(f"{class_names}: {p:.0%}")
        for i in range(len(text)):
            if predicted_class in text[i]:
                st.info("▶️ " + text[i])
            else:
                st.info(text[i])
        return predicted_class


#------------------------------------------------------------------------------------------
# Hauptbereich

st.title("KI-Faseranalyse")


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
if "Anleitung_int_KI_Faseranalyse" not in st.session_state:
    st.session_state.Anleitung_int_KI_Faseranalyse = 0

Anleitung = [
        "Anleitung",
        "1. Lade das KI-Modell hoch (falls erforderlich), indem du den :blue[vorverarbeiteten Bilderordner] über den Button :blue['Upload KI: Bilderordner wählen'] auswählst.",
        "2. Lade anschließend das Bild hoch, das für die :blue[Faseranalyse] verwendet werden soll – idealerweise aus dem Ordner :orange['test'].",
        "3. Starte die Analyse über den Button :blue['Analyse starten ➡️ Prognose & Wahrscheinlichkeit']."
    ]

# Anzeige
header.info(Anleitung[st.session_state.Anleitung_int_KI_Faseranalyse], icon="ℹ️", width="stretch")


with header.form("Anleitung"):
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.Anleitung_int_KI_Faseranalyse > 0:
            zurück_hide = False
        else:
            zurück_hide = True
        if st.form_submit_button("← zurück", use_container_width=True, disabled=zurück_hide):
            st.session_state.Anleitung_int_KI_Faseranalyse -= 1

    with col2:
        if st.session_state.Anleitung_int_KI_Faseranalyse < len(Anleitung) - 1:
            if st.form_submit_button("vor →", use_container_width=True):
                st.session_state.Anleitung_int_KI_Faseranalyse += 1


#---------------------------------------------------------
#---------------------------------------------------------
st.subheader("Upload KI 🤖")
col1, col2 = st.columns(2)
with col2:
    if st.session_state.pathtomodel:
        st.info(
            f"Aktuell hochgeladene KI: \n {st.session_state.pathtomodel} \n\n YOLO-Version: {yolo_version}")  # zeigt die Info KI-Path unterhalb Subheader

    # Schritt 1: Buttonklick speichern
    if not st.session_state.pathtomodel:
        st.markdown(
            ' ##### Falls :red[KI-Not-Activated], wähle hier das KI-Model durch die Auswahl des Bildordners, welches du beim Training in KI-Training verwendet hast. ',
            unsafe_allow_html=True,
            help=None)
        #ki_upload_help = "Mit diesem Button lädst Du die KI hoch, wähle lediglich den Bildordner aus, den Du zuvor beim **KI-Training** verwendet hast. \n\n Beispiel: /home/usr/Downloads/FibreAI_XXXX-XX-XX"
        #ki_upload = st.button("Upload KI: Bildordner auswählen", help=ki_upload_help)
        #if ki_upload:
        #    st.session_state.choose_folder = True

        # Schritt 2: Wenn Button gedrückt wurde -> Dialog öffnen
        if st.session_state.choose_folder:
            if os.name == 'nt':  # Windows
                initial_dir = "C:/"
            elif os.name == 'posix':  # Unix oder Linux (inkl. macOS)
                initial_dir = "~/"
            else:
                initial_dir = "/"

            folder_selected = filedialog.askdirectory(initialdir=initial_dir)

            if folder_selected:
                pathtomodel = os.path.join(folder_selected, "model_saved.txt")
                if os.path.exists(pathtomodel):
                    st.session_state.pathtomodel = pathtomodel
                    with open(pathtomodel) as f:
                        model_path = f.read()
                        st.session_state.pathtomodel = model_path
                        #with col1:
                            #st.success(f"KI wurde erfolgreich geladen")
                        data_dir, yolo_version = tmp.readYoloArgs(model_path)
                        with col2:
                            st.info(
                                f"Aktuell hochgeladene KI: \n\n {st.session_state.pathtomodel} \n YOLO-Version: {yolo_version}")  # zeigt Info nach erfolgreichem hochladen
                        st.session_state.ki_available = True
                        st.rerun()
                else:
                    st.warning("Es wurde kein trainiertes Modell gefunden. Bitte versuche es erneut.")
                    st.session_state.ki_available = False

            # Danach Button-Zustand zurücksetzen
            st.session_state.choose_folder = False
with col1:
    # KI Statusbild anzeigen
    # use_container_width=True
    if st.session_state.ki_available:
        st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/KI_Schrift_Act.png", width=imageWidth)
        # st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/KI_Schrift_Act.png", use_container_width=True)
    else:
        st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/KI_Schrift_Nact.png", width=imageWidth)
        # st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/KI_Schrift_Nact.png", use_container_width=True)

ki_upload_help = "Mit diesem Button lädst Du die KI hoch, wähle lediglich den Bildordner aus, den Du zuvor beim **KI-Training** verwendet hast. \n\n Beispiel: /home/usr/Downloads/FibreAI_XXXX-XX-XX"
st.session_state.ki_upload = st.button("Upload KI: Bildordner auswählen", help=ki_upload_help, use_container_width=True)
ki_upload = st.session_state.ki_upload
if ki_upload:
    st.session_state.choose_folder = True
    st.rerun()




# Bild hochladen
st.subheader("Upload Picture 📷")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        ' ##### Lade hier das Bild für die :blue[Faseranalyse] hoch. In der Regel sollte es ein unbekanntes Bild sein. \n\n Im Bildordner aus der Datenvorbereitung, findest unter **"test"** die Bilder zum hochladen.',
        unsafe_allow_html=True,
        help=None)
    if st.session_state.pathtomodel and data_dir is not None:
        st.write(f'**"test":** in :blue[{data_dir}] möglicherweise?')


with col2:
    st.session_state.uploaded_file = st.file_uploader(
        "", accept_multiple_files=False, type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'],
        label_visibility="hidden",
    )
    if st.session_state.uploaded_file is not None:
        #st.session_state.image = Image.open(st.session_state.uploaded_file)
        st.session_state.image = st.session_state.uploaded_file
        st.image(st.session_state.image, width=imageWidth)

#Analyse Bilder per KI
st.subheader("Analyse 🔍 starten")
start_analyse_button_help = "Mit diesem Button startest Du die Faseranalyse, sofern das KI-Model und ein Bild hochgeladen wurde."
start_analyse_button = st.button("Analyse starten ➡️ Prognose & Wahrscheinlichkeit",
                                 disabled=st.session_state.start_analyse,
                                 help = start_analyse_button_help,
                                 use_container_width=True
                                 )
# Erstelle PDF
if st.button("Dokumentationsbericht erstellen",
             disabled=st.session_state.start_analyse,
             help="erstellt eine PDF mit allen Vorhersagen, für alle Test-Bilder",
             use_container_width=True):
    report_path = os.path.join(data_dir, "Dokumentationsbericht.pdf")
    ppdf.createFancyReport(report_path)
    st.success("PDF erstellt!")

col1, col2 = st.columns(2)
with col1:
    # Start Button für die Analyse
    if start_analyse_button:
        #st.write(f"Typ von image: {type(st.session_state.uploaded_file)}")
        st.session_state.ki_faseranalyse_set = True #wichtig für die PDF
        if not st.session_state.uploaded_file:
            with col2:
                st.warning("Bitte lade zuerst ein Bild hoch!")
        else:
            with col1:
                #st.subheader("Analyseergebnisse 🔍")
                if st.session_state.trainedModel:
                    predicted_class = startAnalyse(st.session_state.trainedModel, st.session_state.uploaded_file, img_size)
                with col2:
                    #st.success(f"☑️ Vorhersage: {predicted_class}")
                    showClassImage(predicted_class)



#------------------------------------------------------------------------------------------
# Seitenleiste

### Seitenleiste
# Öffne das Bild
image = Image.open("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png")

st.logo(image, icon_image=image, size="large")



