import streamlit as st
from PIL import Image
import base64
from io import BytesIO
#import importlib  # Zum dynamischen Import von Modulen


#---------------------------------------------------------
def main():
    # Page Setup
    st.set_page_config(
        layout="wide",
        page_title = "KI Textil",
        page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
    )
    #--------------------------
    image_width = 100

    st.title("FibreAI")

    st.write("FibreAI ist ein intelligentes KI-Tool für die Klassifikation textiler Fasern anhand von Querschnittsbildern. Dieses KI-Tool wurde im Rahmen der Lehrveranstaltung **KI im Textil: Erleben, Verstehen, Anwenden** entwickelt und bietet die Möglichkeit Künstliche Intelligenz in der Textiltechnik hautnah zu erleben.")
    st.write("Die Startseite gibt nachfolgend einen Überblick über die integrierten Funktionen des Tools.")

    st.subheader("KI-Faseranalyse:")
    st.write("Eine unbekannte Faser soll bestimmt werden? Dann ist die „KI-Faseranalyse“ genau die richtige Funktion. Mit Hilfe eines Querschnittsbildes der unbekannten Faser lässt sich hier die zugehörige Faserart bestimmen.")
    st.write("**Zusatzoption:** Für die Faserbestimmung lassen sich außerdem unterschiedliche KI-Modelle auswählen. Dies ist besonders interessant, wenn vorab eigene Modelle erstellt und trainiert wurden. ")

    st.subheader("KI-Training:")
    st.write("Ein eigenes KI-Modell zur Faserklassifizierung soll erstellt und trainiert werden? Die Funktion „KI-Training“ bietet genau diese Möglichkeiten. ")

    st.subheader("Datenvorbereitung:")
    st.write("Selbst erstellte Bilder sollen für das Trainieren eines KI-Modells vorbereitet werden? Die Funktion „Datenvorbereitung“ bietet unterschiedliche Optionen die Bilddaten zu bearbeiten.")

    st.subheader("Datenbank:")
    st.write("Eigene Bilddaten wurden erstellt und sollen nun sicher abgespeichert werden? Unsere Datenbank bietet hier Abhilfe und dient gleichzeitig zur Organisation der Daten.")

    st.subheader("Team:")
    st.write("Das **KI im Textil-Team** wünscht viel Freude bei der Verwendung vom FibreAI!")

    # Anzeige der Mitarbeiter Fotos
    A, B, C, D, E = st.columns(5)
    with A:
        st.image("webpictures/beer.png", width=image_width)
    with B:
        st.image("webpictures/hellweg.png", width=image_width)
    with C:
        st.image("webpictures/tabak.png", width=image_width)
    with D:
        st.image("webpictures/radau.png", width=image_width)
    with E:
        st.image("webpictures/brodka.png", width=image_width)

    # -------------------------------------------------------------------------------------------
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



if __name__ == "__main__":
    main()
