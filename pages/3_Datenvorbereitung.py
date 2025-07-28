
import streamlit as st
import importlib.util
from PIL import Image

import os
from tkinter import filedialog
from datetime import datetime
import shutil

data_path = "/opt/lampp/htdocs/Webseite_SHK/streamlit/"

#---------------------------------------------------------
# Absoluter oder relativer Pfad zur Datei
#import bildverarbeitungFunction
file_path = f'{data_path}pages/bibliotheken/bildverarbeitungFunction.py'

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
if "datenvorbereitung_set" not in st.session_state:
    st.session_state.datenvorbereitung_set = False
    # wichtig für die PDF
if "anzahl_Bilder_eigene_Bilder" not in st.session_state:
    st.session_state.anzahl_Bilder_eigene_Bilder = []




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
# PDF Variable
# wichtig für die Anzeige später in der PDF
if "datenvorbereitung_variablen" not in st.session_state:
    st.session_state.datenvorbereitung_variablen = []

# Hauptprogramm zum Steuern der Bildbearbeitung
def process_images(zielPath):
    try:
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if bildformat_check:
                bvf.formatPictures(file, image, basename, zielOrdner, bildformat_select)
                st.session_state.datenvorbereitung_variablen.append(("Bildformat", bildformat_select))
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if flipp_check:
                bvf.flippen(file, image, zielOrdner)
                st.session_state.datenvorbereitung_variablen.append(("Flippen", None))
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if split_check:
                bvf.splitten(file, split_number, image, zielOrdner)
                st.session_state.datenvorbereitung_variablen.append(("Splitten", split_number))
        for file, image, basename, zielOrdner in bvf.open_image(zielPath, ordner_namen):
            if drehen_check:
                image = bvf.randomdrehen(image)
                st.session_state.datenvorbereitung_variablen.append(("Drehen", None))
            if schaerfen_check:
                image = bvf.schaerfen(image)
                st.session_state.datenvorbereitung_variablen.append(("Schärfen", None))
            if rauschen_check:
                image = bvf.rauschen(image, kernel_input)
                st.session_state.datenvorbereitung_variablen.append(("Rauschen", kernel_input))
            if black_check:
                image = bvf.schwarzweiß(image)
                st.session_state.datenvorbereitung_variablen.append(("schwarzweiß", None))
            if crop_check:
                image = bvf.schneiden(image, crop_input / 100)
                st.session_state.datenvorbereitung_variablen.append(("Schneiden", crop_input))
            if kontrast_check:
                image = bvf.kontrastAdjust(image, alpha_input, beta_input)
                st.session_state.datenvorbereitung_variablen.append(("Kontrast", (alpha_input, beta_input)))
            if resize_check:
                image = bvf.groesseAendern(image, resize_pictureGroesse)
                st.session_state.datenvorbereitung_variablen.append(("Bildgröße", resize_pictureGroesse))
                st.session_state.image_size = resize_pictureGroesse
            image = bvf.save_image(image, basename, zielOrdner)
        return True
    except:
        st.error("Fehler bei der Funktion ProcessImages")
        return False

def existingDir(zielPath):
    if os.path.isdir(zielPath):
        dir_content = os.listdir(zielPath)
        if dir_content:
            print("Inhalt vorher:", dir_content)
            for item in dir_content:
                full_path = os.path.join(zielPath, item)
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)  # ganze Ordner löschen
                else:
                    os.remove(full_path)  # Dateien löschen
            dir_content = os.listdir(zielPath)
            print("Inhalt nachher:", dir_content)
    else:
        print("Pfad ist kein existierender Ordner:", zielPath)
    return True

def run_image_processing(zielPath, flipp_check, split_check, progress_bar):
    success = False  # Standardwert

    with st.empty():
        if flipp_check:
            st.info("Achtung, beim Flippen der Bilder kann es etwas dauern...")
        if split_check:
            st.info("Achtung, beim Splitten der Bilder kann es etwas dauern...")

        if process_images(zielPath):
            st.success(f"Die Bildverarbeitung ist nun fertig. Betrachte deine Bilder im Zielordner: **{zielPath}**.")
            progress_bar.progress(100, "Fertig!")  # Fortschritt auf 100%
            success = True

    return success


# Start Button und Bilderbearbeitungsprozess
def startButton(DBselection, dbselectedPath, ordner_namen, zielPath):
    #zielPath = proof_ziel_path_windows(zielPath)
    # bei Datenbank Bilder, dbselectedPath = tatsächlicher Pfad(datenbank_bilderPath)
    # bei eigene Bilder, dbselectedPath = uploaded_files (ordner_name : file)
    print("ZielPath: ", zielPath)
    print(DBselection, dbselectedPath, zielPath)

    progress_bar = st.progress(0, "Starte nun mit dem Kopiervorgang in den Zielordner.")
    if (DBselection == "Eigene Bilder" and "Mikroskop" in ordner_namen):
        try:
            # Basis - Ordner bereinigen
            dir_val = existingDir(zielPath)
            print("ZielPath: ", zielPath)
            if dir_val == True:
                print("Starte Vorgang copyImages\n\n\n\n\n\n")
                print("DBSelection: ", DBselection)
                print("ordner_namen: ", ordner_namen)
                print("dbselectedPath: ", dbselectedPath)
                print("zielPath: ", zielPath)

                # Schritt 1: Kopieren
                if bvf.copyImages(DBselection, ordner_namen, dbselectedPath, zielPath):
                    print("DBSelection: ", DBselection)
                    print("ordner_namen: ", ordner_namen)
                    print("dbselectedPath: ", dbselectedPath)
                    print("zielPath: ", zielPath)
                    progress_bar.progress(50,
                                          "Alle Bilder wurden erfolgreich kopiert, **starte nun die Bildverarbeitung**.")  # Fortschritt auf 50% setzen
                else:
                    progress_bar.progress(0, "Fehler...")  # Bei Fehler den Fortschritt zurücksetzen

                print("Starte Vorgang Verarbeitung\n\n\n\n\n\n")
                verarbeitung_erfolgreich = run_image_processing(zielPath, flipp_check, split_check, progress_bar)

                if verarbeitung_erfolgreich:
                    bvf.show_images(zielPath, ordner_namen)
                else:
                    st.write("❌ Bildverarbeitung fehlgeschlagen oder abgebrochen.")

        except Exception as e:
            print("Datenvorbereitung hat nicht geklappt: ", e)
            print("ZielPfad ", zielPath)
            progress_bar.progress(50)  # Bei Fehler den Fortschritt zurücksetzen
    else:
        try:
            # Basis - Ordner bereinigen
            dir_val = existingDir(zielPath)
            print("ZielPath: ", zielPath)
            if dir_val == True:
                print("Starte Vorgang copyImages\n\n\n\n\n\n")
                print("DBSelection: ", DBselection)
                print("ordner_namen: ", ordner_namen)
                print("dbselectedPath: ", dbselectedPath)
                print("zielPath: ", zielPath)


                # Schritt 1: Kopieren
                if bvf.copyImages(DBselection, ordner_namen, dbselectedPath, zielPath):
                    print("DBSelection: ", DBselection)
                    print("ordner_namen: ", ordner_namen)
                    print("dbselectedPath: ", dbselectedPath)
                    print("zielPath: ", zielPath)
                    progress_bar.progress(50, "Alle Bilder wurden erfolgreich kopiert, **starte nun die Bildverarbeitung**.")  # Fortschritt auf 50% setzen
                else:
                    #st.warning(f"Beim kopieren der Bilder in Zielordner: **{zielPath}** hat etwas nicht geklappt.")
                    progress_bar.progress(0, "Fehler...")  # Bei Fehler den Fortschritt zurücksetzen

                print("Starte Vorgang Verarbeitung\n\n\n\n\n\n")
                verarbeitung_erfolgreich = run_image_processing(zielPath, flipp_check, split_check, progress_bar)

                if verarbeitung_erfolgreich:
                    #st.write("✅ Bildverarbeitung erfolgreich abgeschlossen!")
                    bvf.show_images(zielPath, ordner_namen)
                    bvf.setTestBilder(zielPath, ordner_namen)
                    bvf.setTrainAndValBilder(zielPath, ordner_namen)
                    bvf.proof_train_val_test_folder(zielPath)
                    st.success("Es wurden auch :blue[Testbilder] für das spätere trainieren mit der KI erfolgreich ausselektiert.")

                else:
                    st.write("❌ Bildverarbeitung fehlgeschlagen oder abgebrochen.")

        except Exception as e:
            print("Datenvorbereitung hat nicht geklappt: ", e)
            print("ZielPfad ", zielPath)
            #st.warning(f"Die Datenverabeitung der Bilder hat nicht ganz geklappt.")
            progress_bar.progress(50)  # Bei Fehler den Fortschritt zurücksetzen


def proof_ziel_path_windows(zielpath):
    print("ZielPath in Windows: ", zielpath)
    #zielpath = "C:/Users/alen/Downloads/TEST/FibreAI_2025-06-12/" + "\\"
    tmp = zielpath.split("/")
    zielpath = ""
    for i in tmp:
        zielpath = zielpath + i + "\\"
    print("zielpath: ", zielpath)
    zielpath_new = zielpath.replace("\\\\\\", "")
    print(zielpath_new)
    #zielpath_new = zielpath_new.replace("\\", "\\\\")
    #print(zielpath_new)
    zielpath_new = zielpath_new + "\\"
    print("zielpath_new: ", zielpath_new)
    return zielpath_new






#---------------------------------------------------------
#---------------------------------------------------------
st.title("Datenvorbereitung")

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
if "Anleitung_int_Datenvorbereitung" not in st.session_state:
    st.session_state.Anleitung_int_Datenvorbereitung = 0

Anleitung = [
        "Anleitung",
        "1. Wähle aus zwischen: :blue[Datenbank Bilder] oder :blue[Eigene Bilder].",
        "2. Wenn du :blue['Eigene Bilder'] auswählst, lade deine Bilder hoch, indem du die entsprechenden Klassen auswählst. Danach erscheinen Upload-Felder für den jeweiligen Upload.\n \n Wenn du :blue['Datenbank-Bilder'] auswählst, stelle sicher, dass die Datenbanken auf Seite 2 erfolgreich erkannt wurden. In der Regel erscheint oben ein grünes Informationsfeld mit den erfolgreich geladenen Klassen.",
        "3. Wähle die gewünschten Modifikationen aus, z.B. 'Bildformat ändern' und 'PNG'.\n\nHinweis: Einige Modifikationen bieten dir zusätzliche Auswahlmöglichkeiten über Multiselect-Felder.",
        "4. Wähle deinen Zielordner unten über den Button :blue['Bildordner auswählen'] aus.",
        "5. Starte die Bildverarbeitung mit einem Klick auf :blue['Start']."
    ]


# Anzeige
header.info(Anleitung[st.session_state.Anleitung_int_Datenvorbereitung], icon="ℹ️", width="stretch")


with header.form("Anleitung"):
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.Anleitung_int_Datenvorbereitung > 0:
            zurück_hide = False
        else:
            zurück_hide = True
        if st.form_submit_button("← zurück", use_container_width=True, disabled=zurück_hide):
            st.session_state.Anleitung_int_Datenvorbereitung -= 1

    with col2:
        if st.session_state.Anleitung_int_Datenvorbereitung < len(Anleitung) - 1:
            if st.form_submit_button("vor →", use_container_width=True):
                st.session_state.Anleitung_int_Datenvorbereitung += 1


#---------------------------------------------------------
#---------------------------------------------------------

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

        try:
            anzahl_liste = []
            for klasse in ordner_namen:
                try:
                    anzahl = len(st.session_state[klasse]) if st.session_state[klasse] else 0
                    anzahl_liste.append((klasse, anzahl))
                except KeyError:
                    anzahl_liste.append((klasse, 0))  # Oder None
            st.session_state.anzahl_Bilder_eigene_Bilder = anzahl_liste
        except Exception as e:
            print(e)

    except:
        case = False
    DBKlassen.append("Mikroskop")
    eigeneKlassen = bvf.processDBselectionUploadBox(DBKlassen)
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
        # Füge Anzahl der Bilder in st.session_state ein




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

zielPath_button_help = "Hier wählst du deinen Zielordner aus, wo die fertig bearbeiteten Bilder gespeichert werden. \n\n Beispiel: /home/usr/Downloads/"
zielPath_button = st.button("Bildordner auswählen", help=zielPath_button_help)
zielPath = ""
if zielPath_button:
    # Überprüfe das Betriebssystem
    if os.name == 'nt':  # Windows
        initial_dir = "C:/"
    elif os.name == 'posix':  # Unix oder Linux (inkl. macOS)
       initial_dir = "~/"
    else:
        initial_dir = "/"
    try:
        zielPath = filedialog.askdirectory(initialdir=initial_dir)
        #proof_ziel_path_windows(zielPath)
        date = datetime.now().strftime("%Y-%m-%d")
        ordnername = f"FibreAI_{date}"

        zielPath = f"{zielPath}/{ordnername}/"
        #st.write("ZielPfad: ", zielPath)
        st.session_state.zielPath = zielPath
    except:
        zielPath = ""
        st.session_state.zielPath = zielPath
        

if zielPath:
    #st.session_state.zielPath = bvf.proofendingzielPath(zielPath) #prüft Zielpfad auf Endung /
    startButton_hide = False
    st.success(f"Dein Zielordner lautet: **{st.session_state.zielPath}**")

#---------------------------------------------------------
# starte hier den Prozess der Bildbearbeitung
start_check_help = "Beim drücken des Buttons startest Du die Bearbeitung der Bilder. \n Schau dir nochmal genau an, ob alle Einstellungen deiner Wahl entsprechen."
start_check = st.button("Start", disabled=startButton_hide, help=start_check_help)
if start_check:
    st.session_state.datenvorbereitung_set = True #wichtig für die PDF
    zielVar = bvf.erstelleOrdner(st.session_state.zielPath, ordner_namen)  # Ordner erstellen und Zielpfade setzen
    if all(path != "" for path in zielVar):
        # Erstellen der Ordner
        st.success("Alle Ordner & Unterordner wurden nun im Zielpfad erstellt.")
        if DBselection == "Datenbank Bilder":
            startButton(DBselection, datenbank_bilderPath, st.session_state.ordner_namen, st.session_state.zielPath)
        if DBselection == "Eigene Bilder":
            startButton(DBselection, uploaded_files, st.session_state.ordner_namen, st.session_state.zielPath)
    else:
        st.warning("Zielordner konnte nicht erstellt werden. Bitte prüfe den angegeben Dateipfad zum ZielOrdner.")



#---------------------------------------------------------
#Wichtig für die Übergabe an Seite 4
col1, col2 = st.columns(2)
with col1:
    if DBselection == "Datenbank Bilder":
        #st.write("Ausgewählte Datenbanken:", st.session_state.datenbank)
        ordner_namen = bvf.getNamesofDatenbank(datenbank_bilderPath) #Ordner für die Zielordnererstellung
        st.session_state.ordner_namen = ordner_namen
        #st.write("Ordner-Namen:", st.session_state.ordner_namen)
    if DBselection == "Eigene Bilder":
        ordner_namen = st.session_state.ordner_namen
        #st.write("Ordner-Namen:", st.session_state.ordner_namen)
    st.session_state.DBselection = DBselection
    #st.write("DBselection:", st.session_state.DBselection)
with col2:
    if DBselection == "Datenbank Bilder":
        #st.write("Datenbank-Bilderpath:", st.session_state.datenbank_bilderPath)
        ordner_namen_path = bvf.erstelleOrdnerPfade(zielPath, st.session_state.ordner_namen)
        st.session_state.ordner_namen_path = ordner_namen_path
        #st.write("Ordner-Pfade:", st.session_state.ordner_namen_path)
    if DBselection == "Eigene Bilder":
        ordner_namen_path = bvf.erstelleOrdnerPfade(zielPath, st.session_state.ordner_namen)
        st.session_state.ordner_namen_path = ordner_namen_path
        #st.write("Ordner-Pfade:", st.session_state.ordner_namen_path)
        st.session_state.zielPath = zielPath
        #st.write("Zielpfad:", st.session_state.zielPath)




#-------------------------------------------------------------------------------------------
### Seitenleiste
### Seitenleiste
image = Image.open(f"{data_path}webpictures/fibreai.png")
st.logo(image, icon_image=image, size="large")


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

