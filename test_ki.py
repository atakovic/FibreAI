import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from io import StringIO
#------------------------------------------------------------------------------------------
import importlib.util
import os
from ultralytics import YOLO

# Absoluter oder relativer Pfad zur Datei
#import trainModelPython
file_path = os.path.join(os.path.dirname(__file__), '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/trainModelPython.py')

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("trainModelPython", file_path)
tmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tmp)

##################################################

st.write
klassen_namen=["Fuchs", "Bär", "Elf"]

def showuploadBoxen(ordner_namen):
    Upload_Boxen = {}
    col1, col2 = st.columns(2)

    with col1:
        for i in range(len(klassen_namen)):
            if i % 2 == 0:
                files = st.file_uploader(
                    f"**{klassen_namen[i]}**",
                    label_visibility="visible",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'],
                    key=klassen_namen[i]
                )
                Upload_Boxen[klassen_namen[i]] = files  # Speichern der hochgeladenen Dateien

    with col2:
        for i in range(len(klassen_namen)):
            if i % 2 == 1:
                files = st.file_uploader(
                    f"**{klassen_namen[i]}**",
                    label_visibility="visible",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'],
                    key=klassen_namen[i]
                )
                Upload_Boxen[klassen_namen[i]] = files  # Speichern der hochgeladenen Dateien

    return Upload_Boxen


# Uploads speichern
Uploadbox = showuploadBoxen(klassen_namen)
st.session_state["Uploadbox"] = Uploadbox  # Speichern in Session-State
"""
def image_to_binary(uploaded_file):
    #Konvertiert ein hochgeladenes Bild in eine Binärdarstellung
    if uploaded_file is not None:
        # Bild in Bytes einlesen
        img_bytes = uploaded_file.getvalue()

        # Bytes in eine binäre Zeichenkette umwandeln
        binary_string = ''.join(format(byte, '08b') for byte in img_bytes)

        return binary_string

    return None



# Hochgeladene Bilder auslesen und anzeigen
for tier in klassen_namen:
    if tier in st.session_state["Uploadbox"] and st.session_state["Uploadbox"][tier] is not None:
        st.write(f"**Bilder für {tier}:**")
        for uploaded_file in st.session_state["Uploadbox"][tier]:
            st.write(uploaded_file.name)  # Name der Datei ausgeben
            st.image(uploaded_file, caption=uploaded_file.name)  # Bild anzeigen
            binary_string = image_to_binary(uploaded_file)
            st.write(binary_string)

def extractPicturestoClasses(klassen_namen):
    klassen_test = []
    for tier in klassen_namen:
        if tier in st.session_state["Uploadbox"] and st.session_state["Uploadbox"][tier] is not None:
            #Werte aus Session-State übernehmen
            batch_size = 16
            learning_rate = 0.00001
            epoch = 1
            model_name = "VGG16"
            st.info(f"Gewählte Modifikation: \n\n Batch: {batch_size}, Learning-Rate: {learning_rate}, Epoch: {epoch}, Model: {model_name} \n\n")

            # Starte das Training
            st.write("**Achtung:** Das Model kann mit dem Button: **Model herunterladen** gespeichert werden.\n Der Button befindet sich am Ende der Webseite.")
            st.write("*Fortschritt des Trainings:*")
            #tmp.startModel(batch_size, learning_rate, epoch, model_name, klassen_test)
"""

model = YOLO("yolo11n-cls.pt")  # load a pretrained model (recommended for training)
model.train(data=st.session_state[Uploadbox], epochs=3, imgsz=64)


st.write(st.session_state)


