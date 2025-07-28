import os
import numpy as np
import streamlit as st
import glob
import importlib.util

from asn1crypto import pdf
from PIL import Image
from fpdf import FPDF
import cv2
import matplotlib.pyplot as plt
from datetime import datetime

from ultralytics import YOLO

#---------------------------------------------------------
# Absoluter oder relativer Pfad zur Datei
#import bildverarbeitungFunction
data_path = "/opt/lampp/htdocs/Webseite_SHK/streamlit/"
file_path = f'{data_path}pages/bibliotheken/bildverarbeitungFunction.py'

# Modul dynamisch importieren
spec = importlib.util.spec_from_file_location("bildverarbeitungFunction", file_path)
bvf = importlib.util.module_from_spec(spec)  # Alias `bvf` für das Modul
spec.loader.exec_module(bvf)

#---------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Globale Variablen
#-----------------------------------------------------------------------------------------


seite_w = 190
seite_h = 277

DBKlassen = ["Flachs", "Maulbeerseide", "Rohbaumwolle", "merzerisierte Baumwolle",
             "Tussahseide", "Viskose", "Wolle"]
DBKlassen_proof_datenbank = ["Flachs", "Seide", "rWolle", "merzWolle",
             "Tussah", "Viskose", "Wolle"]



# ----------------------------------------------------------------------------------
# PDF Kreuz
# ----------------------------------------------------------------------------------

#Fuktion prüft, ob die Webseiten besucht sind, genauer: ob die st.session_states exisitieren
def proofinsessionstate(name):
    try:
        if (name in st.session_state) and (st.session_state[name] == True):
            return True
        else:
            return False
    except Exception as e:
        print(f"Fehler beim proofinstreamlit: {e}")
        return False


def proofKonfigurationsessionstate(name):
    try:
        for eintrag in st.session_state.get("datenvorbereitung_variablen", []):
            schritt, parameter = eintrag
            if schritt == name:
                return True, parameter
        return False, None
    except Exception as e:
        print(f"Fehler beim proofKonfigurationsessionstate: {e}")
        return False, None


def proofDatenbankinsessionstate(name):
    try:
        if name == "Real":
            for i in range(len(st.session_state.datenbank)):
                tmp = str(st.session_state.datenbank[i])[-4:]
                print(tmp)
                if tmp == "Real":
                    return tmp
            return None
        if name == "Synt":
            for i in range(len(st.session_state.datenbank)):
                tmp = str(st.session_state.datenbank[i])[-4:]
                print(tmp)
                if tmp == "Synt":
                    return tmp
            return None
        if name in st.session_state.datenbank: 
            return True
        else:
            return False
    except Exception as e:
        print(f"Fehler beim proofDatenbankinsessionstate: {e}")
        return False

def proofsessionstateDBSelection():
    try:
        if "DBselection" in st.session_state:
            return st.session_state.DBselection
        return None
    except Exception as e:
        print(f"Fehler beim proofsessionstateDBSelection: {e}")
        return None
    
# dient zur Überprüfung bei Auswahl: Eigene Bilder, welche Klassen verwendet worden sind 
# und vor allem wie viele Bilder    
def proofsessionstateEigeneBilder(name):
    try:
        if isinstance(st.session_state.anzahl_Bilder_eigene_Bilder, list):
            bilder_dict = dict(st.session_state.anzahl_Bilder_eigene_Bilder)
            if name in bilder_dict:
                return name, bilder_dict[name]
        return None
    except Exception as e:
        print(f"Fehler beim proofsessionstateEigeneBilder: {e}")
        return None


def proofbildervorher(DBKlassen):
    try:
        if "DBselection" in st.session_state:
            if st.session_state.DBselection == "Datenbank Bilder":
                if st.session_state.datenbank_bilderPath:
                    anzahl = bvf.templateStrings(DBKlassen, st.session_state.datenbank_bilderPath)
                    return anzahl

            if st.session_state.DBselection == "Eigene Bilder":
                if st.session_state.anzahl_Bilder_eigene_Bilder:
                    anzahl = 0
                    for i, klasse, anzahl_klasse in enumerate(st.session_state.datenbank_bilder_eigene_Bilder):
                        anzahl += anzahl_klasse
                        return anzahl
        else:
            return None
    except Exception as e:
        print(f"Fehler beim proofbildervorher: {e}")
        return None

def proofbildernachher(dateipfad, erlaubte_endungen={".jpg", ".jpeg", ".png", ".tif", ".bmp"}):
    try:
        bildanzahl = 0
        for root, dirs, files in os.walk(dateipfad):
            bilder = [
                datei for datei in files
                if os.path.splitext(datei)[1].lower() in erlaubte_endungen
            ]
            bildanzahl += len(bilder)
        return bildanzahl
    except Exception as e:
        print(f"Fehler beim proofbildernachher: {e}")
        return None


#-----------------------------------------------------------------------------------------
#PDF Klassen GANZ WICHTIG
#-----------------------------------------------------------------------------------------

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.page_number_custom = 0

    def add_page(self, *args, **kwargs):
        self.page_number_custom += 1
        super().add_page(*args, **kwargs)
        addnewPage(self, self.page_number_custom)



#-----------------------------------------------------------------------------------------
# Predict - YOLO - in Verbindung mit PDF
#-----------------------------------------------------------------------------------------

# Fügt eine Liste von bearbeiteten Bildern (mit Vorhersage-Text) in ein PDF ein
# TEST
def to_rgb(image):
    import cv2
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    else:
        raise ValueError(f"Unbekanntes Bildformat: shape={image.shape}")

# https://chatgpt.com/c/6880c557-afd8-832c-a3c3-f638df667d35
def addImage(pdf, processed_images, files, y, model):
    try:
        x_titel = 18
        y_titel = y

        # Überschrift setzen
        pdf.set_font("Arial", 'B', size=10)
        pdf.set_xy(x_titel, y_titel)
        pdf.cell(w=0, h=10, txt="Ergebnis:", ln=1, align="L")
        y += 10  # Abstand nach Überschrift

        # Positionen
        x_titel_rechts = (seite_w / 2) + 20

        # Gemeinsame Schleife für linkes Bild + rechte Vorhersage
        for i in range(min(len(processed_images), len(files))):
            image_np, image_path = processed_images[i]
            image_pil = Image.fromarray(to_rgb(image_np))
            file_input = files[i]
            image_name = os.path.basename(image_path)

            # Y-Position je nach Position auf Seite (0–2)

            # Variablen
            # Positionen je nach Bildnummer auf der Seite
            pos = i % 3
            if pos == 0:
                y_picture = 210
            elif pos == 1:
                y_picture = 70
            else:
                y_picture = 140

            # ----- LINKES BILD -----
            temp_path = f"/tmp/{image_name}"
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                image_pil.save(temp_path, format="PNG")
                pdf.image(temp_path, x=x_titel + 2, y=y_picture, w=65, h=65)
            except Exception as e:
                print(f"Fehler beim Speichern/Einfügen von {image_name}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ----- RECHTE VORHERSAGE -----
            try:
                pdf.set_font("Arial", size=10)
                results = list(model(file_input))
                probs = results[0].probs.data.numpy().tolist()

                y_temp = y_picture
                pdf.set_xy(x_titel_rechts, y_temp)
                pdf.cell(w=0, h=5, txt=image_name, ln=1, align="L")
                y_temp += 5

                pdf.set_xy(x_titel_rechts, y_temp)
                pdf.cell(w=0, h=5, txt="___________________________", ln=1, align="L")
                y_temp += 5

                for j, prob in enumerate(probs):
                    class_name = model.names[j]
                    percent = f"{prob * 100:.0f}%"
                    pdf.set_xy(x_titel_rechts, y_temp)
                    pdf.cell(w=0, h=5, txt=f"{class_name}: {percent}", ln=1, align="L")
                    y_temp += 5

            except Exception as e:
                print(f"Fehler bei Modellvorhersage für {image_name}: {e}")

            # Neue Seite nach jedem 3. Bild
            if i % 3 == 0:
                pdf.add_page()

            #if (i + 1) % 3 == 0 and (i + 1) < len(processed_images):
            #    pdf.add_page()

        print("Images + Vorhersagen erfolgreich in PDF eingefügt.")
        return pdf

    except Exception as e:
        print(f"Allgemeiner Fehler in addImage(): {e}")
        return pdf



# Führt YOLO-Inferenz auf allen Bildern im test/-Ordner eines Verzeichnisses durch
def predictALLImagesTest(path, model):
    try:
        if path:
            image_extensions = ('*.png', '*.jpg', '*.jpeg', '*.tif', '*.tiff', '*.webp')
            files = []
            for ext in image_extensions:
                files.extend(glob.glob(os.path.join(path, 'test', '**', ext), recursive=True))

            # Inferenz ueber alle Bilder
            results = model(files, stream=True, verbose=False)
            return results, files
    except Exception as e:
        st.error(f"Fehler beim predicten aller Test-Bilder: {e}")
    return None, None

# Nimmt YOLO-Predictions und schreibt sie direkt ins Bild (als Text-Overlay)
def setPredictionInsidePicture(results, files, model):
    try:
            processed_images = []  # Liste der Bilder fuer die PDF

            for i, r in enumerate(results):
                file_path = files[i]
                image_name = file_path.split("/")[-1]
                img_cv2 = cv2.imread(file_path)
                img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)

                if hasattr(r, 'probs'):
                    top1 = r.probs.top1
                    top1conf = float(r.probs.top1conf)
                    class_name = model.names[top1]
                    conf_percent = round(top1conf * 100, 2)
                    text = f"{class_name} ({conf_percent}%)"
                else:
                    text = "Keine Klassifikation"

                cv2.putText(img_rgb, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(img_rgb, image_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

                processed_images.append((img_rgb, file_path))

                #st.write(file_path)
                #st.image(Image.fromarray(img_rgb), caption=os.path.basename(file_path))

            return processed_images
    except Exception as e:
        st.error(f"Fehler beim Schreiben der Prediction innerhalb der Bilder: {e}")
    return None

# Liest Trainingskonfiguration aus args.yaml und schreibt sie ins PDF
def getArgstoPDF(pathtomodel):
    try:
        args_yaml_path = os.path.join(pathtomodel, "args.yaml")

        #Model-Version, Epochen, Datenset, Batchgröße, Image-Größe, Speicherort KI
        name_list = ["model", "epochs", "data", "batch", "imgsz", "save_dir"]
        data_list = {}


        if os.path.exists(args_yaml_path):
            with open(args_yaml_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key in name_list:
                            data_list[key] = value

            print("Trainingsdaten saved in PDF")
            return data_list
        else:
            print("args.yaml nicht gefunden")
            return None

    except Exception as e:
        print(f"Fehler beim Speichern der Trainingsdaten: {e}")
        return None


#-----------------------------------------------------------------------------------------
#PDF
#-----------------------------------------------------------------------------------------

# Matrix Bild
def setMatrixtoPDF(pathtomodel, pdf, x, y):
    try:
        listed_dir = os.listdir(pathtomodel)
        confusion_matrix = os.path.join(pathtomodel, "confusion_matrix.png")
        pdf.set_font("Arial", 'B', size=10)
        if "confusion_matrix.png" in listed_dir:
            pdf.set_xy(x=x, y=y)
            y += 10

            pdf.cell(w=50, h=10, txt="Konfusionsmatrix", ln=1, align="L")
            pdf.image(confusion_matrix, x=x-6, y=y, w=100, h=75, type='', link='')

        print("Matrix saved in PDF")
    except Exception as e:
        print(f"Fehler beim Speichern der Matrix: {e}")

# Result Bild
def setResultstoPDF(pathtomodel, pdf, x, y):
    try:
        listed_dir = os.listdir(pathtomodel)
        results = os.path.join(pathtomodel, "results.png")
        pdf.set_font("Arial", 'B', size=10)
        if "results.png" in listed_dir:
            pdf.set_xy(x=x, y=y)
            y += 10

            pdf.cell(w=50, h=10, txt="Fehlerfunktionen & Genauigkeitsfunktionen", ln=1, align="L")
            pdf.image(results, x=x, y=y, w=75, h=75, type='', link='')

        print("Matrix saved in PDF")
    except Exception as e:
        print(f"Fehler beim Speichern der Matrix: {e}")

# Logo
def setLogotoPDF(pdf):
    try:
        logo = "/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png"
        if os.path.exists(logo):
            pdf.image(logo, x=15, y=20, w=85)

        else:
            print("Logo nicht gefunden")
    except Exception as e:
        print(f"Fehler beim Speichern des Logos: {e}")

# Rahmen fuer die PDF
def setBordertoPDF(pdf):
    try:
        pdf.set_line_width(0.5) #Rahmendicke
        pdf.rect(x=10, y=10, w=seite_w, h=seite_h) #Rahmen PDF
        pdf.rect(x=10, y=10, w=seite_w/2, h=seite_h/8) #Rahmen Logo
        pdf.rect(x=(seite_w/2)+10, y=10, w=seite_w/2, h=seite_h/8) #Rahmen Datum usw.
        pdf.rect(x=10, y=(seite_h/8)+10, w=seite_w, h=20)  # Rahmen Dokumentations- und Ergebnisbericht

    except Exception as e:
        print(f"Fehler beim setzen des Borders: {e}")

def setTitletoPDF(pdf):
    try:
        pdf.set_xy(x=10, y=(seite_h/8)+15)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(w=190, h=10, txt="Dokumentations- und Ergebnisbericht", ln=1, align="C")
    except Exception as e:
        print(f"Fehler beim setzen des Titels: {e}")

def setDatetoPDF(pdf):
    try:
        pdf.set_font("Arial", size=10)

        pdf.set_xy(x=(seite_w/2)+12, y=12)
        pdf.multi_cell(w=(seite_w/2), h=7.5,
                       txt=f"Datum:\nUhrzeit:\nOrt:\nName:",
                       align="L"
                       )

        date = datetime.today().strftime("%d.%m.%Y")
        time_now = datetime.today().strftime("%H:%M Uhr")
        pdf.set_xy(x=(seite_w / 2) + 12, y=12)
        pdf.multi_cell(w=(seite_w / 2)-5, h=7.5,
                       txt=f"{date}\n{time_now}\nMoenchengladbach\n__________________",
                       align="R"
                       )
    except Exception as e:
        print(f"Fehler beim setzen des Datums usw.: {e}")

def setAnwendungsuebersicht(pdf):
    # Border
    pdf.set_line_width(0.5)  # Rahmendicke
    pdf.rect(x=10, y=(seite_h/8)+30, w=50, h=10)  # Rahmen PDF

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=10, y=(seite_h/8)+30)
    pdf.cell(w=50, h=10, txt="Anwendungsuebersicht", ln=1, align="C")

    checkbox_labels = ["Datenbank", "Datenvorbereitung", "KI-Training", "KI-Faseranalyse"]
    checkbox_labels_session_state = ["datenbank_set", "datenvorbereitung_set", "ki_training_set", "ki_faseranalyse_set"]
    x_start, y = 20, (seite_h/8)+45
    for i, label in enumerate(checkbox_labels):
        pdf.rect(x_start + i * 45, y, 4, 4)  # Checkbox
        #prüfe ob die checkboxen in st.session_states sind und setze kreuz
        kreuz = proofinsessionstate(checkbox_labels_session_state[i])
        if kreuz == True:
            pdf.set_font("Arial", style="B", size=12)
            pdf.text(x_start + i * 45 +0.5, y + 3.5, "x")
        pdf.set_font("Arial", size=10)
        pdf.text(x_start + i * 45 + 6, y + 3.5, label)

def setSeitenzahl(pdf, seitenzahl):
    rect_w = 20
    rect_h = 10
    x_pos = seite_w - rect_w
    y_pos = seite_h - rect_h

    # Text
    pdf.set_font("Arial", size=10)
    pdf.set_xy(x_pos, y_pos + 2.5)  # leichte vertikale Zentrierung
    pdf.cell(w=rect_w, h=5, txt=f"Seite {seitenzahl}", align="C")

    # Border
    pdf.set_line_width(0.5)
    pdf.rect(x=x_pos, y=y_pos, w=rect_w, h=rect_h)

def templateStrings(dbName, bilder_root, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = [".jpg", ".jpeg", ".png", ".tif"]

    pfad = os.path.join(bilder_root, dbName)

    if not os.path.exists(pfad):
        return "❌"

    try:
        dateien = [
            f for f in os.listdir(pfad)
            if os.path.isfile(os.path.join(pfad, f)) and any(f.endswith(ext) for ext in allowed_extensions)
        ]
        return f"{os.path.basename(dbName)}: {len(dateien)} Bilder"
    except Exception as e:
        return "Fehler"

def setDatenbankuebersicht(pdf):
    BilderPath = "/opt/lampp/htdocs/Webseite_SHK/streamlit/BildDatenbank/"
    DBOrdner = ["Real", "Synthetisch"]

    # Border fuer Titel
    pdf.set_line_width(0.5)
    pdf.rect(x=10, y=(seite_h / 8) + 55, w=50, h=10)

    # Border fuer den Bereich
    pdf.rect(x=10, y=(seite_h / 8) + 55, w=seite_w/2, h=(seite_h/8)*2)
    pdf.rect(x=(seite_w / 2)+10, y=(seite_h / 8) + 55, w=seite_w / 2, h=(seite_h/8)*2)

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=10, y=(seite_h / 8) + 55)
    pdf.cell(w=50, h=10, txt="Datenbank", ln=1, align="C")

    halbeseite_w = seite_w/ 2

    # --- check_real ---
    pdf.set_font("Arial", 'B', size=10)
    x_start, y = 20, (seite_h / 8) + 70
    pdf.rect(x_start, y, 4, 4)  # Checkbox
    pdf.text(x_start +6 , y + 3.5, "reale Daten:")
    bool = proofDatenbankinsessionstate("Real")
    if bool == "Real":
        pdf.text(x_start +0.5 , y + 3.5, "X")

    x = x_start + 2
    y = y + 10

    for i, klassen in enumerate(DBKlassen):
        pdf.set_font("Arial", size=10)
        pdf.rect(x, y, 4, 4)  # Checkbox
        dbName = os.path.join(DBOrdner[0], klassen)  # z.B. "Real/Flachs"
        label = templateStrings(dbName, BilderPath)
        y += 5
        # setzen der Kreuze
        try:
            label_session_state = str(DBKlassen_proof_datenbank[i]) + "Real"
            bool = proofDatenbankinsessionstate(label_session_state)
            pdf.set_font("Arial",  size=12)
            if bool:
                pdf.text(x+0.5, y-1, f"X")
        except Exception as e:
            print(f"Fehler beim X setzen in der PDF für die Klassen {e}")
        pdf.text(x+5, y-2, label)


    # --- check_synt ---
    pdf.set_font("Arial", 'B', size=10)
    x_start, y = halbeseite_w + 20, (seite_h / 8) + 70
    pdf.rect(x_start, y, 4, 4)  # Checkbox
    pdf.text(x_start + 6, y + 3.5, "synthetische Daten:")
    bool = proofDatenbankinsessionstate("Synt")
    if bool == "Synt":
        pdf.text(x_start +0.5 , y + 3.5, "X")

    x = x_start + 2
    y = y + 10

    for i, klassen in enumerate(DBKlassen):
        pdf.set_font("Arial", size=10)
        pdf.rect(x, y, 4, 4)  # Checkbox
        dbName = os.path.join(DBOrdner[1], klassen)  # z.B. "Real/Flachs"
        label = templateStrings(dbName, BilderPath)
        y += 5
        # setzen der Kreuze
        try:
            label_session_state = str(DBKlassen_proof_datenbank[i]) + "Synt"
            bool = proofDatenbankinsessionstate(label_session_state)
            pdf.set_font("Arial",  size=12)
            if bool:
                pdf.text(x+0.5, y-1, f"X")
        except Exception as e:
            print(f"Fehler beim X setzen in der PDF für die Klassen {e}")
        pdf.text(x+5, y-2, label)

def setDatenvorbereitunguebersicht(pdf):
    # Border fuer Titel
    pdf.set_line_width(0.5)
    x = 10
    y = (seite_h / 8) + 124.5
    pdf.rect(x=x, y=y, w=50, h=10)

    # Text
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x, y=y)
    pdf.cell(w=50, h=10, txt="Datenvorbereitung", ln=1, align="C")

    # Titel
    x_titel = 18
    y = y + 15
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Verwendete Bilder:", ln=1, align="L")

    # Variablen
    halbeseite_w = seite_w/ 2
    x_start, y = 20, y+15
    bool = proofsessionstateDBSelection()

    # --- check_Datenbank Bilder ---
    pdf.set_font("Arial", 'B', size=10)
    pdf.rect(x_start, y, 4, 4)  # Checkbox
    pdf.text(x_start +6 , y + 3.5, "Datenbank Bilder:")
    if bool == "Datenbank Bilder":
        pdf.text(x_start + 0.5 , y + 3.5, "X")


    # --- check_Eigene Bilder ---
    x_start = halbeseite_w + 20
    pdf.set_font("Arial", 'B', size=10)
    pdf.rect(x_start, y, 4, 4)  # Checkbox
    pdf.text(x_start + 6, y + 3.5, "Eigene Bilder:")
    if bool == "Eigene Bilder":
        pdf.text(x_start + 0.5 , y + 3.5, "X")

    # Variablen
    x = x_start + 2
    y = y + 10

    for i, klassen in enumerate(DBKlassen):
        pdf.set_font("Arial", size=10)
        name = DBKlassen[i]
        tmp = proofsessionstateEigeneBilder(name)
        if tmp:
            anzahl = tmp[1]
        else:
            anzahl = None
        print("anzahl = ", anzahl)

        pdf.set_font("Arial", size=10)
        pdf.rect(x, y, 4, 4)  # Checkbox
        label = f"{klassen}: {anzahl} Bilder"
        y += 5
        if anzahl and anzahl > 0:
            pdf.text(x +0.5, y - 1.5, "X")
        
        pdf.text(x+5, y-2, label)


def setDatenvorbereitungKonfigurationsuebersicht(pdf):
    # beginnt bei Seite 2 - Anfang der Seite
    # Variablen
    x = 10
    y = (seite_h / 8) + 30

    # Border
    pdf.set_line_width(0.5)  # Rahmendicke
    pdf.rect(x=x, y=y, w=50, h=10)  # Rahmen PDF

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x, y=y)
    pdf.cell(w=50, h=10, txt="Datenvorbereitung", ln=1, align="C")

    # Text
    x_titel = 18
    y = y + 15
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Konfiguration:", ln=1, align="L")


    # Variablen
    x_start, y_start = 20, y+15
    x_middle, y_middle = (seite_w/3)+x_start, y_start
    x_end, y_end = ((seite_w/3)*2)+x_start, y_start
    versetze = 15                           #fuer 2 Zeilen Text zusammengehoerend
    versetze_einzeln = versetze - 3.5       #fuer 1 Zeile Text
    versetze_text = 8                       #versetze den Text bei 2 Zeilen Text zusammengehoerend

    # --- check_Left Side ---
    pdf.set_font("Arial", size=10)
    pdf.rect(x_start, y_start, 4, 4)  # Checkbox
    pdf.text(x_start +6, y_start + 3.5, "Bildgroeße ändern")
    Bool, Breite_and_Hoehe = proofKonfigurationsessionstate(name = "Bildgröße")
    if Bool == True:
        pdf.text(x_start +0.5, y_start, f"X")
    pdf.text(x_start +6, y_start + versetze_text, f"Breite & Hoehe: {Breite_and_Hoehe}")

    y_start += versetze
    pdf.rect(x_start, y_start, 4, 4)  # Checkbox
    pdf.text(x_start + 6, y_start + 3.5, "Helligkeitswert")
    Bool, Helligkeitswert = proofKonfigurationsessionstate(name = "Kontrast")
    if Bool == True:
        pdf.text(x_start +0.5, y_start + 3.5, f"X")
    pdf.text(x_start + 6, y_start + versetze_text, f"(-100 bis 100): {Helligkeitswert}")

    y_start += versetze
    pdf.rect(x_start, y_start, 4, 4)  # Checkbox
    pdf.text(x_start + 6, y_start + 3.5, "Schwarz-Weiß")
    Bool, tmp = proofKonfigurationsessionstate(name = "schwarzweiß")
    if Bool == True:
        pdf.text(x_start +0.5, y_start + 3.5, f"X")

    y_start += versetze_einzeln
    pdf.rect(x_start, y_start, 4, 4)  # Checkbox
    pdf.text(x_start + 6, y_start + 3.5, "Flippen")
    Bool, tmp = proofKonfigurationsessionstate(name = "Flippen")
    if Bool == True:
        pdf.text(x_start +0.5, y_start + 3.5, f"X")

    # --- check_middle Side ---
    pdf.set_font("Arial", size=10)
    pdf.rect(x_middle, y_middle, 4, 4)  # Checkbox
    pdf.text(x_middle +6 , y_middle + 3.5, "Bild schneiden")
    Bool, Cuttingwert = proofKonfigurationsessionstate(name = "Schneiden")
    if Bool == True:
        pdf.text(x_middle +0.5, y_middle + 3.5, f"X")
    pdf.text(x_middle + 6, y_middle + versetze_text, f"Ränder [%]: {Cuttingwert}")

    y_middle += versetze
    pdf.rect(x_middle, y_middle, 4, 4)  # Checkbox
    pdf.text(x_middle + 6, y_middle + 3.5, "Kontrastwert")
    Bool, Kontrastwert = proofKonfigurationsessionstate(name = "Kontrast")
    if Bool == True:
        pdf.text(x_middle +0.5, y_middle + 3.5, f"X")
    pdf.text(x_middle + 6, y_middle + versetze_text, f"(0 bis 3,0): {Kontrastwert}")

    y_middle += versetze
    pdf.rect(x_middle, y_middle, 4, 4)  # Checkbox
    pdf.text(x_middle + 6, y_middle + 3.5, "Rauschen reduzieren")
    Bool, RauschenWert = proofKonfigurationsessionstate(name = "Rauschen")
    if Bool == True:
        pdf.text(x_middle +0.5, y_middle + 3.5, f"X")
    pdf.text(x_middle + 6, y_middle + versetze_text, f"Kernelwert für Bildrauschen(0 bis 20): {RauschenWert}")

    y_middle += versetze_einzeln
    pdf.rect(x_middle, y_middle, 4, 4)  # Checkbox
    pdf.text(x_middle + 6, y_middle + 3.5, "Bild schärfen")
    Bool, tmp = proofKonfigurationsessionstate(name = "Schärfen")
    if Bool == True:
        pdf.text(x_middle +0.5, y_middle + 3.5, f"X")

    # --- check_right Side ---
    pdf.set_font("Arial", size=10)
    pdf.rect(x_end, y_end, 4, 4)  # Checkbox
    pdf.text(x_end +6 , y_end + 3.5, "Bild splitten")
    Bool, Anzahl_splits = proofKonfigurationsessionstate(name = "Splitten")
    if Bool == True:
        pdf.text(x_end +0.5, y_end + 3.5, f"X")
    pdf.text(x_end + 6, y_end + versetze_text, f"Anzahl: {Anzahl_splits}")

    y_end += versetze
    pdf.rect(x_end, y_end, 4, 4)  # Checkbox
    pdf.text(x_end + 6, y_end + 3.5, "Bildformat")
    Bool, Bildformat = proofKonfigurationsessionstate(name = "Bildformat")
    if Bool == True:
        pdf.text(x_end +0.5, y_end + 3.5, f"X")
    pdf.text(x_end + 6, y_end + versetze_text, f"Dateiendung: {Bildformat}")

    # Text
    y = y_end + (versetze*3)
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Bilderanzahl:", ln=1, align="L")

    pdf.set_font("Arial", size=10)
    y += versetze_text
    Anzahl_vorher = proofbildervorher(DBKlassen)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"Anzahl an Bildern vor der Bearbeitung: {Anzahl_vorher}", ln=1, align="L")

    y += versetze_text
    try:
        if st.session_state.zielPath:
            dateipfad = st.session_state.zielPath
        else:
            dateipfad = None
    except:
        dateipfad = None
    Anzahl_nachher = proofbildernachher(dateipfad)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"Anzahl an Bildern nach der Bearbeitung: {Anzahl_nachher}", ln=1, align="L")

def setKITraining(yaml_list, pdf):
    # Variablen
    x = 10
    y = (seite_h / 8) + 160

    # Border
    pdf.set_line_width(0.5)  # Rahmendicke
    pdf.rect(x=x, y=y, w=50, h=10)  # Rahmen PDF
    pdf.rect(x=x, y=y, w=seite_w, h=0)

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x, y=y)
    pdf.cell(w=50, h=10, txt="KI-Training", ln=1, align="C")

    # Text
    x_titel = 18
    y = y + 15
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Modellauswahl:", ln=1, align="L")

    # Variablen
    x_start, y_start = 20, y + 15
    x_middle, y_middle = (seite_w / 3) + x_start, y_start
    versetze = 15  # fuer 2 Zeilen Text zusammengehoerend
    versetze_einzeln = versetze - 3.5  # fuer 1 Zeile Text
    versetze_text = 8  # versetze den Text bei 2 Zeilen Text zusammengehoerend
    halbeseite_w = seite_w / 2

    # --- check_Left Side ---
    pdf.set_font("Arial", size=10)
    pdf.rect(x_start, y_start, 4, 4)  # Checkbox
    if "model" in yaml_list:
        if "yolo11" in yaml_list["model"]:
            pdf.text(x_start+0.5, y_start+ 3.5, "X")
    pdf.text(x_start + 6, y_start + 3.5, "YOLO 11")


    # --- check_middle Side ---
    pdf.set_font("Arial", size=10)
    pdf.rect(x_middle, y_middle, 4, 4)  # Checkbox
    if "model" in yaml_list:
        if "yolov8" in yaml_list["model"]:
            pdf.text(x_middle+0.5, y_middle+ 3.5, "X")
    pdf.text(x_middle + 6, y_middle + 3.5, "YOLO 8")

    # Text
    y = y_start + 10
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Einstellungen:", ln=1, align="L")

    pdf.set_font("Arial", size=10)
    y += versetze_text
    if "epochs" in yaml_list:
        epochs = yaml_list["epochs"]
    else:
        epochs = None
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"Epochen: {epochs}", ln=1, align="L")

    y += versetze_text
    if "batch" in yaml_list:
        batch_size = yaml_list["batch"]
    else:
        batch_size = None
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"Batchgröße: {batch_size}", ln=1, align="L")

    y += versetze_text
    if "data" in yaml_list:
        data = yaml_list["data"]
    else:
        data = None
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"Datensatz: {data}", ln=1, align="L")

    y += versetze_text
    if "save_dir" in yaml_list:
        save_dir = yaml_list["save_dir"]
    else:
        save_dir = None
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt=f"KI-Speicherort: {save_dir}", ln=1, align="L")

def setKITrainingAuswertung(pdf):
    # Hinweis Anfang der dritten Seite
    # Variablen
    x = 10
    y = (seite_h / 8) + 30
    versetze = 15                       # fuer 2 Zeilen Text zusammengehoerend
    versetze_einzeln = versetze - 3.5   # fuer 1 Zeile Text
    versetze_text = 8                   # versetze den Text bei 2 Zeilen Text zusammengehoerend

    # Border
    pdf.set_line_width(0.5)  # Rahmendicke
    pdf.rect(x=x, y=y, w=50, h=10)  # Rahmen PDF
    pdf.rect(x=x, y=y, w=seite_w, h=0)

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x, y=y)
    pdf.cell(w=50, h=10, txt="KI-Training", ln=1, align="C")

    # Text
    x_titel = 18
    y = y + 15
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x_titel, y=y)
    pdf.cell(w=50, h=10, txt="Ergebnis:", ln=1, align="L")

    # --- Linke Seite ---
    y_titel = y + versetze_text
    pathtomodel = "/home/alen/.pyenv/runs/classify/train92"
    setMatrixtoPDF(pathtomodel, pdf, x_titel, y_titel)

    # -- Rechte Seite ---
    x_halbeseite_w_titel = (seite_w / 2)+20
    setResultstoPDF(pathtomodel, pdf, x_halbeseite_w_titel, y_titel)

def setKIFaserAnalyse(pdf, model, test_image_dir):
    # Variablen
    x = 10
    y = ((seite_h / 8) * 5) +10
    versetze = 15                       # fuer 2 Zeilen Text zusammengehoerend
    versetze_einzeln = versetze - 3.5   # fuer 1 Zeile Text
    versetze_text = 8                   # versetze den Text bei 2 Zeilen Text zusammengehoerend

    # Border
    pdf.set_line_width(0.5)  # Rahmendicke
    pdf.rect(x=x, y=y, w=50, h=10)  # Rahmen PDF
    pdf.rect(x=x, y=y, w=seite_w, h=0)

    # Titel
    pdf.set_font("Arial", 'B', size=10)
    pdf.set_xy(x=x, y=y)
    pdf.cell(w=50, h=10, txt="KI-Faseranalyse", ln=1, align="C")

    # Zeige Faseranalyse Bilder Auswertung aus Test an:
    # Faseranalyse starten

    y_titel = y + versetze
    results, files = predictALLImagesTest(test_image_dir, model)
    if results and files:
        processed_images = setPredictionInsidePicture(results, files, model)
        if processed_images:
            addImage(pdf, processed_images, files, y_titel, model)


# ----------------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------------
def addnewPage(pdf, seitenzahl):
    # erstelle neue Seite
    # Überschreibung durch die Klasse und Methode add_new_page()

    # Logo
    setLogotoPDF(pdf)
    # Rahmenlinie
    setBordertoPDF(pdf)
    # Titel
    setTitletoPDF(pdf)
    # Datum, Uhrzeit, Ort, Name
    setDatetoPDF(pdf)
    # Seitenzahl
    setSeitenzahl(pdf, seitenzahl)

def setFirstPage(pdf):
    pdf.add_page()

    # Anwendungsuebersicht
    setAnwendungsuebersicht(pdf)
    # Datenbank
    setDatenbankuebersicht(pdf)
    # Datenvorbereitung
    setDatenvorbereitunguebersicht(pdf)

def setSecondPage(yaml_list, pdf):
    pdf.add_page()

    # Datenvorbereitung - Einstellung / Konfiguration
    setDatenvorbereitungKonfigurationsuebersicht(pdf)
    # KI-Training
    setKITraining(yaml_list, pdf)

def setThirdPage(pdf, model, test_image_dir):
    pdf.add_page()

    # KI-Auswertung (Matrix und Ergebnisse)
    setKITrainingAuswertung(pdf)


    # KI Faseranalyse aller Test-Bilder
    setKIFaserAnalyse(pdf, model, test_image_dir)

def setFourthPage(pdf):
    pathtomodel = "/home/alen/.pyenv/runs/classify/train92"
    getArgstoPDF(pathtomodel)

# ----------------------------------------------------------------------------------
# PDF Komplett
# ----------------------------------------------------------------------------------

def createFancyReport(pdf_path):
    pdf = CustomPDF()
    pdf.set_title("Dokumentations- und Ergebnisbericht")

    # erhalte zuerst Informationen
    pathtomodel = "/home/alen/.pyenv/runs/classify/train91/"
    yaml_list = getArgstoPDF(pathtomodel) # hole Daten aus args.yaml

    # erstelle erste Seite
    setFirstPage(pdf)

    # erstelle zweite Seite
    setSecondPage(yaml_list, pdf)

    # ertelle dritte und weitere Seiten
    model_Path = "/home/alen/.pyenv/runs/classify/train92/weights/best.pt"
    model = YOLO(model_Path)
    test_image_dir = "/home/alen/Downloads/YOLOTRAINTEST"
    setThirdPage(pdf, model, test_image_dir)



    pdf.output(pdf_path)
    return pdf
