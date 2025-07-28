# wichtig für Ki-Train.py

import io
import tensorflow as tf

from PIL import Image
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import Callback
from plotly import graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from PIL import Image
import base64
from io import BytesIO
from io import StringIO
import os
import numpy as np
from ultralytics import YOLO
from pathlib import Path

import streamlit as st
import importlib.util

#---------------------------------------------------------
# Absoluter oder relativer Pfad zur Datei
#import bildverarbeitungFunction
file_path = '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/bildverarbeitungFunction.py'

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("bildverarbeitungFunction", file_path)
bvf = importlib.util.module_from_spec(spec)  # Alias `bvf` für das Modul
spec.loader.exec_module(bvf)


#---------------------------------------------------------
# Zeigt die Epochen aus der Console in Streamlit
# Custom Callback für Streamlit-Ausgabe
# Eigene Callback-Funktion

#---------------------------------------------------------

# Funktion zum Trainieren des Modells
def startModel(batch_size, image_size, epoch, model_name, class_images):
    # class_images = string Zielort = zielPath
    #Trainiert das Modell mit den angegebenen Parametern.

    #model_name: Name des Modells (z.B. "VGG16", "ResNet", etc.)
    #class_images: Dictionary mit Bildern für jede Klasse
    if model_name == "YOLO11":
        model = YOLO("yolo11n-cls.pt")  # load a pretrained model (recommended for training)

        # Streamlit-Container für dynamisches Schreiben
        epoch_placeholder = st.empty()

        # Eigene Callback-Funktion
        def on_train_epoch_start(trainer):
            current_epoch = trainer.epoch + 1  # trainer.epoch startet bei 0
            total_epochs = trainer.args.epochs
            epoch_placeholder.info(f"🚀 Epoch {current_epoch}/{total_epochs} gestartet.")

        def on_train_epoch_end(trainer):
            current_epoch = trainer.epoch + 1
            total_epochs = trainer.args.epochs
            epoch_placeholder.success(f"✅ Epoch {current_epoch}/{total_epochs} abgeschlossen.")

        model.add_callback("on_train_epoch_start", on_train_epoch_start)
        model.add_callback("on_train_epoch_end", on_train_epoch_end)
        train = model.train(data=class_images, epochs=epoch, imgsz=image_size,
                            batch = batch_size,
                            )

        st.write(train)
        #st.write(train.save_dir)

        #speichern des trainierten Modells in model_saved in zielPath
        model_saved_file = os.path.join(class_images, "model_saved.txt") #Pfad des Models
        pathtomodel = str(train.save_dir)

        with open(model_saved_file, "w") as f: #trage Pfad des Models in Datei ein
            f.write(pathtomodel)
            if os.path.isfile(model_saved_file) is True:
                st.success(f"Modelpfad wurde erfolgreich gespeichert in {class_images} unter **model_saved.txt**. \n\n Falls dein Model auf der nächsten Seite nicht erfolgreich erkannt wird. So kannst du es problemlos wieder laden.")
            else:
                st.error(f"Fehler beim Speichern des Modelpfads in {class_images}.")

        col1, col2 = st.columns(2)
        with col1:
            results = os.path.join(train.save_dir, "results.png")
            st.image(results)

        with col2:
            confusion_matrix = os.path.join(train.save_dir, "confusion_matrix.png")
            st.image(confusion_matrix)

        return model, pathtomodel

    elif model_name == "YOLO8":
        model = YOLO("yolov8n-cls.pt")  # load a pretrained model (recommended for training)
        # Streamlit-Container für dynamisches Schreiben
        epoch_placeholder = st.empty()

        # Eigene Callback-Funktion
        def on_train_epoch_start(trainer):
            current_epoch = trainer.epoch + 1  # trainer.epoch startet bei 0
            total_epochs = trainer.args.epochs
            epoch_placeholder.info(f"🚀 Epoch {current_epoch}/{total_epochs} gestartet.")

        def on_train_epoch_end(trainer):
            current_epoch = trainer.epoch + 1
            total_epochs = trainer.args.epochs
            epoch_placeholder.success(f"✅ Epoch {current_epoch}/{total_epochs} abgeschlossen.")

        model.add_callback("on_train_epoch_start", on_train_epoch_start)
        model.add_callback("on_train_epoch_end", on_train_epoch_end)
        train = model.train(data=class_images, epochs=epoch, imgsz=image_size,
                            batch=batch_size,
                            )

        st.write(train)
        #st.write(train.save_dir)

        # speichern des trainierten Modells in model_saved in zielPath
        model_saved_file = os.path.join(class_images, "model_saved.txt")
        pathtomodel = str(train.save_dir)
        with open(model_saved_file, "w") as f:
            f.write(pathtomodel)
            if os.path.isfile(model_saved_file) is True:
                st.success(f"Modelpfad wurde erfolgreich gespeichert in {class_images} - falls dein Model auf der nächsten Seite nicht erfolgreich erkannt wird. So kannst du es problemlos wieder laden.")
            else:
                st.error(f"Fehler beim Speichern des Modelpfads in {class_images}.")

        col1, col2 = st.columns(2)
        with col1:
            results = os.path.join(train.save_dir, "results.png")
            st.image(results)

        with col2:
            confusion_matrix = os.path.join(train.save_dir, "confusion_matrix.png")
            st.image(confusion_matrix)

        return model, pathtomodel



# Anzeigen der Funktionen für die Lehrzwecke
def show_function(functionToShow):
    lines = ""
    if functionToShow == "YOLO11":
        lines = """
        if model_name == "YOLO11":
        model = YOLO("yolo11n-cls.pt")  # load a pretrained model (recommended for training)
        model.add_callback("on_train_start", on_train_start)
        counter = 0
        train = model.train(data=class_images, epochs=epoch, imgsz=64,
                            batch=batch_size,
                            #callbacks={'on_epoch_end': on_epoch_end}
                            )
        st.write(train)
        st.write(train.save_dir)
        col1, col2 = st.columns(2)
        with col1:
            results = os.path.join(train.save_dir, "results.png")
            st.image(results)

        with col2:
            confusion_matrix = os.path.join(train.save_dir, "confusion_matrix.png")
            st.image(confusion_matrix)
        """
    elif functionToShow == "YOLO8":
        lines = """
        if model_name == "YOLO8":
        model = YOLO("yolov8n-cls.pt")  # load a pretrained model (recommended for training)
        model.add_callback("on_train_start", on_train_start)
        counter = 0
        train = model.train(data=class_images, epochs=epoch, imgsz=64,
                            batch=batch_size,
                            #callbacks={'on_epoch_end': on_epoch_end}
                            )
        st.write(train)
        st.write(train.save_dir)
        col1, col2 = st.columns(2)
        with col1:
            results = os.path.join(train.save_dir, "results.png")
            st.image(results)

        with col2:
            confusion_matrix = os.path.join(train.save_dir, "confusion_matrix.png")
            st.image(confusion_matrix)
        """
    st.code(lines)


def readYoloArgs(pathtomodel):
    args_file = "args.yaml"
    data = ""
    model_name = ""
    with open(os.path.join(pathtomodel, args_file), "r") as f:
        for line in f:
            if "data" in line:
                data = line.strip()  # strip() entfernt Leerzeichen und Zeilenumbrüche
                data = data.split()[1]
            if "model" in line:
                model_name = line.strip()
                model_name = model_name.split()[1]
                if "yolov8" in model_name:
                    model_name = "YOLO8"
                else:
                    model_name = "YOLO11"

    return data, model_name




