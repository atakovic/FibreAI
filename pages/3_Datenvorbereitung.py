import datetime

import streamlit as st
import importlib.util
from PIL import Image
import base64
from io import BytesIO
import os
from pathlib import Path
#from tkinter import filedialog
from datetime import datetime

#---------------------------------------------------------
# Absoluter oder relativer Pfad zur Datei
#import bildverarbeitungFunction
file_path = 'pages/bibliotheken/bildverarbeitungFunction.py'

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("bildverarbeitungFunction", file_path)
bvf = importlib.util.module_from_spec(spec)  # Alias `bvf` für das Modul
spec.loader.exec_module(bvf)

#---------------------------------------------------------
# Page Setup
st.set_page_config(
    layout="wide",
    page_title = "KI Textil",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)
#st.write(st.session_state)

#---------------------------------------------------------
#Variablen und Session-State
black, resize, crop, flip, bildformat, kontrast, helligkeit, drehen = False, False, False, False, False, False, False, False
pictureGroesse = 224
BilderPath = "" #BilderPfad für Hauptklassen

startButton_hide = True
DBKlassen = ["Flachs","Maulbeerseide","Rohbaumwolle","merzerisierte Baumwolle","Tussahseide","Viskose","Wolle"]
DBOrdner = ["Real","Synthetisch"]


# Initialisierung der Session-State-Variablen
if "schaerfen_check" not in st.session_state:
    st.session_state.schaerfen_check = False
if "rauschen_check" not in st.session_state:
    st.session_state.rauschen_check = False
if "DBselection" not in st.session_state:
    st.session_state.DBselection = "Datenbank Bilder"
if "image_size" not in st.session_state:
    st.session_state.image_size = 64
if "UploadString" not in st.session_state:
    st.session_state.UploadString = ""



try:
    if st.session_state.datenbank_bilderPath:
        datenbank_bilderPath = st.session_state.datenbank_bilderPath
        ordner_namen = bvf.getNamesofDatenbank(datenbank_bilderPath)
    if st.session_state.datenbank:
        datenbank = st.session_state.datenbank

    if not st.session_state.datenbank:
        st.warning("Es wurde keine Bild-Datenbank ausgewählt, wähle bitte eine Datenbank aus, auf der Seite **Datenbank** oder lade eigene Bilder hoch über das Menü: **Eigene Bilder**.")
    if "ordner_namen_path" not in st.session_state:
        st.session_state.ordner_namen_path = []
        ordner_namen_path = st.session_state.ordner_namen_path
except:
    if "datenbank" not in st.session_state:
        st.session_state.datenbank = []
        for i in range(len(DBKlassen)):
            if i == 4:
                break
            st.session_state.datenbank.append(DBKlassen[i] + " (real)")
        datenbank = st.session_state.datenbank
    if "datenbank_bilderPath" not in st.session_state:
        st.session_state.datenbank_bilderPath = []
        st.session_state.datenbank_bilderPath = bvf.getdatenbankBilderPath(st.session_state.datenbank_bilderPath, st.session_state.datenbank,2)
        datenbank_bilderPath = st.session_state.datenbank_bilderPath
    if "ordner_namen" not in st.session_state:
        st.session_state.ordner_namen = []
        ordner_namen = bvf.getNamesofDatenbank(datenbank_bilderPath)
        st.session_state.ordner_namen = ordner_namen
    if "ordner_namen_path" not in st.session_state:
        st.session_state.ordner_namen_path = []
        ordner_namen_path = st.session_state.ordner_namen_path


if st.session_state.DBselection == "Datenbank Bilder":
    # Anzahl der Bilder in der ausgewählten Datenbank
    nameforshow = bvf.changeNamesofDatenbankforDVB(st.session_state.datenbank)
    anzahl = bvf.templateStrings(DBKlassen, datenbank_bilderPath)
    st.success(
        f"Bild-Datenbanken aktuell aktiv: **{nameforshow}** mit **{anzahl} Bildern** und sind nun aktiv in **Datenbank Bilder**.")


#---------------------------------------------------------

# Hauptprogramm zum Steuern der Bildbearbeitung
def process_images(zielPath):
    try:
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if bildformat_check:
                bvf.formatPictures(file, image, basename, zielOrdner, bildformat_select)
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if flipp_check:
                bvf.flippen(file, image, zielOrdner)
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if split_check:
                bvf.splitten(file, split_number, image, zielOrdner)
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if drehen_check:
                image = bvf.randomdrehen(image)
            if schaerfen_check:
                image = bvf.schaerfen(image)
            if rauschen_check:
                image = bvf.rauschen(image, kernel_input)
            if black_check:
                image = bvf.schwarzweiß(image)
            if crop_check:
                image = bvf.schneiden(image, crop_input / 100)
            if kontrast_check:
                image = bvf.kontrastAdjust(image, alpha_input, beta_input)
            if resize_check:
                image = bvf.groesseAendern(image, resize_pictureGroesse)
                st.session_state.image_size = resize_pictureGroesse
            image = bvf.save_image(image, basename, zielOrdner)
        return True
    except:
        st.error("Fehler bei der Funktion ProcessImages")
        return False


# Start Button und Bilderbearbeitungsprozess
def startButton(DBselection, dbselectedPath, zielPath):
    # bei Datenbank Bilder, dbselectedPath = tatsächlicher Pfad(datenbank_bilderPath)
    # bei eigene Bilder, dbselectedPath = uploaded_files (ordner_name : file)

    progress_bar = st.progress(0, "Starte nun mit dem Kopiervorgang in den Zielordner.")
    bvf.clearImages(zielPath, ordner_namen)


    # Schritt 1: Kopieren
    if bvf.copyImages(DBselection, ordner_namen, dbselectedPath, zielPath):
        #print("DBSelection: ", DBselection)
        #print("ordner_namen: ", ordner_namen)
        #print("dbselectedPath: ", dbselectedPath)
        #print("zielPath: ", zielPath)
        progress_bar.progress(50, "Alle Bilder wurden erfolgreich kopiert, **starte nun die Bildverarbeitung**.")  # Fortschritt auf 50% setzen
    else:
        st.warning(f"Beim kopieren der Bilder in Zielordner: **{zielPath}** hat etwas nicht geklappt.")
        progress_bar.progress(0, "Fehler...")  # Bei Fehler den Fortschritt zurücksetzen
    with st.empty():
        if flipp_check:
            #print("flipp_check")
            st.info("Achtung, beim Flippen der Bilder kann es etwas dauern...")
        if split_check:
            #print("split_check")
            st.info("Achtung, beim Splitten der Bilder kann es etwas dauern...")
        if process_images(zielPath) == True:
            #print("process_images")
            st.success(f"Die Bildverarbeitung ist nun fertig. Betrachte deine Bilder im Zielordner: **{zielPath}**.")
            progress_bar.progress(100, "Fertig!")  # Fortschritt auf 100% setzen
        else:
            st.warning(f"Die Datenverabeitung der Bilder hat nicht ganz geklappt.")
            progress_bar.progress(50)  # Bei Fehler den Fortschritt zurücksetzen
    bvf.show_images(zielPath, ordner_namen)
    bvf.setTestBilder(zielPath, ordner_namen)
    bvf.setTrainAndValBilder(zielPath, ordner_namen)
    st.success("Es wurden auch Testbilder für das spätere Trainieren mit der KI erfolgreich ausselektiert.")


#---------------------------------------------------------
#---------------------------------------------------------
st.title("Datenvorbereitung")

# Erzeuge Klassennamen in Streamlit Array
st.subheader("Bereite hier deine Bilder für die Bildklassifizierung vor.")
st.write("Mit **Schneiden** wird die Funktion freigeschaltet, den Rand des Bild abzuschneiden in **%**.")
st.write("Mit **Flippen** wird die Funktion freigeschaltet, das Bild mehrmals zu spiegeln (Links nach Rechts) & (Oben nach Unten) - daraus entstehen bis zu **4 neue Bilder**.")
st.write("Mit der Funktion **Kontrastwerte** & **Helligkeitswerte** anpassen, werden alle Bilder automatisch auf die gleichen Kontrastwere & Helligkeit angepasst.")
#---------------------------------------------------------
# Selection: Datenbank Bilder oder eigene Bilder verwenden
DBselection = st.pills(
    "",
    options=["Datenbank Bilder", "Eigene Bilder"],
    selection_mode="single",
    default="Datenbank Bilder" ,
    label_visibility="hidden",
)
#---------------------------------------------------------
#Funktion für die Klassenbearbeitung der auswählten Datenbank Bilder
if DBselection:
    st.session_state.DBselection = DBselection

if DBselection == "Eigene Bilder":
    try:
        datenbank = st.session_state.datenbank
        ordner_namen = st.session_state.ordner_namen
        datenbank_bilderPath = st.session_state.datenbank_bilderPath
        case = True
    except:
        case = False
    eigeneKlassen = bvf.processDBselectionUploadBox(DBKlassen)
    #eigeneKlassen = bvf.formateigeneKlassen(eigeneKlassen)
    # wenn eigeneKlassen nicht leer ist, sollen datenbank, datenbank_bilderpath und ordner_namen angepasst werden:
    if eigeneKlassen:
        # mache dies, um Überschneidungen zu vermeiden
        if case == True:
            datenbank.clear()
            datenbank_bilderPath.clear()
            ordner_namen.clear()

        # die zu erstellenden Ordner Namen werden nun neu zugeteilt
        ordner_namen = eigeneKlassen
        st.session_state.ordner_namen = ordner_namen
        #st.write(ordner_namen)

        # es sollen nun Uploadboxen erstellt werden für das uploaden der einzelnen Fotos
        uploadBoxen = bvf.showuploadBoxen(ordner_namen) # Speicherort der Fotos
        uploaded_files = bvf.saveuploadedFiles(ordner_namen)
        st.session_state.uploades_files = uploaded_files

        #st.write(uploaded_files)


#---------------------------------------------------------
# Columns für die Auswahlen
A, B, C = st.columns(3)
with A:
    resize_pictureGroesse = st.number_input(
        "Gewünschte Größe des Bildes in **Breite** & **Höhe**.",
        value = 224,
    )
    alpha_input = st.number_input(
        "**Kontrastwert**(0 bis 3.0)",
        value = 0.5,
        min_value=0.0,
        max_value=3.0,
        step=0.1,
        ) # alpha Value für convertScaleAbs

with B:
    crop_input = st.number_input(
        "Gewünschtes **Zuschneiden** (Ränder) in **%**.",
        value = 5,
    )
    beta_input = st.number_input(
        "**Helligkeitswert**(-100 bis 100)",
        value = 0,
        min_value = -100,
        max_value = 100,
        step = 1,
    ) # beta Value für convertScaleAbs
with C:
    bildformat_select = st.selectbox(
        "In welchem **Bildformat** soll umgewandelt werden?.",
        ("PNG", "JPEG"),
        index = 0,
    )
    kernel_input = st.number_input(
        "**Kernelwert** für Bildrauschen(0 bis 20)",
        value=1,
        min_value=0,
        max_value=20,
        step=1,
    )
split_number = st.selectbox(
    "**Anzahl der Bilder**, die aus **einem Bild** entstehen sollen",
    ("4", "6", "8", "12", "16"),
    index=0,
)
#---------------------------------------------------------
# CodeBlock to Show:
FunctionSelect = st.pills(
    "Hier können die einzelnen Funktionen eingesehen werden:",
    options=["Leer", "Größe ändern", "Drehen", "Schärfen", "Schneiden",
             "Schwarz Weiß", "Flippen", "Format ändern", "Kontrast&Helligkeit", "Rauschen", "Splitten"],
    selection_mode="single",
    default="Leer",
)
if FunctionSelect != "Leer":
    bvf.show_function(FunctionSelect)

#---------------------------------------------------------
# Columns für die Checkfelder
schaerfen_disabled = st.session_state.rauschen_check
rauschen_disabled = st.session_state.schaerfen_check
col1, col2, col3 = st.columns(3)
with col1:
    resize_check = st.checkbox("Bildgröße ändern")
    drehen_check = st.checkbox("Bild (random) drehen")
    schaerfen_check = st.checkbox("Bild schärfen", disabled=schaerfen_disabled, key="schaerfen_check")
    if schaerfen_check:
        rauschen_disabled = True

with col2:
    crop_check = st.checkbox("Schneiden")
    black_check = st.checkbox("Schwarz-Weiß")
    flipp_check = st.checkbox("Flippen")
    split_check = st.checkbox("Splitten")

with col3:
    bildformat_check = st.checkbox("Bildformat ändern")
    kontrast_check = st.checkbox("Kontrast und Helligkeit anpassen")
    rauschen_check = st.checkbox("Rauschen reduzieren", disabled=rauschen_disabled, key="rauschen_check")
    if rauschen_check:
        schaerfen_disabled = True
        if (alpha_input == 0 and beta_input == 0):
            st.info("Bitte den Wert für Kontrast und Helligkeit anpassen.")

#---------------------------------------------------------
st.subheader("Zielordner auswählen:")
#---------------------------------------------------------
# Ordner auswählen und weitere Operationen durchführen
#zielPath = st.text_input("Füge hier den Ordnerpfad für das speichern der Bilder hinzu & bestätige mit **ENTER**:", placeholder="Beispiel: /home/usr/Downloads/", label_visibility="visible")
#if zielPath:
#    zielPath = bvf.proofendingzielPath(zielPath) #prüft Zielpfad auf Endung /
#    startButton_hide = False
#    st.success(f"Dein Zielordner lautet: **{zielPath}**")

zielPath_button = st.button("Bildordner auswählen")
zielPath = ""
if zielPath_button:
    # Überprüfe das Betriebssystem
    if os.name == 'nt':  # Windows
        initial_dir = "C:/"
    elif os.name == 'posix':  # Unix oder Linux (inkl. macOS)
        initial_dir = "/home/usr/"
    else:
        initial_dir = "/"
    zielPath = filedialog.askdirectory(initialdir=initial_dir)
    date = datetime.now().strftime("%Y-%m-%d")
    zielPath = zielPath + "/FibreAI_" + date + "/"
    st.session_state.zielPath = zielPath

if zielPath:
    st.session_state.zielPath = bvf.proofendingzielPath(zielPath) #prüft Zielpfad auf Endung /
    startButton_hide = False
    st.success(f"Dein Zielordner lautet: **{st.session_state.zielPath}**")

#---------------------------------------------------------
# starte hier den Prozess der Bildbearbeitung
start_check = st.button("Start", disabled=startButton_hide)
if start_check:
    zielVar = bvf.erstelleOrdner(st.session_state.zielPath, ordner_namen)  # Ordner erstellen und Zielpfade setzen
    if all(path != "" for path in zielVar):
        # Erstellen der Ordner
        st.success("Alle Ordner & Unterordner wurden nun im Zielpfad erstellt.")
        if DBselection == "Datenbank Bilder":
            startButton(DBselection, datenbank_bilderPath, st.session_state.zielPath)
        if DBselection == "Eigene Bilder":
            startButton(DBselection, uploaded_files, st.session_state.zielPath)
    else:
        st.warning("Zielordner konnte nicht erstellt werden. Bitte prüfe den angegeben Dateipfad zum ZielOrdner.")



#---------------------------------------------------------
#Wichtig für die Übergabe an Seite 4
col1, col2 = st.columns(2)
with col1:
    if DBselection == "Datenbank Bilder":
        st.write("Ausgewählte Datenbanken:", st.session_state.datenbank)
        ordner_namen = bvf.getNamesofDatenbank(datenbank_bilderPath) #Ordner für die Zielordnererstellung
        st.session_state.ordner_namen = ordner_namen
        st.write("Ordner-Namen:", st.session_state.ordner_namen)
    if DBselection == "Eigene Bilder":
        ordner_namen = st.session_state.ordner_namen
        st.write("Ordner-Namen:", st.session_state.ordner_namen)
    st.session_state.DBselection = DBselection
    st.write("DBselection:", st.session_state.DBselection)
with col2:
    if DBselection == "Datenbank Bilder":
        st.write("Datenbank-Bilderpath:", st.session_state.datenbank_bilderPath)
        ordner_namen_path = bvf.erstelleOrdnerPfade(zielPath, st.session_state.ordner_namen)
        st.session_state.ordner_namen_path = ordner_namen_path
        st.write("Ordner-Pfade:", st.session_state.ordner_namen_path)
    if DBselection == "Eigene Bilder":
        ordner_namen_path = bvf.erstelleOrdnerPfade(zielPath, st.session_state.ordner_namen)
        st.session_state.ordner_namen_path = ordner_namen_path
        st.write("Ordner-Pfade:", st.session_state.ordner_namen_path)

st.session_state.zielPath = zielPath


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


#-------------------------------------------------------------------------------------------

#Hinweis Variablen:
# Allgemein:
#ordner_namen = ist für das Erstellen der einzelnen Ablageordner // Klassen
#ordner_namen_path = einzelne Pathverzeichnisse für die erstellten Bilder und Ordner die bearbeitet worden sind
#DBselection = Auswahl der Bilderdatenbank

# Auswahl: Datenbank Bilder:
#datenbank = beinhaltet Werte wie FlachsReal, FlachsSynt, also datenbanken
#datenbank_bilderPath = beinhaltet die entsprechenden Verzeichnisse

#Auswahl: Eigene Bilder:
#uploaded_files = Array der gespeicherten Bilder

# hier vielleicht noch verändern:
# Anzeige der Anzahl der Bilder(position und gleiches für EigeneBilder anzeigen lassen)
# Anzeige Warnung: Keine Datenbank gewählt, verschwinden lassen sobald Eigene Bilder(onchange)
# Kontrast und Helligkeit: schauen, ob man das optimieren kann
