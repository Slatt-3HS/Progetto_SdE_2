
import streamlit as st
import folium
from streamlit_folium import folium_static
import json


def intro_descrittiva():
    url_cdc = "https://nida.nih.gov/research-topics/trends-statistics/overdose-death-rates#Fig1"
    st.header("""Introduzione""")
    st.write("""
    ### Analisi delle morti legate all'assunzione di droga in Connecticut (USA) nel periodo 2012-2023.

    **Contesto**  
    Le morti relative all'assunzione di droga, negli Stati Uniti, rappresentano uno dei problemi più grandi riguardanti la salute pubblica.
    Il numero di decessi dovuti all'abuso di sostanze stupefacenti ha registrato un incremento costante negli ultimi decenni;
    secondo il CDC (Centers for Disease Control and Prevention), solo nel 2022 si sono verificate oltre 100.000 morti per problematiche insorte in seguito all'assunzione di droga, con un aumento significativo attribuibile agli oppioidi sintetici come il **fentanil** [[fonte](%s)].
    """ % url_cdc)

    # Creazione della mappa centrata sul Connecticut
    mappa = folium.Map(location = [41.6032, -73.0877], zoom_start = 8)

    # pagina github con le coordinate dei confini degli stati degli USA e le loro città
    # https://github.com/OpenDataDE/State-zip-code-GeoJSON
    # da qui ho scaricato il file con quelle del connecticut

    with open("ct_connecticut_zip_codes_geo.min.json", "r") as file:
        confini_ct = json.load(file)

    # aggiungo alla mappa il layer evidenziante lo stato del connecticut
    folium.GeoJson(
        confini_ct,
        name='Connecticut',
        style_function = lambda x: {
            'fillColor': 'red',
            'color': 'red',
            'weight': 0.1,
            'fillOpacity': 0.2
        }
    ).add_to(mappa)

    # impaginazione della mappa
    # con questi comandi la accentro
    col1, col_mappa, col3 = st.columns([1, 2, 1])
    with col_mappa:
        # visualizzazione della mappa
        folium_static(mappa, width =700, height = 400)

    st.write("""
    A livello statale, il **Connecticut** riflette questa tendenza preoccupante, di cui analizzeremo le morti relative a problemi insorti in seguito all'assunzione di droga nel periodo 2012-2023. 

    **Obiettivi dell'analisi**  
    Tra gli obiettivi della presente analisi ci sono:  
    - Identificare le **tendenze temporali** delle morti per overdose nel Connecticut.  
    - Esplorare la distribuzione geografica dei decessi per individuare le aree maggiormente colpite.  
    - Determinare le **sostanze più coinvolte** nei decessi (come oppioidi, cocaina e altri stupefacenti).  
    - Analizzare i dati demografici per riconoscere i gruppi di popolazione più vulnerabili (età, sesso, etnia).  

    **Importanza dello Studio**  
    
    Lo studio di questi dati riveste un'importanza cruciale sia dal punto di vista sociale che sanitario. La crisi delle overdose ha un impatto devastante sulle comunità, causando la perdita di vite umane e gravando sul sistema sanitario e sui servizi sociali. La conoscenza approfondita del fenomeno può:  
    - Fornire alle autorità sanitarie strumenti utili per monitorare e mitigare la crisi.  
    - Favorire la pianificazione di **programmi di prevenzione** e di **riduzione dei danni** che derivano dall'abuso di droghe.  
    - Supportare la creazione di campagne educative volte a sensibilizzare la popolazione sui rischi legati all'abuso di sostanze.  

    
    **Descrizione del dataset**
    
    Il dataset utilizzato per la presente analisi contiene dati relativi a 11.981 persone decedute a seguito di assunzione di droga in Connecticut, nel periodo 2012-2023.
    Esso proviene da [data.gov](https://catalog.data.gov/dataset/accidental-drug-related-deaths-2012-2018) e ogni caso include variabili relative a:
    - Data del decesso.
    - Età, sesso e etnia della vittima. 
    - Tipi di droghe implicate, rappresentate in variabili binarie (0 = non rilevata in corpo, 1 = altrimenti)
    - Coordinate geografiche del luogo di decesso
    
    **Preprocessing dei dati**
    
    Per rendere i dati completi, coerenti e pronti per l'analisi, è stato effettuato un preprocessing dei dati dove sono state eseguite le seguenti operazioni:
    - Conversione delle date in formato datetime e creazione di colonne aggiuntive per anno, mese, giorno e trimestre.
    - Gestione dei valori mancanti:
        - Età: sostituiti con la media (solo 2 NA)
        - Sesso e etnia: sostituiti con "Unknown"
        - Contea di morte: sostituiti con "Unknown"
    - Estrazione di latitudine e longitudine dalla colonna contenente le informazioni sul luogo di decesso.
    - Conversione dei valori di alcune variabili in formato intero per facilitare l'analisi
    - Riordino delle colonne per migliorare la leggibilità
    
    ---
    """)


