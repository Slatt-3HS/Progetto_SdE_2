import streamlit as st
import polars as pl
import altair as alt
import numpy as np

import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static

from scipy.stats import gaussian_kde

def analisi_spaziale(dati):
    # funzione per l'analisi spaziale/grafica
    # fatta su mappa

    st.header("Analisi geografica")

    tab1, tab2 = (
        st.tabs([
            "Distribuzione geografica delle morte",
            "Densità"
        ])
    )

    # pulizia dei dati per l'analisi geografica
    dati_geo = (
        dati.filter(
            pl.col("DeathCityGeo").str.contains(r"\(-?\d+\.\d+, -?\d+\.\d+\)")
        )
        .with_columns([
            pl.col("DeathCityGeo")
            .str.extract(r"\(([^,]+), ([^)]+)\)", 1)  # estraggo primo gruppo (latitudine)
            .cast(pl.Float64)
            .alias("Latitudine"),
            pl.col("DeathCityGeo")
            .str.extract(r"\(([^,]+), ([^)]+)\)", 2)  # estraggosecondo gruppo (longitudine)
            .cast(pl.Float64)
            .alias("Longitudine"),
        ])
    ).to_pandas() # devo convertire a pandas per compatibilità con scikit

    with tab1:

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



    with tab2:
        st.subheader("Densità della distribuzione geografica delle morti")

        m_dens =folium.Map(location=[41.6, -72.7], zoom_start=8)

        # dati per l aheatmap
        dati_dens = [[riga['Latitudine'], riga['Longitudine']] for _, riga in dati_geo.iterrows()]

        HeatMap(dati_dens).add_to(m_dens)


        # Stima della densità con il metodo del Kernel
        # https://docs.scipy.org/doc/scipy/tutorial/stats/kernel_density_estimation.html

        # stima
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

        # Creazione del grafico con Altair
        grafico_densità = alt.Chart(dati_densità).mark_circle().encode(
            x=alt.X('Longitudine:Q', scale=alt.Scale(domain=[x.min(), x.max()])),
            y=alt.Y('Latitudine:Q', scale=alt.Scale(domain=[y.min(), y.max()])),
            color=alt.Color('Densità:Q', scale=alt.Scale(scheme='plasma')),
            tooltip=['Longitudine', 'Latitudine', 'Densità']
        ).properties(
            width=500,
            height=500
        )

        # Visualizzazione affiancato dei grafici di densità
        col1, col2 = st.columns([1,1])
        with col1:
            folium_static(m_dens, width = 700, height = 400)
        with col2:
            st.altair_chart(grafico_densità, use_container_width=True)

    """
    st.subheader("Mortalità per contea")

    # aggregazione per contea
    dati_contea = (
        dati.group_by("DeathCounty")
        .agg([
            pl.count().alias("Morti totali"),
            pl.col("Age").mean().alias("Età media")
        ])
    )

    grafico_contea = (
        alt.Chart(dati_contea).mark_bar().encode(
            x=alt.X("DeathCounty:N", title="Contea", sort='-y'),
            y=alt.Y("Morti totali:Q", title="Numero di Morti"),
            tooltip=["DeathCounty", "Morti totali", "Età media"]
        ).properties(
            title="Morti per Contea",
            width=700,
            height=400
        )
    )

    etichette_contea = (
        alt.Chart(dati_contea).mark_text(
            align='center',
            baseline='bottom',
            dy=-5
        ).encode(
            x="DeathCounty:N",
            y="Morti totali:Q",
            text="Morti totali:Q"
        )
    )

    # grafico morte contea
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_contea + etichette_contea, use_container_width = False)
    st.dataframe(dati_contea)
    
    """



    st.subheader("Confronto per sesso")

    morti_contea_sesso = (
        dati.group_by(["Death County", "Sex"])
        .agg([
            pl.count().alias("Morti"),
            pl.col("Age").mean().alias("Età media")
        ])
        .sort("Morti", descending = True)
    )

    morti_contea = (
        dati.group_by("Death County")
        .agg([
            pl.count().alias("Morti totali")
        ])
        .sort("Morti totali", descending = True)
    )

    # per la visualizzazione (senza questa me la stampava trasposta)
    grafico_contea_sesso = (
        alt.Chart(morti_contea_sesso)
        .mark_bar()
        .encode(
            x=alt.X("Morti:Q", title="Numero di Morti"),
            y=alt.Y("Death County:N", title="Contea", sort='-x'),
            color=alt.Color("Sex:N", scale=alt.Scale(
                domain=["Male", "Female"], range=["#1f77b4", "#e377c2"]
                    )
            ),
            tooltip=["Death County", "Sex", "Morti", "Età media"]
        ).properties(
            title="Morti per Contea e Sesso",
            width=700,
            height=400
        )
    )

    etichette_contea = (
        alt.Chart(morti_contea).mark_text(
            align='left',
            baseline='middle',
            dx=5
        ).encode(
            y= alt.Y(
                "Death County:N",
                sort = "-x"
            ),
            x="Morti totali:Q",
            text="Morti totali:Q"
        )
    )

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_contea_sesso + etichette_contea, use_container_width = False)


