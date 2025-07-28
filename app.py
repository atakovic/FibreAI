import streamlit as st


pg = st.navigation([st.Page("pages/1_Startseite.py"),
                    st.Page("pages/2_Datenbank.py"),
                    st.Page("pages/3_Datenvorbereitung.py"),
                    st.Page("pages/4_KI-Training.py"),
                    st.Page("pages/5_KI-Faseranalyse.py"),
                    st.Page("pages/6_Kontakt.py")
                    ])
pg.run()
