import cv2
import numpy as np
import os.path
from pathlib import Path
import random
import shutil
import glob
from PIL import Image
from distutils.dir_util import copy_tree # copy Images
import inspect # show function
import streamlit as st
import os


#-----------------------------------------------------------
# Funktion bei "Template-Bilder" zur Speicherung in den Arrays
def templateStrings(dbNames, BilderPath, allowed_extensions=None):
    gesamtDateien = 0
    if allowed_extensions is None:
        allowed_extensions = [".jpg", ".jpeg", ".png", ".tif"]

    if isinstance(BilderPath, list):
        for path in BilderPath:
            if not os.path.exists(path):
                st.error(f"Der Pfad {path} existiert nicht.")
                continue

            klasse = path.split("/")

            want = None
            for name in dbNames:
                if name in klasse:
                    want = name

            if want is None:
                continue

            # Zähle die Dateien im Verzeichnis mit den erlaubten Erweiterungen
            try:
                dateien = [
                    f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f)) and any(f.endswith(ext) for ext in allowed_extensions)
                ]
                #st.info(f"{len(dateien)} Dateien")
                gesamtDateien += len(dateien)

            except Exception as e:
                st.error(f"Fehler beim Zugriff auf {path}: {e}")
        return gesamtDateien

    if isinstance(BilderPath, str):
        path = BilderPath
        klasse = path.split("/")

        want = None
        for name in dbNames:
            if name in klasse:
                want = name

            if want is None:
                continue

        # Zähle die Dateien im Verzeichnis mit den erlaubten Erweiterungen
        try:
            dateien = [
                f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f)) and any(f.endswith(ext) for ext in allowed_extensions)
            ]
            st.info(f"{len(dateien)} Bilder")
            return len(dateien)
        except Exception as e:
            st.error(f"Fehler beim Zugriff auf {path}: {e}")


def getdatenbankBilderPath(datenbank_bilderPath, datenbank, number):  # erstellt Datenbank-Verzeichnisspfade
    #print("getdatenbankBilderPath")
    datenbank_bilderPath.clear()
    bilderpath = "BildDatenbank/"
    if number == 1:
        for daten in datenbank:
            secondName = daten[-4:]  # Real, Synt
            if secondName == "Synt":
                secondName = "Synthetisch"
            firstName = daten[:-4]
            firstName = formateigeneKlassen(firstName)

            path = os.path.join(bilderpath + secondName, firstName + "/")
            # searchpath = bilderpath + name + "/" + firstName + "/"
            if os.path.exists(path):
                datenbank_bilderPath.append(path)

        return datenbank_bilderPath
    if number == 2:
        for daten in datenbank:
            firstName = daten.split()[-1]  # Real, Synt
            secondName = daten.split()[-2]  # Klassen
            if secondName == "Baumwolle":
                thirdName = daten.split()[-3]  # merzerisierte
                secondName = thirdName + " " + secondName

            if firstName == "(real)":
                firstName = "Real"
            if firstName == "(synthetisch)":
                firstName = "Synthetisch"
            path = os.path.join(bilderpath + firstName, secondName + "/")
            if os.path.exists(path):
                datenbank_bilderPath.append(path)

        return datenbank_bilderPath

def changeNamesofDatenbankforDVB(array):  # ändert nur den Anzeigenamen im Info für die ausgewählten Datenbanken
    ordner_namen = []
    for daten in array:
        newname = daten.split()
        print(newname)
        firstName = daten[:-4]
        secondName = daten[-4:]
        print(firstName)
        if firstName == "Seide":
            firstName = "Maulbeerseide"
        if firstName == "rWolle":
            firstName = "Rohbaumwolle"
        if firstName == "merzWolle":
            firstName = "merzerisierte Baumwolle"
        if firstName == "Tussah":
            firstName = "Tussahseide"
        print(secondName)
        if secondName == "Synt":
            secondName = "Synthetisch"
        ordner_namen.append(firstName + " " + "(" + secondName.lower() + ")")

    return ordner_namen

def getNamesofDatenbank(datenbank_bilderPath):  # erstellt die Ordner_Namen zum erstellen der Ordner im ZielPath
    #print("getNamesofDatenbank")
    ordner_namen = []
    for daten in datenbank_bilderPath:
        # newname = daten.split()
        # print(newname)
        firstName = daten.split("/")[-2]
        secondName = daten.split("/")[-3]
        # print(firstName)
        # print(secondName)
        ordner_namen.append(firstName + " " + "(" + secondName + ")")

    return ordner_namen

def getonlynamesandpictures(zielPath):
    anzahl = len(os.listdir(zielPath))
    files_dir = [
        f for f in os.listdir(zielPath) if os.path.isdir(os.path.join(zielPath, f))
    ]
    #for directory in files_dir:
    #    if directory == ("test" or "val" or "train"):
    #        files_dir.remove(directory)

    return files_dir, anzahl



# erstelle einzelne Klassen Ordner in Zielpfad
def erstelleOrdner(zielPath, ordner_namen):
    #print("erstelleOrdner")
    # Zielordner aus dem Pfad erstellen
    zielPath = Path(zielPath)
    zielPath.mkdir(parents=True, exist_ok=True)

    #Erstelle Klassen_Ordner
    paths = {}
    for ordner in ordner_namen:
        ordner_path = zielPath / ordner
        ordner_path.mkdir(parents=True, exist_ok=True)
        paths[ordner] = ordner_path

    return paths

# erstelle Zielpfade und speichere in Array
def erstelleOrdnerPfade(zielPath, ordner_namen):
    #print("erstelleOrdnerPfade")
    klassenPfade = []
    if zielPath != "":
        for ordner in ordner_namen:
            #newvar = zielPath.split("/")[-1]
            #if newvar != "":
            #    zielPath = zielPath + "/"
            newpath = str(zielPath + ordner + "/")
            #print("newpath", newpath)
            try:
                if os.path.isdir(newpath):
                    klassenPfade.append(newpath)
            except:
                continue
        #stelle sicher, dass "/" immer am Ende hinzugefügt wird, auch wenn der Benutzer es vergisst

    return klassenPfade


#Prüfe ob Zielpfad auf / endet oder nicht
def proofendingzielPath(zielPath):
    #print("proofendingzielPath")
    newvar = zielPath.split("/")[-1]
    if newvar != "":
        zielPath = zielPath + "/"
        return zielPath
    return zielPath
#-------------------------------------------------------------------------------------------
#Funktion die die Auswahl der eigenen ausgesuchten Klassen mit "richtigem" Namen wieder zurück gibt
def formateigeneKlassen(eigeneKlassen):
    #print("formateigeneKlassen")
    if isinstance(eigeneKlassen, str):
        if eigeneKlassen == "Seide":
            eigeneKlassen = "Maulbeerseide"
        if eigeneKlassen == "Tussah":
            eigeneKlassen = "Tussahseide"
        if eigeneKlassen == "rWolle":
            eigeneKlassen = "Rohbaumwolle"
        if eigeneKlassen == "merzWolle":
            eigeneKlassen = "merzerisierte Baumwolle"
        return eigeneKlassen

    if isinstance(eigeneKlassen, list):
        for i in range(len(eigeneKlassen)):
            if eigeneKlassen[i] == "Seide":
                eigeneKlassen[i] = "Maulbeerseide"
            if eigeneKlassen[i] == "Tussah":
                eigeneKlassen[i] = "Tussahseide"
            if eigeneKlassen[i] == "rWolle":
                eigeneKlassen[i] = "Rohbaumwolle"
            if eigeneKlassen[i] == "merzWolle":
                eigeneKlassen[i] = "merzerisierte Baumwolle"
        return eigeneKlassen


def showuploadBoxen(ordner_namen):
    #print("showuploadBoxen")
    Upload_Boxen = {}
    col1, col2 = st.columns(2)

    with col1:
        for i in range(len(ordner_namen)):
            if i % 2 == 0:
                files = st.file_uploader(
                    f"**{ordner_namen[i]}**",
                    label_visibility="visible",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'],
                    key=ordner_namen[i]
                )
                Upload_Boxen[ordner_namen[i]] = files  # Speichern der hochgeladenen Dateien

    with col2:
        for i in range(len(ordner_namen)):
            if i % 2 == 1:
                files = st.file_uploader(
                    f"**{ordner_namen[i]}**",
                    label_visibility="visible",
                    accept_multiple_files=True,
                    type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'webp'],
                    key=ordner_namen[i]
                )
                Upload_Boxen[ordner_namen[i]] = files  # Speichern der hochgeladenen Dateien

    return Upload_Boxen
# Testfunktion zum Verständnis für die Ablage der Dateien
#def zeigeBildNamen(ordner_namen):
#    for ordner in ordner_namen:
#        uploaded_files = st.session_state.get(ordner) # interner Speicherort und Ablage der Dateien
#        if uploaded_files:
#            for uploaded_file in uploaded_files:
#                st.info(f"Filename: {uploaded_file.name} in Ordner: {ordner}")  # Zeigt den Dateinamen an
#                # Optional: andere Dateioperationen wie uploaded_file.read() hier hinzufügen

def saveuploadedFiles(ordner_namen):
    #print("saveuploadedFiles")
    uploaded_files = []
    for ordner in ordner_namen:
        uploaded_file = st.session_state.get(ordner) # interner Speicherort und Ablage der Dateien
        if uploaded_file:
            for file in uploaded_file:
                uploaded_files.append((ordner, file))
    #for ordner2, file in uploaded_files:
    #    st.info(f"filename:{file.name}")
    # letzten beiden nur zum Verständnis

    return uploaded_files
#--------------------------------------------------------------------------------------------
# Wird benötigt für die Seite KI-Training

def processDBselectionUploadBox(möglicheKlassen, class_names):
    #print("processDBselectionUploadBox")
    eigeneKlassen = st.pills(
        "Wähle hier deine Klassen aus für den Upload",
        möglicheKlassen,
        selection_mode="multi",
        default=None,
        disabled=st.session_state.get("switchzielPath", False), #switcht auf disabled, enabled, wenn True/False
        key ="eigeneKlassen",

    )
    eigeneKlassen = formateigeneKlassen(eigeneKlassen)
    if eigeneKlassen:
        class_names.clear()
        for i in eigeneKlassen:
            class_names.append(i)


    return (class_names, eigeneKlassen)

def processDBselectionUploadBox(möglicheKlassen):
    #print("processDBselectionUploadBox")
    eigeneKlassen = st.pills(
        "Wähle hier deine Klassen aus für den Upload",
        möglicheKlassen,
        selection_mode="multi",
        default=None,
        disabled=st.session_state.get("switchzielPath", False), #switcht auf disabled, enabled, wenn True/False
        key ="eigeneKlassen",

    )


    return eigeneKlassen


def getNamesofDir(zielPath):
    #print("getNamesofDir")
    eigeneKlassen = []
    andereKlassen = []
    file = os.listdir(zielPath)
    for name in file:
        name = name.split()
        andereKlassenNamen = ""
        #print(name)
        for i in name:
            andereKlassenNamen += str(i)
        andereKlassen.append(andereKlassenNamen)

        firstName = name[0]
        if name[0] == "merzerisierte":
            secondName = name[1]
            #print(firstName + " " + secondName)
            newName = firstName + " " + secondName
            if newName not in eigeneKlassen:
                eigeneKlassen.append(firstName + " " + secondName)

            else:
                continue

        else:
            #print(firstName)
            if firstName not in eigeneKlassen:
                eigeneKlassen.append(firstName)
            else:
                continue
    return eigeneKlassen, andereKlassen
    #eigeneKlassen = Klassen in bereinigter Form
    #andereKlassen = Klassen aus Zielpfad mit (real/synth..)

def lookforpictures(zielPath):
    #print("lookforpictures")
    counter = 0
    try:
        direction = os.listdir(zielPath)
        for dir in direction:
            full_path = os.path.join(zielPath, dir)
            if os.path.isdir(full_path):  # Prüft, ob es ein Unterordner ist
                liste = os.listdir(full_path)
                for file in liste:
                    if file.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".bmp")):
                        counter += 1
        return counter
    except:
        return counter

#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
# Zur Löschung / Bereinigung der Bilder im Klassenordner
def clearImages(zielPath, ordner_namen):
    #print("clearImages")
    #ordner_namen = ["merzWolle", "Seide", "Flachs", "rWolle"]
    # Zielpfad zu bestehendem Ordner im Zielordner
    for ordner in ordner_namen:
        zielOrdner = os.path.join(zielPath, ordner)
        if os.path.exists(zielOrdner):
            for file in os.listdir(zielOrdner):
                file_path = os.path.join(zielOrdner, file)  # Vollständiger Pfad
                try:
                    os.remove(file_path)  # Datei löschen
                except Exception as e:
                    print(f"Fehler beim Löschen der Datei {file_path}: {e}")

# Kopiere Bilder aus Datenbank oder Uploads des Users
def copyImages(DBselection, ordner_namen, dbselectedPath, zielPath):
    #print("copyImages")
    # dbselectedPath = datenbank_bilderPath oder uploaded_files
    # Liste der Ordnernamen, in die Bilder kopiert werden sollen
    success = True  # Erfolgsvariable initialisieren

    try:
        # Verarbeiten von "Datenbank Bilder"
        if DBselection == "Datenbank Bilder":
            if isinstance(dbselectedPath, str):
                path = dbselectedPath
                #hier wählt der genau die Ordner aus, die sich im exakten Pfad befinden
                from_directory = dbselectedPath
                namePath = str(path)  # Pfad mit oder ohne / am Ende
                #print("namepath: ", namePath)
                namePath1 = namePath.split("/")[-2]  # OrdnerName
                namePath2 = namePath.split("/")[-3]  # Real, Synt
                #print("namepath: ", namePath1)
                #print("namepath2: ", namePath2)
                newNamePath = namePath1 + " " + "(" + namePath2 + ")"
                #und kopiert diese ins Zielpfad --> Exakter Ordner ins Zielpfad...
                to_directory = zielPath + newNamePath
                copy_tree(from_directory, to_directory)
                success = True

            if isinstance(dbselectedPath, list):
                for path in dbselectedPath:
                    namePath = str(path) #Pfad mit oder ohne / am Ende
                    #print("namepath: ", namePath)
                    namePath1 = namePath.split("/")[-2] #OrdnerName
                    namePath2 = namePath.split("/")[-3]  # Real, Synt
                    #print("namepath: ", namePath1)
                    #print("namepath2: ", namePath2)
                    newNamePath = namePath1 + " " + "(" + namePath2 + ")"
                    #print("newNamePath: ", newNamePath)

                    from_directory = path
                    #print("from_directory: ", from_directory)
                    to_directory = zielPath + newNamePath
                    copy_tree(from_directory, to_directory)
                    success = True

        # Verarbeiten von "Eigene Bilder"
        elif DBselection == "Eigene Bilder":
            for ordner, file in dbselectedPath:
                if file:
                    #print("file: ", file)
                    filename = file.name
                    #print("filename: ", filename)
                    #zielOrdner = os.path.join(zielPath, ordner)
                    zielDateiPfad = os.path.join(zielPath, ordner, filename)
                    #print("zielDateiPfad: ", zielDateiPfad)
                    # Dateiinhalt speichern
                    with open(zielDateiPfad, "wb") as f:
                        f.write(file.read())
                        success = True

    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
        success = False

    return success

# Funktion zum Öffnen von Bildern
def open_image(zielPath, ordner_namen):
    #print("open_image")
    try:
        for ordner in ordner_namen:
            zielOrdner = os.path.join(zielPath, ordner)

            # Glob-Muster, um alle Dateien im Ordner zu finden
            suchmuster = os.path.join(zielOrdner, '**', '*.*')  # Suche alle Dateien
            for file in glob.glob(suchmuster, recursive=True):
                # Bild öffnen
                basename = os.path.basename(file)
                image = cv2.imread(file)
                if image is None:
                    continue

                # Bilddaten und Infos als Tuple zurückgeben
                yield file, image, basename, zielOrdner
    except Exception as e:
        st.error(f"Fehler beim Verarbeiten von OpenImages")
        return False

def randomdrehen(image):
    #print("randomdrehen")
    try:
        randomzahl = random.randint(0,2)
        if randomzahl == 2:
            return cv2.rotate(image, cv2.ROTATE_180)
        else:
            return image
    except Exception as e:
        st.write(f"Fehler bei der Randomdrehen-Funktion")
        return False

def schaerfen(image):
    #print("schaerfen")
    try:
        # Create the sharpening kernel
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) #Gewichte
        # Sharpen the image
        return cv2.filter2D(image, -1, kernel)
    except Exception as e:
        st.write(f"Fehler bei der Schärfen-Funktion")
        return False

def rauschen(image, kernel):
    #print("rauschen")
    #kernel = Kernelgröße für das Rauschen des Bildes, je höher, desto mehr Rauschen
    try:
        return cv2.GaussianBlur(image, (kernel, kernel), 0)
    except Exception as e:
        st.write(f"Fehler bei der rauschen-Funktion")
        return False

def schwarzweiß(image):
    #print("schwarzweiß")
    try:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except:
        st.write(f"Fehler bei der SchwarzWeiß-Funktion")
        return False

def schneiden(image, percentage):
    #print("schneiden")
    #percentage = Zuschneiden in %
    try:
        # Bildgröße ausmessen
        height, width = image.shape[:2]

        # Prozentsätze für die vier Quadranten
        crop_percentages = [
            (0.0, 0.0, percentage, percentage),  # Oben links
            (percentage, 0.0, 1.0, percentage),  # Oben rechts
            (0.0, percentage, percentage, 1.0),  # Unten links
            (percentage, percentage, 1.0, 1.0)   # Unten rechts
        ]

        for (x_start, y_start, x_end, y_end) in crop_percentages:
            x1 = int(x_start * width)
            y1 = int(y_start * height)
            x2 = int(x_end * width)
            y2 = int(y_end * height)

        # Zuschneiden und Resizen
        cropped_image = image[y1:y2, x1:x2]
        return cropped_image
    except:
        st.write(f"Fehler bei der Schneiden-Funktion")
        return False

def kontrastAdjust(image, alpha, beta):
    #print("kontrastAdjust")
    #alpha = Helligkeitswert
    #beta = Kontrastwert
    try:
        return cv2.convertScaleAbs( image, alpha=alpha, beta=beta)
    except:
        st.write(f"Fehler bei der kontrastAdjust-Funktion")
        return False

def groesseAendern(image, resize_pictureGroesse):
    #print("groesseAendern")
    #resize_pictureGroesse = Wert für Breite und Höhe
    BreiteUndHöhe = resize_pictureGroesse
    try:
        return cv2.resize(image, (BreiteUndHöhe,BreiteUndHöhe), interpolation=cv2.INTER_AREA)
    except:
        st.error(f"Fehler bei der GroesseAendern-Funktion")
        return False

def save_image(image, basename, zielOrdner):
    #print("save_image")
    try:
        os.chdir(zielOrdner)
        cv2.imwrite(basename, image)
    except:
        st.write(f"Fehler beim speichern der Bilder")
        return False


def formatPictures(file, image, basename, zielOrdner, bildformat_select):
    #print("formatPictures")
    #bildformat_select = PNG oder JPEG
    try:
        file_ending = os.path.splitext(file)[-1]  # Dateiendung z. B. ".tif"

        if bildformat_select == "PNG" and "png" not in file_ending:
            new_file = os.path.join(zielOrdner, basename.replace(file_ending, '.png'))
            success = cv2.imwrite(new_file, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            #print("old-file: ", file)
            #print("new-file: ", new_file)
        if bildformat_select == "JPEG" and ("jpg" not in file_ending and "jpeg" not in file_ending):
            new_file = os.path.join(zielOrdner, basename.replace(file_ending, '.jpg'))
            success = cv2.imwrite(new_file, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
            #print("old-file: ", file.name)
            #print("new-file: ", new_file.name)
        # Altes Bild löschen, wenn das Speichern erfolgreich war
        if success:
            #print("remove file: ", file)
            os.remove(file)
            return new_file
        else:
            return image


    except:
        st.write(f"Fehler bei der FormatPictures-Funktion")
        return False


def flippen(file, image, zielOrdner):
    #print("flippen")
    # Bild flippen
    try:
        f2 = cv2.flip(image, 1)  # nach rechts nach links
        f3 = cv2.flip(image, 0)  # auf den Kopf gestellt (geflippt)
        f4 = cv2.flip(image, -1)  # auf den Kopf gestellt (original)
        f1 = image # bleibt im Urzustand

        # Dateien speichern
        os.chdir(zielOrdner)
        name = os.path.splitext(file)[0]
        file_ending = os.path.splitext(file)[-1]

        cv2.imwrite(name + '_f2' + file_ending, f2)
        cv2.imwrite(name + '_f3' + file_ending, f3)
        cv2.imwrite(name + '_f4' + file_ending, f4)
        os.rename(file, name + '_f1' + file_ending)
        #return f1, f2, f3, f4

    except:
        st.write(f"Fehler bei der Flippen-Funktion")
        return False

def splitten(file, number, image, zielOrdner):
    #print("splitten")
    try:
        # Bildgröße abrufen
        number = int(number)
        height, width= image.shape[:2]

        # Sicherstellen, dass der Zielordner existiert
        os.chdir(zielOrdner)
        name = os.path.splitext(file)[0]
        file_ending = os.path.splitext(file)[-1]

        if number == 4:
            markWidth = int(width / 2)
            markHeight = int(height / 2)

            # Die vier Teile definieren
            new1 = image[0:markHeight, 0:markWidth]  # Oben links
            cv2.imwrite(name + '_s1' + file_ending, new1)
            new2 = image[0:markHeight, markWidth:width]  # Oben rechts
            cv2.imwrite(name + '_s2' + file_ending, new2)
            new3 = image[markHeight:height, 0:markWidth]  # Unten links
            cv2.imwrite(name + '_s3' + file_ending, new3)
            new4 = image[markHeight:height, markWidth:width]  # Unten rechts
            cv2.imwrite(name + '_s4' + file_ending, new4)
            os.remove(file)

        if number == 6:
            markWidth1 = int(width / 3)
            markWidth2 = int(2 * width / 3)
            markHeight = int(height / 2)

            # Die sechs Teile definieren
            new1 = image[0:markHeight, 0:markWidth1]  # Oben links
            cv2.imwrite(name + '_s1' + file_ending, new1)
            new2 = image[0:markHeight, markWidth1:markWidth2]  # Oben Mitte
            cv2.imwrite(name + '_s2' + file_ending, new2)
            new3 = image[0:markHeight, markWidth2:width]  # Oben rechts
            cv2.imwrite(name + '_s3' + file_ending, new3)
            new4 = image[markHeight:height, 0:markWidth1]  # Unten links
            cv2.imwrite(name + '_s4' + file_ending, new4)
            new5 = image[markHeight:height, markWidth1:markWidth2]  # Unten Mitte
            cv2.imwrite(name + '_s5' + file_ending, new5)
            new6 = image[markHeight:height, markWidth2:width]  # Unten rechts
            cv2.imwrite(name + '_s6' + file_ending, new6)

        if number == 8:
            markWidth1 = int(width / 4)
            markWidth2 = int(2 * width / 4)
            markWidth3 = int(3 * width / 4)
            markHeight = int(height / 2)

            # Die acht Teile definieren
            new1 = image[0:markHeight, 0:markWidth1]  # Oben ganz links
            cv2.imwrite(name + '_s1' + file_ending, new1)
            new2 = image[0:markHeight, markWidth1:markWidth2]  # Oben links Mitte
            cv2.imwrite(name + '_s2' + file_ending, new2)
            new3 = image[0:markHeight, markWidth2:markWidth3]  # Oben rechts Mitte
            cv2.imwrite(name + '_s3' + file_ending, new3)
            new4 = image[0:markHeight, markWidth3:width]  # Oben ganz rechts
            cv2.imwrite(name + '_s4' + file_ending, new4)
            new5 = image[markHeight:height, 0:markWidth1]  # Unten ganz links
            cv2.imwrite(name + '_s5' + file_ending, new5)
            new6 = image[markHeight:height, markWidth1:markWidth2]  # Unten links Mitte
            cv2.imwrite(name + '_s6' + file_ending, new6)
            new7 = image[markHeight:height, markWidth2:markWidth3]  # Unten rechts Mitte
            cv2.imwrite(name + '_s7' + file_ending, new7)
            new8 = image[markHeight:height, markWidth3:width]  # Unten ganz rechts
            cv2.imwrite(name + '_s8' + file_ending, new8)
            os.remove(file)

        if number == 12:
            # Die Breiten- und Höhenabschnitte berechnen
            markWidth1 = int(width / 3)
            markWidth2 = int(2 * width / 3)

            markHeight1 = int(height / 4)
            markHeight2 = int(2 * height / 4)
            markHeight3 = int(3 * height / 4)

            # Die 12 Teile definieren und speichern
            new1 = image[0:markHeight1, 0:markWidth1]  # Oben links
            cv2.imwrite(name + '_s1' + file_ending, new1)
            new2 = image[0:markHeight1, markWidth1:markWidth2]  # Oben Mitte
            cv2.imwrite(name + '_s2' + file_ending, new2)
            new3 = image[0:markHeight1, markWidth2:width]  # Oben rechts
            cv2.imwrite(name + '_s3' + file_ending, new3)
            new4 = image[markHeight1:markHeight2, 0:markWidth1]  # Zweite Zeile links
            cv2.imwrite(name + '_s4' + file_ending, new4)
            new5 = image[markHeight1:markHeight2, markWidth1:markWidth2]  # Zweite Zeile Mitte
            cv2.imwrite(name + '_s5' + file_ending, new5)
            new6 = image[markHeight1:markHeight2, markWidth2:width]  # Zweite Zeile rechts
            cv2.imwrite(name + '_s6' + file_ending, new6)
            new7 = image[markHeight2:markHeight3, 0:markWidth1]  # Dritte Zeile links
            cv2.imwrite(name + '_s7' + file_ending, new7)
            new8 = image[markHeight2:markHeight3, markWidth1:markWidth2]  # Dritte Zeile Mitte
            cv2.imwrite(name + '_s8' + file_ending, new8)
            new9 = image[markHeight2:markHeight3, markWidth2:width]  # Dritte Zeile rechts
            cv2.imwrite(name + '_s9' + file_ending, new9)
            new10 = image[markHeight3:height, 0:markWidth1]  # Unten links
            cv2.imwrite(name + '_s10' + file_ending, new10)
            new11 = image[markHeight3:height, markWidth1:markWidth2]  # Unten Mitte
            cv2.imwrite(name + '_s11' + file_ending, new11)
            new12 = image[markHeight3:height, markWidth2:width]  # Unten rechts
            cv2.imwrite(name + '_s12' + file_ending, new12)
            os.remove(file)

        if number == 16:
            # Die Breiten- und Höhenabschnitte berechnen
            markWidth1 = int(width / 4)  # 1/4 der Breite
            markWidth2 = int(2 * width / 4)  # 2/4 der Breite
            markWidth3 = int(3 * width / 4)  # 3/4 der Breite

            markHeight1 = int(height / 4)  # 1/4 der Höhe
            markHeight2 = int(2 * height / 4)  # 2/4 der Höhe
            markHeight3 = int(3 * height / 4)  # 3/4 der Höhe

            # Die 16 Teile definieren und speichern
            new1 = image[0:markHeight1, 0:markWidth1]  # Oben links ganz
            cv2.imwrite(name + '_s1' + file_ending, new1)
            new2 = image[0:markHeight1, markWidth1:markWidth2]  # Oben links Mitte
            cv2.imwrite(name + '_s2' + file_ending, new2)
            new3 = image[0:markHeight1, markWidth2:markWidth3]  # Oben rechts Mitte
            cv2.imwrite(name + '_s3' + file_ending, new3)
            new4 = image[0:markHeight1, markWidth3:width]  # Oben rechts ganz
            cv2.imwrite(name + '_s4' + file_ending, new4)
            new5 = image[markHeight1:markHeight2, 0:markWidth1]  # Zweite Zeile links ganz
            cv2.imwrite(name + '_s5' + file_ending, new5)
            new6 = image[markHeight1:markHeight2, markWidth1:markWidth2]  # Zweite Zeile links Mitte
            cv2.imwrite(name + '_s6' + file_ending, new6)
            new7 = image[markHeight1:markHeight2, markWidth2:markWidth3]  # Zweite Zeile rechts Mitte
            cv2.imwrite(name + '_s7' + file_ending, new7)
            new8 = image[markHeight1:markHeight2, markWidth3:width]  # Zweite Zeile rechts ganz
            cv2.imwrite(name + '_s8' + file_ending, new8)
            new9 = image[markHeight2:markHeight3, 0:markWidth1]  # Dritte Zeile links ganz
            cv2.imwrite(name + '_s9' + file_ending, new9)
            new10 = image[markHeight2:markHeight3, markWidth1:markWidth2]  # Dritte Zeile links Mitte
            cv2.imwrite(name + '_s10' + file_ending, new10)
            new11 = image[markHeight2:markHeight3, markWidth2:markWidth3]  # Dritte Zeile rechts Mitte
            cv2.imwrite(name + '_s11' + file_ending, new11)
            new12 = image[markHeight2:markHeight3, markWidth3:width]  # Dritte Zeile rechts ganz
            cv2.imwrite(name + '_s12' + file_ending, new12)
            new13 = image[markHeight3:height, 0:markWidth1]  # Unten links ganz
            cv2.imwrite(name + '_s13' + file_ending, new13)
            new14 = image[markHeight3:height, markWidth1:markWidth2]  # Unten links Mitte
            cv2.imwrite(name + '_s14' + file_ending, new14)
            new15 = image[markHeight3:height, markWidth2:markWidth3]  # Unten rechts Mitte
            cv2.imwrite(name + '_s15' + file_ending, new15)
            new16 = image[markHeight3:height, markWidth3:width]  # Unten rechts ganz
            cv2.imwrite(name + '_s16' + file_ending, new16)
            os.remove(file)

    except Exception as e:
        print(f"Fehler bei der Splitten-Funktion: {str(e)}")
        return False

# Anzeigen der Funktionen für die Lehrzwecke
def show_function(functionToShow):
    if functionToShow == "Größe ändern":
        function = groesseAendern
    if functionToShow == "Drehen":
        function = randomdrehen
    if functionToShow == "Schärfen":
        function = schaerfen
    if functionToShow == "Schneiden":
        function = schneiden
    if functionToShow == "Schwarz Weiß":
        function = schwarzweiß
    if functionToShow == "Flippen":
        function = flippen
    if functionToShow == "Format ändern":
        function = formatPictures
    if functionToShow == "Kontrast&Helligkeit":
        function = kontrastAdjust
    if functionToShow == "Rauschen":
        function = rauschen
    if functionToShow == "Splitten":
        function = splitten

    lines = inspect.getsource(function)
    st.code(lines)


def show_images(zielOrdner, ordner_namen):
    try:
        images = {ordner: [] for ordner in ordner_namen}

        # Bilder aus den Ordnern laden
        for ordner in ordner_namen:
            ordnerpfad = os.path.join(zielOrdner, ordner)
            dateien = glob.glob(f"{ordnerpfad}/*")

            # Nur das erste Bild verwenden
            if dateien:
                images[ordner].append(dateien[0])

        st.write("Vorschau der Bilder:")
        # Bilder anzeigen
        numberArray = len(ordner_namen)
        columns = st.columns(numberArray)
        for idx, (ordner, imgs) in enumerate(images.items()):
            with columns[idx]:
                for img in imgs:
                    st.image(img, caption=ordner)
    except Exception as e:
        st.write(f"Fehler bei der ShowImages-Funktion: {e}")

def setTestBilder(zielOrdner, ordner_namen):
    # zielOrdner = Ordnerpfad
    # ordner_namen = einzelne Ordner die durchgegangen werden sollen
    # test_anzahl = Anzahl der Testbilder die gespeichert werden sollen

    test_ordner_liste = []

    for ordner in ordner_namen:
        # Pfade setzen
        ordnerpfad = os.path.join(zielOrdner, ordner)
        testordnerpfad = os.path.join(zielOrdner, f"{ordner}_test")
        test_ordner_liste.append(testordnerpfad)

        # Testordner erstellen (wenn er noch nicht existiert)
        if not os.path.exists(testordnerpfad):
            os.mkdir(testordnerpfad)
            #print(f"Testordner erstellt: {testordnerpfad}")
        else:
            print(f"Testordner existiert bereits: {testordnerpfad}")

        # Alle Bilder im Ordner
        alle_bilder = os.listdir(ordnerpfad)
        anzahl = len(alle_bilder)
        #print(f"{ordner} hat {anzahl} Bilder.")

        # Anzahl Testbilder bestimmen
        if 5 < anzahl < 10:
            test_anzahl = 5
        elif 1 < anzahl <= 5:
            test_anzahl = 1
        elif anzahl >= 10:
            test_anzahl = min(int(anzahl * 0.1), 10)
        else:
            test_anzahl = 0

        #print(f"Testbilder: {test_anzahl}")

        # Zufällig Bilder auswählen und verschieben
        if test_anzahl > 0:
            test_bilder = random.sample(alle_bilder, test_anzahl)
            for bild in test_bilder:
                quelle = os.path.join(ordnerpfad, bild)
                ziel = os.path.join(testordnerpfad, bild)
                shutil.move(quelle, ziel)
                #print(f"Verschoben: {bild}")

    # Erstelle den Hauptordner "TEST"
    haupt_test_ordner = os.path.join(zielOrdner, "test")
    if not os.path.exists(haupt_test_ordner):
        os.mkdir(haupt_test_ordner)
        #print(f"Haupt-Testordner erstellt: {haupt_test_ordner}")

    # Verschiebe alle _test-Ordner in TEST
    for testordnerpfad in test_ordner_liste:
        zielpfad = os.path.join(haupt_test_ordner, os.path.basename(testordnerpfad))
        if not os.path.exists(zielpfad):  # doppelt vermeiden
            shutil.move(testordnerpfad, zielpfad)
            #print(f"{testordnerpfad} -» {zielpfad}")

def setTrainAndValBilder(zielOrdner, ordner_namen):
    # Erstelle train und val Ordner
    train_ordner = os.path.join(zielOrdner, "train")
    val_ordner = os.path.join(zielOrdner, "val")

    for ordner in ordner_namen:
        ordnerpfad = os.path.join(zielOrdner, ordner)
        # Bilder auflisten
        alle_bilder = [f for f in os.listdir(ordnerpfad) if os.path.isfile(os.path.join(ordnerpfad, f))]
        random.shuffle(alle_bilder)

        # Aufteilen in 70% train und 30% val
        trenner = int(len(alle_bilder) * 0.7)
        train_bilder = alle_bilder[:trenner]
        val_bilder = alle_bilder[trenner:]

        # Zielpfade erstellen (Klassenordner in train und val)
        train_klassenordner = os.path.join(train_ordner, ordner)
        val_klassenordner = os.path.join(val_ordner, ordner)

        for pfad in [train_klassenordner, val_klassenordner]:
            if not os.path.exists(pfad):
                os.makedirs(pfad)
                # Bilder verschieben
        for bild in train_bilder:
            shutil.move(os.path.join(ordnerpfad, bild), os.path.join(train_klassenordner, bild))

        for bild in val_bilder:
            shutil.move(os.path.join(ordnerpfad, bild), os.path.join(val_klassenordner, bild))

    # Wenn alle Bilder verschoben sind, lösche den ursprünglichen Ordner
    for ordner in ordner_namen:
        ordnerpfad = os.path.join(zielOrdner, ordner)
        if (
                os.path.isdir(ordnerpfad)
                and not os.listdir(ordnerpfad)
                and ordner not in ["test", "train", "val"]
        ):
            os.rmdir(ordnerpfad)
            print(f"Ordner {ordner} wurde gelöscht.")

def get_all_unique_folder_names(root_path): #zeigt in KI-Training alle Unterordner -> Klassen
    unique_folders = set()
    exclude_folders = {"train", "test", "val"}

    for dirpath, dirnames, filenames in os.walk(root_path):
        for dirname in dirnames:
            if dirname not in exclude_folders:
                # "_test" entfernen, wenn vorhanden
                clean_name = dirname.replace("_test", "").strip()
                unique_folders.add(clean_name)

    return sorted(list(unique_folders))

def count_images_in_folder(root_path): #zählt in KI-Training alle Bilder im Ordner
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    count = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                count += 1

    return count

