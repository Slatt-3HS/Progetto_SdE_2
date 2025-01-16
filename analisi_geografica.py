import streamlit as st
import polars as pl
import altair as alt
import numpy as np

import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static

from scipy.stats import gaussian_kde

from classe_Grafici import Grafici

def analisi_spaziale(dati):
    """
    funzione per l'analisi spaziale/geografica, fatta anche con mappe interattive
    """


    st.header("Analisi geografica")

    st.write("""
    
    La distribuzione geografica delle morti per overdose offre una prospettiva essenziale per comprendere le aree maggiormente colpite e identificare possibili fattori locali che contribuiscono al fenomeno.  
    Questa analisi esamina i dati suddivisi per contea e città, evidenziando le zone con il più alto numero di decessi. Attraverso visualizzazioni mirate, è possibile individuare tendenze regionali e confrontare il peso della crisi nelle diverse aree del Connecticut.

    L'obiettivo è identificare i punti caldi e correlare eventuali differenze geografiche con fattori demografici, economici o infrastrutturali, supportando così lo sviluppo di strategie mirate per la prevenzione e l'intervento.
    """)

    # pulizia dei dati per l'analisi geografica
    dati_geo = (
        dati.filter(
            pl.col("DeathCityGeo").str.contains(r"\(-?\d+\.\d+, -?\d+\.\d+\)")
        )
    ).to_pandas() # devo convertire a pandas per compatibilità con scikit


    st.subheader("Distribuzione geografica delle morti")

    # mappa interattiva, with clustering marker
    m = folium.Map(location = [41.6, -72.7], zoom_start =8)

    # Marker Cluster per una migliore visualizzazione
    # https://python-visualization.github.io/folium/latest/user_guide/plugins/marker_cluster.html
    marker_cluster = MarkerCluster().add_to(m)

    for indice, riga in dati_geo.iterrows(): # uso iterrows, fa parte di pandas
        folium.CircleMarker(
            location=[riga["Latitudine"], riga["Longitudine"]],
            radius = 5,
            popup=f"Age: {riga['Age']}, Sex: {riga['Sex']}, Race: {riga['Race']}",
            color="red",
            fill=True,
            fillColor="red"
        ).add_to(marker_cluster)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        folium_static(m, width=700, height=400)

    # ulteriori statistiche
    st.subheader("Statistiche distribuzione geografica")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Totale decessi:", len(dati_geo))
    with col2:
        st.metric("Luoghi di decesso:", dati_geo["Death City"].nunique()) # nunique() restituisco il numero di valori unici che ho


    st.subheader("Densità della distribuzione geografica delle morti")

    m_dens =folium.Map(location=[41.6, -72.7], zoom_start=8) # imposta los cheletro della mappa

    # dati per la heatmap
    dati_dens = [[riga['Latitudine'], riga['Longitudine']] for _, riga in dati_geo.iterrows()]

    HeatMap(dati_dens).add_to(m_dens) # aggiungo il layer della densità alla mappa


    # Stima della densità con il metodo del Kernel
    # https://docs.scipy.org/doc/scipy/tutorial/stats/kernel_density_estimation.html

    # stima delle densità
    x = dati_geo["Longitudine"]
    y = dati_geo["Latitudine"]

    xy = np.vstack([x,y])
    z = gaussian_kde(xy)(xy)

    # Creazione DataFrame
    dati_densità = pl.DataFrame({
        'Longitudine': x,
        'Latitudine': y,
        'Densità': z
    })

    # Creazione della densità
    grafico_densità = alt.Chart(dati_densità).mark_circle().encode(
        x=alt.X('Longitudine:Q', scale=alt.Scale(domain=[x.min(), x.max()])),
        y=alt.Y('Latitudine:Q', scale=alt.Scale(domain=[y.min(), y.max()])),
        color=alt.Color('Densità:Q', scale=alt.Scale(scheme='plasma')),
        tooltip=['Longitudine', 'Latitudine', 'Densità']
    ).properties(
        width=500,
        height=500
    )


    # Creazione delle tab per la visualizzazione dei grafici
    tab1, tab2 = st.tabs(["Mappa di Densità", "Grafico di Densità"])
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            folium_static(m_dens, width=700, height=400)
    with tab2:
        st.altair_chart(grafico_densità, use_container_width=True)

    # top 10 contee suddivisi per sesso
    morti_contea_sesso = (
        dati.group_by(["Death County", "Sex"])
        .agg([
            pl.count().alias("Morti totali")
        ])
        .sort("Morti totali", descending = True)
        .head(10)
    )

    # top 10 città suddivisi per sesso
    morti_citta_sesso = (
        dati.group_by(["Death City", "Sex"])
        .agg([
            pl.count().alias("Morti totali")
        ])
        .sort("Morti totali", descending = True)
        .head(10)
    )

    # Grafico della top 10 morti per contea suddivisi per sesso
    grafico_contea_sesso = Grafici.crea_grafico_barre(
        dat=morti_contea_sesso,
        y_col="Morti totali",
        x_col="Death County",
        color_col="Sex",
        title="Top 10 Morti per Contea e Sesso",
        label_angle=-90,
        show_legend=True,
        width=400
    )

    # Grafico della top 10 morti per città suddivisi per sesso
    grafico_citta_sesso = Grafici.crea_grafico_barre(
        dat=morti_citta_sesso,
        y_col="Morti totali",
        x_col="Death City",
        color_col="Sex",
        title="Top 10 Morti per Città e Sesso",
        label_angle=-90,
        show_legend=True,
        width=400
    )

    # Visualizzazione dei grafici affiancati con Streamlit
    col1, col2 = st.columns([1,1])
    with col1:
        st.altair_chart(grafico_contea_sesso, use_container_width=True)
    with col2:
        st.altair_chart(grafico_citta_sesso, use_container_width=True)

    st.write("""
    A livello di **città**, **Hartford** si distingue come la città con il maggior numero di decessi tra i maschi (817), seguita da **New Haven** (569) e **Waterbury** (552).  
    Tra le donne, **Hartford** registra il maggior numero di decessi (265), seguita da **New Haven** (196).  
    I numeri senza città specificata ("Unknown") rimangono alti per entrambi i sessi, in particolare tra gli uomini (2.065).

    Per quanto riguarda le **contee**, **Hartford** e **New Haven** dominano le statistiche maschili con rispettivamente 1.819 e 1.813 decessi.  
    Tra le donne, **Hartford** guida con 619 decessi, seguita da **New Haven** (592) e **Fairfield** (344).  
    Anche qui, i decessi non attribuiti a una contea specifica ("Unknown") sono rilevanti, in particolare tra gli uomini (2.886).

    In generale, emerge una chiara concentrazione di decessi nelle aree urbane più popolose, come Hartford e New Haven, sia a livello cittadino che di contea.  
    Questa distribuzione riflette probabilmente la maggiore densità di popolazione e l'accesso più ampio a sostanze letali in queste zone.  

    I decessi attribuiti a località sconosciute ("Unknown") meritano ulteriore indagine, poiché rappresentano una quota significativa del totale e potrebbero influenzare le priorità di intervento e prevenzione.
    """)

    # distribuzione delle morti per luogo
    morti_luogo = (
        dati
        .with_columns(
            pl.col("Location").str.to_lowercase().alias("Location")
        )
        .group_by("Location")
        .agg(pl.count().alias("Morti totali"))
        .sort("Morti totali", descending=True)  # ordine decrescente delle morti toali
    )

    grafico_morti_luogo = (
        Grafici.crea_grafico_barre(
            dat=morti_luogo,
            y_col="Morti totali",
            x_col="Location",
            color_col="Morti totali",
            horizontal=True,
            sort="-x",
            title="Morti per luogo di decesso"
        )
    )

    # grafico delle morti per luogo e per modo
    # accentramento grafico
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.altair_chart(grafico_morti_luogo, use_container_width=False)

    st.write(
        """
        L'analisi dei dati sui luoghi di decesso mostra che le abitazioni private (**residence**) rappresentano il luogo predominante, con **4.799 decessi totali**. Questo dato evidenzia come una parte significativa delle morti avvenga in contesti domestici, sottolineando l'importanza di monitorare le condizioni a rischio e le situazioni di emergenza all'interno delle case.

        I decessi in ospedale sono il secondo luogo più frequente, con **2.336 casi**, distribuiti in diverse categorie:
        - **Pronto soccorso/er e ambulatoriale**: 401 decessi.
        - **Ricovero ospedaliero**: 246 decessi.
        - **Morti all'arrivo in ospedale**: 81 decessi.
        Un numero significativo di decessi è attribuito ad altre località (**1.559**) e ad aree non specificate (**1.349**), evidenziando una necessità di migliorare la precisione nella categorizzazione del luogo di decesso.

        Le abitazioni del deceduto (**decedent's home**) riportano **776 casi**, a indicare una distinzione tra questa categoria e le abitazioni residenziali generiche. Altri luoghi riportano numeri significativamente inferiori, tra cui:
        - **Case di riposo e hospice**: 15 casi complessivi.
        - **Altri luoghi specifici (es. rifugi e strutture assistite)**: numeri isolati, con solo 1 o 2 decessi per luogo.

        """)

    # Selezione delle top 10 città con più morti
    top_citta_morti = (
        dati
        .group_by("Death City")
        .agg(pl.count().alias("Morti totali"))
        .sort("Morti totali", descending=True)
        .head(10)
        .select("Death City")
    )

    # Filtrare i dati per le top 10 città e calcolare le morti per anno
    morti_per_anno_top_citta = (
        dati
        .filter(pl.col("Death City").is_in(top_citta_morti["Death City"]))
        .group_by(["Year", "Death City"])
        .agg(pl.count().alias("Morti totali"))
        .sort(["Year", "Death City"])
    )

    # Creazione del grafico a linee per le top 10 città
    grafico_morti_per_anno_citta = Grafici.crea_grafico_linea(
        dat=morti_per_anno_top_citta,
        x_col="Year",
        y_col="Morti totali",
        color_col="Death City",
        title="Sviluppo delle Morti per Anno nelle Top 10 Città",
        width=800,
        height=400,
        show_legend=True
    )

    # Selezione delle top 10 contee con più morti
    top_contee_morti = (
        dati
        .group_by("Death County")
        .agg(pl.count().alias("Morti totali"))
        .sort("Morti totali", descending=True)
        .head(10)
        .select("Death County")
    )

    # iltrare i dati per le top 10 contee e calcolare le morti per anno
    morti_per_anno_top_contee = (
        dati
        .filter(pl.col("Death County").is_in(top_contee_morti["Death County"]))
        .group_by(["Year", "Death County"])
        .agg(pl.count().alias("Morti totali"))
        .sort(["Year", "Death County"])
    )

    # Creazione del grafico a linee per le top 10 contee
    grafico_morti_per_anno_contee = Grafici.crea_grafico_linea(
        dat=morti_per_anno_top_contee,
        x_col="Year",
        y_col="Morti totali",
        color_col="Death County",
        title="Sviluppo delle Morti per Anno nelle Top 10 Contee",
        width=800,
        height=400,
        show_legend=True
    )

    # Creazione della selezione con tendina per scegliere il grafico
    selezione_grafico = st.selectbox("Seleziona il grafico da visualizzare:", ["Top 10 Città", "Top 10 Contee"])

    if selezione_grafico == "Top 10 Città":
        st.altair_chart(grafico_morti_per_anno_citta, use_container_width=True)
    else:
        st.altair_chart(grafico_morti_per_anno_contee, use_container_width=True)

    st.write("""
    Nel corso degli anni analizzati, Hartford emerge chiaramente come la città con il maggior numero di morti totali, mostrando un incremento significativo dai 27 decessi del 2012 ai 188 del 2021. 
    Questo trend la pone in cima alla lista delle città più colpite, seguita da Waterbury, che registra un aumento marcato, arrivando a 125 morti nel 2019 e mantenendosi su valori simili nel 2020 con 124 decessi. 
    Anche altre città come Bridgeport, New Haven e Bristol contribuiscono in maniera rilevante al conteggio totale, pur mostrando incrementi meno drammatici rispetto a Hartford e Waterbury. 

    A livello di contea, Hartford e New Haven dominano i numeri di morti, con Hartford che raggiunge i 428 decessi nel 2021 e New Haven che tocca il picco di 516 nello stesso anno. Le contee meno popolate, come Litchfield e Windham, presentano numeri nettamente inferiori, suggerendo che il fenomeno sia particolarmente concentrato nelle aree urbane più densamente popolate. 
    Tuttavia, è importante notare la categoria "Unknown", che in alcuni anni mostra numeri molto elevati, come i 917 decessi non attribuiti a una contea specifica nel 2016, indicando possibili lacune nei sistemi di registrazione.

    Nel complesso, i dati mostrano un incremento marcato dei decessi dal 2012 al 2021, con picchi significativi nelle città e contee più grandi. 
    Questo suggerisce che fattori come densità di popolazione, accesso alle droghe e infrastrutture sanitarie abbiano un ruolo centrale nella distribuzione geografica dei decessi. 
    L'aumento più evidente si osserva a partire dal 2015, probabilmente in concomitanza con la crisi degli oppioidi, che potrebbe aver aumentato il problema. 
    La gravità della situazione a Hartford e New Haven indica la necessità di focalizzare gli interventi di prevenzione e trattamento su queste aree, mentre una maggiore attenzione ai decessi classificati come "Unknown" potrebbe migliorare la qualità dei dati e la comprensione del fenomeno.
    
    """)

