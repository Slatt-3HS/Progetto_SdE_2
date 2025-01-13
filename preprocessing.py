import polars as pl
import streamlit as st

# link dove trovare il dataset
# https://catalog.data.gov/dataset/accidental-drug-related-deaths-2012-2018

def get_droghe():
    """
    funzione fatta per estrarre le colonne relative alle droghe dal dataset (variabili binarie)
    """
    colonne_droga = [
        'Heroin', 'Heroin death certificate (DC)', 'Cocaine', 'Fentanyl', 'Fentanyl Analogue',
        'Oxycodone', 'Oxymorphone', 'Ethanol', 'Hydrocodone',
        'Benzodiazepine', 'Methadone', 'Meth/Amphetamine', 'Amphet', 'Tramad',
        'Hydromorphone', 'Morphine (Not Heroin)', 'Xylazine', 'Gabapentin',
        'Opiate NOS', 'Heroin/Morph/Codeine', 'Other Opioid', 'Any Opioid', 'Other'
    ]

    return colonne_droga


@st.cache_data
def carica_dati():
    """
    Fase di preprocessing:
    In questa funzione carico, pulisco e trasformo i dati per renderli lavorabili per le mie analisi
    """
    dati = pl.read_csv("drug_deaths.csv", ignore_errors = True) # carico i dati

    # conversione del formato della colonna Date e rimozione dei valori nulli
    dati = dati.with_columns(
        # creo una nuova colonna con le date in formato datetime
        pl.col("Date").str.strptime(pl.Datetime, format="%m/%d/%Y")
    )

    # fase di pulizia/riordino del dataset
    dati = (dati
            .with_columns([
                pl.col("Age").fill_null(strategy="mean"), # sostituisco gli NA in Age con la media generale (solo 3 valori mancanti, quindi non inficia sui risultati finali)
                # Rimpiazzo valori nulli in alcune colonne (utili alle successive analisi) con "unknown"
                pl.col("Sex").fill_null("Unknown"),
                pl.col("Race").fill_null("Unknown"),
                pl.col("Death County").fill_null("Unknown"),
                # Creazione di colonne separate per anno, mese e trimestre
                # utile per analisi di serie storiche
                pl.col("Date").dt.year().alias("Year").cast(pl.Int64),
                pl.col("Date").dt.month().alias("Month").cast(pl.Int64),
                pl.col("Date").dt.day().alias("Day").cast(pl.Int64),
                pl.col("Date").dt.quarter().alias("Quarter").cast(pl.Int64) # aggiungo anche il trimestre (= quarter in inglese)
            ])
    )

    # conversione dei valori delle colonne relative alle droghe in valori binari, questo per comodità nei successivi calcoli
    # (Y = 1, altrimenti = 0)
    colonne_droga = get_droghe()
    for droga in colonne_droga:
        dati =  dati.with_columns(
            pl.when(pl.col(droga) == "Y").then(1).otherwise(0).alias(droga)
        )

    # conversione di formato dei valori di alcune variaili
    dati = dati.with_columns([
                pl.col("Age").cast(pl.Int64),
                pl.col("Death County").cast(pl.Utf8),
                pl.col("Sex").cast(pl.Utf8)
    ])

    # estraggo la latitudine e la longitudine
    dati = dati.with_columns([
        pl.col("DeathCityGeo")
        .str.extract(r"\(([^,]+), ([^)]+)\)", 1)
        .cast(pl.Float64)
        .alias("Latitudine"),

        pl.col("DeathCityGeo")
        .str.extract(r"\(([^,]+), ([^)]+)\)", 2)
        .cast(pl.Float64)
        .alias("Longitudine")
    ])

    # dato che colonne, relative alla data, create prima vengono messe alla fine, le sposto all'inizio per una migliore visualizzazione
    # le sposto in posizione 3,4,5,6
    dati = dati.drop("Year").insert_column(3, dati.get_column("Year"))
    dati = dati.drop("Month").insert_column(4, dati.get_column("Month"))
    dati = dati.drop("Day").insert_column(5, dati.get_column("Day"))
    dati = dati.drop("Quarter").insert_column(6, dati.get_column("Quarter"))

    return dati


def main():
    """
    main di collaudo del preprocessing dei dati
    """

    dati = carica_dati()

    print("\nStruttura del dataset")
    print(dati.glimpse())

    print("\nStatistiche descrittive")
    print(dati.describe())

    print("\nPrime cinque righe")
    print(dati.head())
    print("\nUltime cinque righe")
    print(dati.tail())

    # distribuzione dei valori nulli nelle variabili (solo per quelle che ne hanno)
    for var in dati.columns:
        n_nulli = dati[var].is_null().sum()
        if n_nulli > 0:
            print(f"{var}: {n_nulli} valori nulli")

main()



