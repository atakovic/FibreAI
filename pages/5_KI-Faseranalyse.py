import os

import streamlit as st
import numpy as np
import PIL
from PIL import Image
import base64
from io import BytesIO
import tensorflow as tf
#from tensorflow.keras.applications.vgg16 import preprocess_input
from pathlib import Path
#from tkinter import filedialog
import importlib.util
from ultralytics import YOLO
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
# Page Setup
st.set_page_config(
    page_title="KI Textil",
    layout="wide",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)

#------------------------------------------------------------------------------------------
# Session State Initialisierung
if "trainedModel" not in st.session_state:
    st.session_state.trainedModel = False
    st.session_state.ki_available = False
    st.session_state.ki_upload_available = False
    st.session_state.start_analyse = True

if "model_classes" not in st.session_state:
    st.session_state.model_classes = []

if "img_size" not in st.session_state:
    st.session_state.img_size = 64
    img_size = st.session_state.img_size
if "pathtomodel" not in st.session_state:
    st.session_state.pathtomodel = None


# Modell laden
img_size = 64
#pathtomodel = "/home/alen/.pyenv/runs/classify/train51/weights/best.pt"
DBKlassen = ["Flachs", "Maulbeerseide", "Rohbaumwolle", "merzerisierte Baumwolle", "Tussahseide", "Viskose", "Wolle"]

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
    st.write(f"Fehler beim Laden des Modells: {e}")
    st.session_state.ki_available = False
    st.session_state.ki_upload_available = False
    st.session_state.start_analyse = True
    st.session_state.img_size = 64

#------------------------------------------------------------------------------------------
# Hilfsfunktionen

def changeClassNameinFaserAnalyse(classname):  # ändert nur den Klassennamen in Faseranalyse
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

    return class_name

def showClassImage(predicted):
    """Zeigt das Bild der vorhergesagten Klasse an."""
    imageWidth = 250
    if predicted:
        st.image(f"webpictures/{predicted}.png", width=imageWidth)
    else:
        st.image("", width=imageWidth)


def startAnalyse(model, uploaded_image, img_size):
    """Führt die Analyse durch und zeigt Ergebnisse an."""
    st.write("Starte die Analyse")
    try:
        # Sicherstellen, dass das Bild im RGB-Format ist
        if uploaded_image.mode != "RGB":
            uploaded_image = uploaded_image.convert("RGB")

        img = uploaded_image.resize((img_size, img_size))
        results = list(model(img))
        names_dict = results[0].names
        probs = results[0].probs.data.numpy().tolist()


    except Exception as e:
        st.error(f"Fehler bei der Vorhersage: {e}")
        probs = None
        predicted_class = None

    if probs is not None:
        #col1, col2 = st.columns(2)
        with col2:
            predicted_class = str(names_dict[np.argmax(probs)])
            predicted_class = changeClassNameinFaserAnalyse(predicted_class)
            st.success(f"Vorhersage: {predicted_class}")
            text = [] #Ausgabe String
            for i, p in enumerate(probs):
                class_names = model.names[i]
                text.append(f"{class_names}: {p:.2%}")
            for i in range(len(text)):
                st.info(text[i])
        #with col1:
            showClassImage(predicted_class)



#------------------------------------------------------------------------------------------
# Hauptbereich

st.title("KI-Faseranalyse")

# Schritt 1: Buttonklick speichern
#if "choose_folder" not in st.session_state:
#    st.session_state.choose_folder = False

#if st.button("Bildordner auswählen"):
#    st.session_state.choose_folder = True

# Schritt 2: Wenn Button gedrückt wurde -> Dialog öffnen
#if st.session_state.choose_folder:
#    if os.name == 'nt':  # Windows
#        initial_dir = "C:/"
#    elif os.name == 'posix':  # Unix/Linux/macOS
#        initial_dir = "/home/usr/"
#    else:
#        initial_dir = "/"

#    folder_selected = filedialog.askdirectory(initialdir=initial_dir)

#    if folder_selected:
#        pathtomodel = os.path.join(folder_selected, "model_saved.txt")
#        if os.path.exists(pathtomodel):
#            st.session_state.pathtomodel = pathtomodel
#            with open(pathtomodel) as f:
#                model_path = f.read()
#                st.session_state.pathtomodel = model_path
#                st.success(f"KI wurde erfolgreich geladen")
#        else:
#            st.warning("Du hast kein trainiertes Modell gefunden. Bitte versuche es erneut.")

    # Danach Button-Zustand zurücksetzen
    #st.session_state.choose_folder = False

folder_selected = st.textinput(label="Wähle hier den Bildordner aus, den du beim Training für die KI verwendet hast.", placeholder="/home/usr/meinBilderOrdner")
if folder_selected:
    pathtomodel = os.path.join(folder_selected, "model_saved.txt")
    if os.path.exists(pathtomodel):
            st.session_state.pathtomodel = pathtomodel
            with open(pathtomodel) as f:
                model_path = f.read()
                st.session_state.pathtomodel = model_path
                st.success(f"KI wurde erfolgreich geladen")
        else:
            st.warning("Du hast kein trainiertes Modell gefunden. Bitte versuche es erneut.")
    


if st.session_state.pathtomodel:
    st.info(st.session_state.pathtomodel)
    pathtomodel = os.path.join(st.session_state.pathtomodel, "weights", "best.pt")
    st.session_state.trainedModel = YOLO(pathtomodel)
    st.session_state.ki_available = True
    st.session_state.ki_upload_available = True
    st.session_state.start_analyse = False
    img_size = st.session_state.img_size

col1, col2 = st.columns(2)
with col1:
    imageWidth = 250
    # KI Statusbild anzeigen
    if not st.session_state.ki_available:
        st.image("webpictures/KI_Schrift_Nact.png", width=imageWidth)
    else:
        st.image("webpictures/KI_Schrift_Act.png", width=imageWidth)

    # Analysebereich

    st.subheader("Auswertung")
    st.text("Hier erhältst du die Klassenausgabe und die Wahrscheinlichkeit der Prognose.")

    start_analyse_button = st.button("Analyse starten", disabled=st.session_state.start_analyse)

    if start_analyse_button:
        if not st.session_state.uploaded_file:
            st.warning("Bitte lade zuerst ein Bild hoch!")
        else:
            if st.session_state.trainedModel:
                with st.spinner('Starte die Analyse...'):
                    startAnalyse(st.session_state.trainedModel, st.session_state.image, img_size)

with col2:
    # Bild hochladen
    st.subheader("Bild hochladen")
    st.session_state.uploaded_file = st.file_uploader(
        "Wähle ein Bild aus", accept_multiple_files=False, type=["png", "jpg", "jpeg"]
    )
    if st.session_state.uploaded_file is not None:
        st.session_state.image = Image.open(st.session_state.uploaded_file)
        st.image(st.session_state.image, width=150)


#-------------------------------------------------------------------------------------------
### Seitenleiste
# Öffne das Bild
image = Image.open("webpictures/fibreai.png")

# Konvertiere das Bild in Base64
buffer = BytesIO()
image.save(buffer, format="PNG")
buffer.seek(0)
data = base64.b64encode(buffer.read()).decode("utf-8")

# Benutzerdefiniertes HTML mit Base64-Bild
#st.sidebar.header("FibreAI")
image = Image.open("webpictures/fibreai.png")
st.sidebar.image(image)
