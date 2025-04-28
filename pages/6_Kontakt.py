import streamlit as st
from PIL import Image
import base64
from io import BytesIO

#---------------------------------------------------------
# Page Setup
st.set_page_config(
    layout="wide",
    page_title = "KI Textil",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmdeZTjsQSvu3Fbl1_4xuf2FfdVLSsEHHnlXaFi6uY-Q&s",
)
#--------------------------
image_width = 100
st.title("Kontakt")
st.write("Falls es Komplikationen gibt oder es zu Rückfragen kommen sollte, könnt ihr uns gerne kontaktieren. \n **Technische Fragen** bitte an **Alen Tabakovic** richten. \n\n Fragen zur **Lehrveranstaltung** gerne an **Prof. Mathias Beer** oder an **Lennart Hellweg**.")

kontakt2, kontakt3 = st.columns(2)
with kontakt2:
    st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/beer.png", width=image_width)
    st.write("**Prof. Mathias Beer**")
    st.write("Professor der Lehrveranstaltung")
    st.write("Email: mathias.beer@hs-niederrhein.de")
    st.write("Raum: D205")
    st.write("Webschulstraße 8")
    st.write("41065 Mönchengladbach")
with kontakt3:
    st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/hellweg.png", width=image_width)
    st.write("**Lennart Hellweg**")
    st.write("Dozent der Lehrveranstaltung")
    st.write("Email: lennart.hellweg@hs-niederrhein.de")
    st.write("Raum: E205")
    st.write("Webschulstraße 20")
    st.write("41065 Mönchengladbach")

kontakt1, kontakt4, kontakt5 = st.columns(3)
with kontakt1:
    st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/tabak.png", width=image_width)
    st.write("**Alen Tabakovic**")
    st.write("Technischer Support")
    st.write("Email: alen.tabakovic@stud.hn.de")
with kontakt4:
    st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/radau.png", width=image_width)
    st.write("**Natalie Radau**")
    st.write("Projekt Support")
    st.write("Email: natalie.radau@stud.hn.de")
with kontakt5:
    st.image("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/brodka.png", width=image_width)
    st.write("**Lisa-Marie Brodka**")
    st.write("Projekt Support")
    st.write("Email: lisa-marie.brodka@stud.hn.de")

#-------------------------------------------------------------------------------------------
### Seitenleiste
# Öffne das Bild
image = Image.open("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png")

# Konvertiere das Bild in Base64
buffer = BytesIO()
image.save(buffer, format="PNG")
buffer.seek(0)
data = base64.b64encode(buffer.read()).decode("utf-8")

# Benutzerdefiniertes HTML mit Base64-Bild
#st.sidebar.header("FibreAI")
image = Image.open("/opt/lampp/htdocs/Webseite_SHK/streamlit/webpictures/fibreai.png")
st.sidebar.image(image)

