import streamlit as st

def intro_barra_lat():
    st.sidebar.markdown("# 📊 Analisi statistica")

    st.sidebar.markdown("### Esplora")

    # link per la navigazione nella pagina
    st.sidebar.markdown("""
        - [Introduzione](#introduzione)
        - [Analisi esplorativa](#analisi-esplorativa)
        - [Analisi geografica](#analisi-geografica)
        - [Analisi statistica](#analisi-statistica)
    """)