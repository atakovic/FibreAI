import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
from tkinter import filedialog
#------------------------------------------------------------------------------------------
import importlib.util
import os


# Absoluter oder relativer Pfad zur Datei
#import trainModelPython
file_path = os.path.join(os.path.dirname(__file__), '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/trainModelPython.py')

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("trainModelPython", file_path)
tmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tmp)

#import bildverarbeitungFunction
file_path = '/opt/lampp/htdocs/Webseite_SHK/streamlit/pages/bibliotheken/bildverarbeitungFunction.py'

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("bildverarbeitungFunction", file_path)
bvf = importlib.util.module_from_spec(spec)  # Alias `bvf` für das Modul
spec.loader.exec_module(bvf)
#------------------------------------------------------------------------------------------
# Page Setup
st.set_page_config(
    page_title = "KI Textil",
    layout="wide",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)


#------------------------------------------------------------------------------------------
DBselection = ""
#SelectionKlassen: Über Funktion erreichbar, Klassen aus Auswahl(Selection)
class_names_changer = False
DVbKlassen = [] #Klassen aus Datenvorbereitung
eigeneKlassen = [] #alle KLassen für die KI
UploadImages = []
anzahl = 0
DBKlassen = ["Flachs","Maulbeerseide","Rohbaumwolle","merzerisierte Baumwolle","Tussahseide","Viskose","Wolle"]

#------------------------------------------------------------------------------------------

# Initialisiere den Session-State
if "epoch" not in st.session_state:
    st.session_state["epoch"] = 3
if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 16
#if "learning_rate" not in st.session_state:
#    st.session_state["learning_rate"] = 0.0001
if "modelChoise" not in st.session_state:
    st.session_state.modelChoise = "YOLO11"
if "trainedModel" not in st.session_state:
    st.session_state.trainedModel = False
if "model_classes" not in st.session_state:
    st.session_state.model_classes = []
if "image_size" not in st.session_state:
    st.session_state.image_size = 64
if "zielPath" not in st.session_state:
    st.session_state.zielPath = ""
if "pathtomodel" not in st.session_state:
    st.session_state.pathtomodel = ""
if "ki_training_set" not in st.session_state:
    st.session_state.ki_training_set = False

try:
    if st.session_state.zielPath:
        zielPath = st.session_state.zielPath


except:
    print("")

#/home/alen/Downloads/Test123


#------------------------------------------------------------------------------------------
st.title("KI-Training")

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
# ---------------------------------------------------------
# Info-Text VOR dem Form-Container
if "Anleitung_int_KI_Training" not in st.session_state:
    st.session_state.Anleitung_int_KI_Training = 0

Anleitung = [
    "Anleitung",
    "1. Wähle deine :blue[vorverarbeiteten] Bilder über den Button :blue['Bildordner auswählen'] aus.\n\n Hinweis: Der Ordner muss folgende Unterordner enthalten: :orange[train], :orange[val] (optional: :orange[test]).",
    "2. Wähle das gewünschte Modell aus – aktuell verfügbar: :blue[YOLOv11] und :blue[YOLOv8].",
    "3. Lege die Trainingsparameter fest, z.B.: :blue['Epoche'] und :blue['Batchgröße'].",
    "4. Starte das Training über den Button :blue['Trainieren']."
]

# Anzeige
header.info(Anleitung[st.session_state.Anleitung_int_KI_Training], icon="ℹ️", width="stretch")

with header.form("Anleitung"):
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.Anleitung_int_KI_Training > 0:
            zurück_hide = False
        else:
            zurück_hide = True
        if st.form_submit_button("← zurück", use_container_width=True, disabled=zurück_hide):
            st.session_state.Anleitung_int_KI_Training -= 1

    with col2:
        if st.session_state.Anleitung_int_KI_Training < len(Anleitung) - 1:
            if st.form_submit_button("vor →", use_container_width=True):
                st.session_state.Anleitung_int_KI_Training += 1


#---------------------------------------------------------
#---------------------------------------------------------

st.write("Hier kannst du deine bearbeiteten Bilder nutzen und hochladen, um deine eigene KI auf die entsprechenden Klassen deiner Wahl zu trainieren.")

# Hauptbereich für Klassen
#st.subheader("Klassen")
st.subheader("Bilderupload")
st.write("Die Klassen werden durch die Unterordner in **train** & **val** erkannt. Das heißt, dass alle Klassen in Form eines Unterordners für das Training in betracht gezogen werden.")

#Anzeigen der Uploadboxen wenn Klassen gewählt werden
#SelectionKlassen = bvf.processDBselectionUploadBox(DBKlassen)
#UploadString = st.text_input(label="Gib hier die Adresse des Bilderordners ein:", )
directory_button_help = "Beim drücken des Buttons wählst du den Bildordner aus, der fertig bearbeiteten Bilder zum trainieren der KI aus. \n\n In der Regel, ist es der gleiche Ordner, wie auf der Seite 3: **Datenvorbereitung**. \n\n Beispiel: /home/usr/Downloads/FibreAI_XXXX-XX-XX"
directory_button = st.button("Bildordner auswählen", help=directory_button_help)
if directory_button:
    # Überprüfe das Betriebssystem
    if os.name == 'nt':  # Windows
        initial_dir = "C:/"
    elif os.name == 'posix':  # Unix oder Linux (inkl. macOS)
        initial_dir = "~/"
    else:
        initial_dir = "/"
    try:
        zielPath = filedialog.askdirectory(initialdir=initial_dir)
        zielPath_dir = os.listdir(zielPath)
        if "train" in zielPath_dir and "val" in zielPath_dir:
            st.write(zielPath)
            st.session_state.zielPath = zielPath
        else:
            st.warning("Der Dateipfad enthält keine Ordner :red[train & val], bitte suche einen neuen Ordner aus.")
            zielPath = ""
            st.session_state.zielPath = ""
    except:
        st.warning("Der Dateipfad enthält keine Ordner :red[train & val], bitte suche einen neuen Ordner aus.")
        zielPath = ""
        st.session_state.zielPath = ""


if st.session_state.zielPath:
    zielPath = st.session_state.zielPath
    dir_names = bvf.get_all_unique_folder_names(zielPath)
    anzahl = bvf.count_images_in_folder(zielPath)
    st.success(f"Folgende Klassen wurden gefunden: **{dir_names}** mit **{anzahl} Gesamtbildern**.")


#-------------------------------------------------------------------------------------------
#Modellwahl
st.subheader("Modelwahl")
model_names = ["YOLO11", "YOLO8"]
model = st.selectbox(
    "Nutze hier diverse und bekannte Modelle zur Auswahl, um dein eigenes Modell zu trainieren. \n\n Bei der Wahl: **Tensorflow**\, würdest du ein von uns selbst kreiertes Netz auswählen.",
    model_names,
    label_visibility="visible",
    key="modelChoise"
    )

FunctionSelect = st.pills(
    "Hier können die einzelnen Funktionen eingesehen werden:",
    options=["Leer", "YOLO11", "YOLO8"],
    selection_mode="single",
    default="Leer",
)
if FunctionSelect != "Leer":
    tmp.show_function(FunctionSelect)




# Einstellungen
st.subheader("Einstellungen")
epoch, batch = st.columns(2)
with epoch:
    st.number_input("Epoche", min_value=1, step=1, key="epoch")
with batch:
    st.number_input("Batchgröße", min_value=8, step=8, key="batch_size")

#learning_rate = st.number_input("Lernrate", min_value=0.0001, step=0.0001, format="%.4f", key="learning_rate")


startTraining = False
trainButton_help = "Beim drücken startest Du das Training der KI."
trainButton = st.button("Trainieren", help=trainButton_help)
try:
    if trainButton and zielPath != "":
        startTraining = True
except:
    st.warning("Dein Zielpfad scheint noch nicht korrekt definiert zu sein für das Training.")


with st.container():
    if (startTraining):

        st.session_state.ki_training_set = True #wichtig für die PDF

        # Werte aus Session-State übernehmen
        image_size = st.session_state.image_size
        batch_size = st.session_state.batch_size
        #learning_rate = st.session_state.learning_rate
        epoch = st.session_state.epoch
        model_name = st.session_state.modelChoise
        st.info(f"Gewählte Modifikation: \n\n Batch: {batch_size}, Epoch: {epoch}, Image-Size: {image_size} Model: {model_name} \n\n Anzahl Bilder: {anzahl} \n\n Klassen: {dir_names}")

        # Starte das Training
        model, pathtomodel = tmp.startModel(batch_size, image_size, epoch, model_name, st.session_state.zielPath)
        st.session_state.model_classes = eigeneKlassen
        st.session_state.trainedModel = model
        st.session_state.pathtomodel = pathtomodel


#-------------------------------------------------------------------------------------------
### Seitenleiste
image = Image.open("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png")
st.logo(image, icon_image=image, size="large")

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#Hinweis Variablen:
# Allgemein:
#ordner_namen oder class_names = ist für das Erstellen der einzelnen Ablageordner // Klassen
#ordner_namen_path = einzelne Pathverzeichnisse für die erstellten Bilder und Ordner die bearbeitet worden sind
#DBselection = Auswahl der Bilderdatenbank

# Auswahl: Datenbank Bilder:
#datenbank = beinhaltet Werte wie FlachsReal, FlachsSynt, also datenbanken
#datenbank_bilderPath = beinhaltet die entsprechenden Verzeichnisse der einzelnen Datenbanken

#Auswahl: Eigene Bilder:
#uploaded_files = Array der gespeicherten Bilder


#schaue dass durch Auswahl Pill: Ja eine Klasse gespeichert wird und die Klasse SelectionKlassen zusammen mit DVbKlassen,
#sich für die Nutzung der Bilder hochladen lässt.
