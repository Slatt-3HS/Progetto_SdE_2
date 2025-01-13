import streamlit as st

# configurazione delle impostazioni di default della pagina
# https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config

st.set_page_config(
    page_title = "Progetto SdE2_TIG_2077790",
    page_icon = "🔬",
    layout = "wide",
    initial_sidebar_state = "collapsed"
)

st.markdown('''
<style>
[data-testid="stSidebar"] {
    background-color: #f0f2f6;
}
.stMetric {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.stMarkdown h1 {
    color: #2c3e50;
    text-align: center;
}
.stMarkdown h2 {
    color: #34495e;
    border-bottom: 2px solid #bdc3c7;
    padding-bottom: 10px;
}
</style>
''', unsafe_allow_html=True)


from preprocessing import carica_dati, get_droghe
from intro_descrittiva import intro_descrittiva
from analisi_esplorativa import analisi_esplorativa
from analisi_stat import analisi_stat
from analisi_geografica import analisi_spaziale
from barra_laterale import intro_barra_lat


# main di collaudo delle funzioni
def main():

    intro_barra_lat()

    dati = carica_dati()
    colonne_droga = get_droghe()


    st.markdown('<div id="introduzione"></div>', unsafe_allow_html=True)
    intro_descrittiva()

    st.markdown('<div id="analisi-esplorativa"></div>', unsafe_allow_html=True)
    analisi_esplorativa(dati, colonne_droga)

    st.markdown('<div id="analisi-geografica"></div>', unsafe_allow_html=True)
    analisi_spaziale(dati)

    st.markdown('<div id="analisi-statistica"></div>', unsafe_allow_html=True)
    analisi_stat(dati, colonne_droga)


main()




