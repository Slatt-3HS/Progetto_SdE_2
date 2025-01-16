
import streamlit as st
import polars as pl
import pandas as pd

from classe_Grafici import Grafici


def analisi_esplorativa(dati, colonne_droga):
    """
    Analisi esplorativa del dataset. Completo di descrizione e grafici ad accompagnamento.
    """
    st.header("🔍 Analisi esplorativa del dataset")
    st.markdown("""
    Benvenuto nell'analisi esplorativa di questo dataset. L'obiettivo di questa analisi è fornire una panoramica dettagliata dei dati attraverso diverse prospettive, incluse:
    - 📊 **Statistiche descrittive:** Analisi di base per comprendere la distribuzione e le caratteristiche generali delle variabili.
    - 📈 **Visualizzazioni temporali e distribuzioni:** Rappresentazione grafica delle tendenze temporali e delle distribuzioni principali.
    - 🌍 **Analisi geografica:** Esplorazione della distribuzione geografica degli eventi registrati.
    - 💊 **Distribuzioni per tipo di droga, genere ed etnia:** Analisi comparative per comprendere l'incidenza delle variabili chiave nei diversi sottogruppi.
    - 🔗 **Correlazioni tra variabili numeriche:** Identificazione di relazioni e pattern tra le variabili numeriche presenti nel dataset.
    """)
    st.write("---")

    # selectbox per mostrare/nascondere il dataset
    st.header("Dataset")
    st.write("Di seguito è possibile visualizzare il dataset completo, pulito e messo in ordine, usato per l'analisi.")
    mostra_dataset = st.selectbox("Vuoi visualizzare il dataset completo?", ["No", "Sì"])
    if mostra_dataset == "Sì":
        st.dataframe(dati)
    else:
        st.warning("Dataset nascosto. Scegliere *Si* dalla tendina per visualizzarlo.")
    st.write("---")


    # capitolo sull'analisi univariata
    # in questo capitolo studio la distribuzione delle caratteristiche principali dei soggetti quali età etnia e sesso
    st.subheader("📌 Analisi Univariata delle principali caratteristiche dei soggetti")
    st.write("""
    L'analisi univariata si concentra sull'esplorazione di singole variabili riguardanti le principali caratteristiche relative ai singoli individui. 
    L'obiettivo è comprendere la distribuzione e la variabilità per variabili come età, sesso e etnia.
    """)



    # funzinone che userò di seguito per categorizzare le età
    def categorizza_età(età):
        if 19 >= età >= 0:
            return '19-'
        elif 25 >= età >= 20:
            return '20-25'
        elif 30 >= età >= 26:
            return '26-30'
        elif 35 >= età >= 31:
            return '31-35'
        elif 40 >= età >= 36:
            return '36-40'
        elif 45 >= età >= 41:
            return '41-45'
        elif 50 >= età >= 46:
            return '46-50'
        elif 55 >= età >= 51:
            return '51-55'
        elif 60 >= età >= 56:
            return '56-60'
        elif 65 >= età >= 61:
            return '61-65'
        else:
            return '65+'

    # faccio con pandas che ha la funzione apply che è più diretta
    cat_età = dati.get_column('Age').to_pandas().apply(categorizza_età)
    morti_cat_età = cat_età.value_counts().reset_index()
    morti_cat_età.columns = ['Categoria Età', 'Morti totali']

    morti_età = (
        dati
        .group_by("Age")
        .agg(pl.count()
             .alias("Morti totali")
             )
    )
    # non la stampo perché non mi da chissà quali che info
    # descriverò i risultati soltanto
    """
    grafico_cat_età = (
        Grafici.crea_grafico_barre(
            dat = morti_cat_età,
            x_col = "Categoria Età",
            y_col = "Morti totali",
            color_col="Morti totali",
            title = "Morti per Categorie di Età",
            sort = "-x"
        )
    )

    # accentramento grafico
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_cat_età, use_container_width=False)
    """
    

    # grafico delle morti per età
    grafico_morti_età = (
        Grafici.crea_grafico_barre(
            dat = morti_età,
            x_col = "Age",
            y_col = "Morti totali",
            color_col = "Morti totali",
            sort = "x",
            title = "Età al momento del decesso",
            width = 1450,
            height = 300,
            show_legend = False,
            label_angle = -70
        )
    )
    # stampa del grafico
    st.altair_chart(grafico_morti_età, use_container_width=False)

    # statistiche principali con metric
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Età minima", f"{dati['Age'].min()}")
    with col2:
        st.metric("Età media", f"{dati['Age'].mean():.2f}")
    with col3:
        st.metric("Età mediana", f"{dati['Age'].median():.2f}")
    with col4:
        st.metric("Deviazione standard età", f"{dati['Age'].std():.2f}")
    with col5:
        st.metric("Età massima", f"{dati['Age'].max()}")

    st.write("""
    I dati analizzati mostrano che le morti legate all’assunzione di droga si concentrano principalmente tra le fasce di età 36-40 anni, 51-55 anni e 31-35 anni, con un numero rispettivamente di 1538, 1524 e 1483 decessi. 
    Questi risultati evidenziano come le fasce di età lavorativa siano maggiormente colpite, mentre valori inferiori si riscontrano tra gli under 19 e gli over 65, con rispettivamente 84 e 419 decessi. 

    L’età minima registrata è di soli 13 anni, mentre l’età massima è di 87 anni. L’età media si attesta a 44,01 anni e la mediana a 44,00 anni, valori che confermano il forte coinvolgimento degli adulti di mezza età (oltre che la quasi-simmetria della dsitribuzione). 
    La deviazione standard di 12,68 anni indica una discreta variabilità, ma con una chiara concentrazione intorno alla fascia centrale visibile dal grafico.

    Si nota che i picchi si verificano tra i 39 e i 54 anni, con valori massimi di 333 decessi a 54 anni e oltre 300 decessi per età vicine. Le età estreme, come 15-19 anni o oltre 80, registrano invece numeri molto bassi, spesso inferiori a 10 decessi.

    La crisi delle overdose colpisce prevalentemente gli adulti di mezza età, in piena attività lavorativa, probabilmente a causa di fattori come stress, esposizione prolungata alle sostanze (per chi ha iniziato in giovane età) o vulnerabilità socio-economica.

    """)


    # Distribuzione per sesso
    morti_sesso = (
        dati
        .group_by("Sex")
        .agg(pl.count().alias("Morti totali"))
        .filter(pl.col("Sex").is_in(["Male", "Female"]))
    )

    # grafico a torta per la distribuzione del sesso
    torta_morti_sesso = (
        Grafici.create_grafico_torta(
            dat = morti_sesso,
            category_col = "Sex",
            value_col = "Morti totali",
            title = "Distribuzione genere",
            show_legend = False,
            width = 600
        )
    )
    col1, col2 = st.columns([1,1])
    with col1:
        st.altair_chart(torta_morti_sesso)
    with col2:
        st.write("""
        
        Il grafico a torta relativo alla distribuzione di genere dei morti evidenzia una netta prevalenza maschile, con 8887 decessi pari al 74,3% del totale. Le donne, invece, registrano 3082 decessi, corrispondenti al 25,7%. 
    
        La forte predominanza maschile tra i decessi può essere spiegata da una maggiore esposizione al rischio da parte degli uomini, sia in ambito lavorativo che sociale.
        E' importante non trascurare il dato relativo alle donne, che rappresentano comunque più di un quarto del totale. Questo suggerisce che, sebbene il fenomeno colpisca in modo più intenso gli uomini, anche le donne sono significativamente coinvolte.

        """)


    # DISTRIBUZIONE PER etnia
    morti_razza = (
        dati
        .filter(pl.col("Race") != "Unknown")
        .group_by("Race")
        .agg(pl.count().alias("Morti totali"))
        .sort("Morti totali", descending = True)
    )

    # grafico a barre della distribuzione delle etnie (detta Race in americano)
    grafico_razza = (
        Grafici.crea_grafico_barre(
            dat = morti_razza,
            x_col = "Race",
            y_col = "Morti totali",
            color_col = "Morti totali",
            title = "Morti per etnia",
            show_legend = False,
            horizontal =  True,
            sort = "-x",
            width = 600,
            height = 600
        )
    )

    # accentramento grafico
    col1, col2 = st.columns([1,1])
    with col1:
        st.altair_chart(grafico_razza)
    with col2:
        st.write("""
        L'analisi dei dati sulle morti per etnia evidenzia una netta predominanza di individui di etnia bianca, con un totale di 10.080 decessi, che rappresentano la stragrande maggioranza del campione analizzato. 
        Seguono a distanza significativa i decessi di individui neri o afroamericani, con 826 casi identificati come "Black or African American" e 809 categorizzati come "Black". 
        Questi due gruppi, sommati, indicano comunque un impatto rilevante tra le comunità nere, anche se decisamente inferiore rispetto a quello osservato nella popolazione bianca.  

        Le altre etnie, come gli asiatici e i nativi americani, presentano numeri decisamente più contenuti, con meno di 30 casi segnalati in molti casi. Per esempio, si registrano 26 decessi tra gli Indiani asiatici e 24 categorizzati come "Asian, Other". 
        Vi sono inoltre pochissimi casi isolati appartenenti ad altre etnie o descrizioni specifiche, sottolineando una distribuzione marginale rispetto ai due principali gruppi etnici.  

        Questo evidente squilibrio potrebbe riflettere fattori socio-economici, culturali o geografici. 
        Ad esempio, è possibile che le comunità bianche e nere siano più esposte ai rischi legati all'abuso di sostanze a causa di una maggiore accessibilità alle droghe illegali o una maggiore presenza in aree urbane ad alto rischio.

        Tuttavia, un elemento importante da considerare è che questo grande sbilanciamento nei dati potrebbe essere influenzato da un cattivo inserimento o categorizzazione delle informazioni. 
        La presenza di dati mancanti o la sovrapposizione di categorie etniche (come "Black" e "Black or African American") potrebbero aver distorto le proporzioni, enfatizzando alcune etnie a discapito di altre. 
        Un miglioramento nei sistemi di registrazione e analisi sarebbe essenziale per ottenere un quadro più accurato del fenomeno.
        """)

    st.write("---")



    # Analisi Temporale e Bivariata
    st.subheader("📆🔗 Analisi Bivariata e Temporale")

    # morti totali per anno
    totale_per_anno = (
        dati
        .group_by("Year")
        .agg(pl.count().alias("Totale_Anno"))
    )
    # morti totali annuali per sesso
    morti_annuali_sesso = (
        dati
        .filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Year", "Sex"])
        .agg(pl.count().alias("Morti"))
        .join(totale_per_anno, on="Year") # equivalente al metodo concat di panda
        .with_columns(
            (pl.col("Morti") / pl.col("Totale_Anno") * 100).round(2).alias("Percentuale")
        )
        .sort("Year")
    )

    # stampa morti annuali
    grafico_morti = Grafici.crea_grafico_linea(
        dat = morti_annuali_sesso,
        x_col="Year",
        y_col="Morti",
        color_col="Sex",
        totale = True,
        title="Numero di morti per anno",
        width = 700,
        label_angle = -60
    )

    # stampa del grafico sopra
    st.altair_chart(grafico_morti, use_container_width = True)


    # morti mensili per sesso
    morti_mese = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Month", "Sex"])
        .agg(pl.count().alias("Conteggio"))
    )

    # morti per giorno della settimaan
    morti_giorno = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["DayOfWeek", "Sex"])
        .agg(pl.count().alias("Conteggio"))
    )

    # grafico morti mensili
    grafico_mese = Grafici.crea_grafico_barre(
        morti_mese,
        x_col="Month",
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Mese",
        label_angle = -60,
        show_legend=False,
        width = 680
    )

    # morti per giorno della settimana
    grafico_giorno = Grafici.crea_grafico_barre(
        morti_giorno,
        x_col="DayOfWeek",
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Giorno della Settimana",
        label_angle = -60
    )

    # stampa affiancata dei due grafici
    col1, col2 = st.columns([1, 1])
    with col1:
        st.altair_chart(grafico_mese, use_container_width=False)
    with col2:
        st.altair_chart(grafico_giorno, use_container_width=False)


    st.write("""
        L'analisi temporale dei decessi ci permette di studiare l'andamento delle morti totali a livello annuale, mensile e settimanale. 
        Analizzando i dati per anno, si osserva un incremento progressivo delle morti dal 2012 (355 decessi) fino a raggiungere un picco massimo nel 2021 (1524 decessi), 
        seguito da una leggera riduzione negli anni successivi (1327 morti nel 2023). Questo andamento potrebbe riflettere fattori come l'aumento dell'accesso a sostanze pericolose.
        La distribuzione tra i generi mostra una prevalenza stabile delle morti maschili (intorno al 73-76%) rispetto a quelle femminili (23-27%), confermando un dato costante osservato anche in altre analisi.
        
        Sul piano mensile, emerge una distribuzione interessante, con picchi significativi nei mesi estivi e autunnali, 
        ad esempio Luglio (798 morti maschili) e Novembre (774 maschili), mentre per le donne si segnalano valori elevati in Luglio (272) e Novembre (275). 
        Questo potrebbe suggerire un legame con specifiche dinamiche stagionali o sociali. 
        
        Infine, l'analisi dei giorni della settimana evidenzia un alto numero di decessi maschili nel fine settimana, con Sabato (1408 morti) e Domenica (1397) al vertice. 
        Per le donne, i decessi sono più distribuiti, ma con valori più alti la Domenica (468) e il Sabato (457). Questi dati potrebbero indicare un'associazione tra le morti durante i fine settimana e comportamenti che aumentano l'esposizione ai rischi della droga.
    """)

    # morti per sesso e età
    morti_eta_sesso = (
        dati
        .select(["Sex", "Age"])  # Seleziona solo le colonne necessarie
        .filter(pl.col("Sex").is_in(["Male", "Female"]))  # Filtra per valori validi di sesso
    )

    # Creazione del boxplot della partizione sopra
    boxplot_eta_sesso = Grafici.crea_boxplot(
        dat=morti_eta_sesso,
        x_col="Sex",
        y_col="Age",
        title="Distribuzione delle età per sesso",
        width=400,
        height=400,
        show_legend = False
    )


    # Aggregazione dei dati per età media rispetto ad anno, mese e giorno della settimana
    morti_em_anno = (
        dati
        .group_by("Year")
        .agg([
            pl.col("Age").mean().alias("Totale"),
            pl.when(pl.col("Sex") == "Male").then(pl.col("Age")).mean().alias("Maschi"),
            pl.when(pl.col("Sex") == "Female").then(pl.col("Age")).mean().alias("Femmine")
        ])
        .melt(id_vars="Year", variable_name="Categoria", value_name="Età Media")
        .sort("Year")
    )

    morti_em_mese = (
        dati
        .group_by("Month")
        .agg([
            pl.col("Age").mean().alias("Totale"),
            pl.when(pl.col("Sex") == "Male").then(pl.col("Age")).mean().alias("Maschi"),
            pl.when(pl.col("Sex") == "Female").then(pl.col("Age")).mean().alias("Femmine")
        ])
        .melt(id_vars="Month", variable_name="Categoria", value_name="Età Media")
        .sort("Month")
    )

    morti_em_giorno = (
        dati
        .group_by("DayOfWeek")
        .agg([
            pl.col("Age").mean().alias("Totale"),
            pl.when(pl.col("Sex") == "Male").then(pl.col("Age")).mean().alias("Maschi"),
            pl.when(pl.col("Sex") == "Female").then(pl.col("Age")).mean().alias("Femmine")
        ])
        .melt(id_vars="DayOfWeek", variable_name="Categoria", value_name="Età Media")
        .sort("DayOfWeek")
    )


    # creazione dei grafici usando il metodo crea_grafico_linea
    grafico_em_anno = (
        Grafici.crea_grafico_linea(
            dat=morti_em_anno,
            x_col="Year",
            y_col="Età Media",
            color_col="Categoria",
            title="Sviluppo dell'età media per anno",
            width=800,
            height=400,
            show_legend=False
        )
    )

    grafico_em_mese = (
        Grafici.crea_grafico_linea(
            dat=morti_em_mese,
            x_col="Month",
            y_col="Età Media",
            color_col="Categoria",
            title="Sviluppo dell'età media per mese",
            width=800,
            height=400,
            show_legend=False
        )
    )

    grafico_em_giorno = (
        Grafici.crea_grafico_linea(
            dat=morti_em_giorno,
            x_col="DayOfWeek",
            y_col="Età Media",
            color_col="Categoria",
            title="Sviluppo dell'età media per giorno della settimana",
            width=800,
            height=400,
            show_legend=True
        )
    )



    # Visualizzazione
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.altair_chart(grafico_em_anno, use_container_width=True)
    with col2:
        st.altair_chart(grafico_em_mese, use_container_width=True)
    with col3:
        st.altair_chart(grafico_em_giorno, use_container_width=True)

    col1,col2 = st.columns([1, 2])
    with col1:
        st.altair_chart(boxplot_eta_sesso)
        with col2:
            st.write("""
                L'analisi dell'età media delle vittime nei diversi intervalli temporali fornisce spunti interessanti per comprendere l'evoluzione del fenomeno. 
                Partendo dalla distribuzione annuale, si osserva un chiaro aumento dell'età media nel tempo, passando da 40.77 anni nel 2012 a 47.99 anni nel 2023. 
                Questo trend potrebbe indicare che le overdose stanno colpendo fasce di popolazione più anziane negli anni recenti. 
                Anche la differenza di genere non si discosta mnolto fra i due sessi: le donne presentano spesso un'età media più alta rispetto agli uomini, con un massimo di 48.20 anni per le donne nel 2023, 
                rispetto a 47.90 anni per gli uomini nello stesso anno.

                Nel confronto mensile, i valori medi dell'età variano leggermente. Giugno registra l'età media più alta (44.81 anni) sia per il totale sia per le donne (45.76 anni), 
                mentre mesi come Settembre e Luglio hanno età medie più basse, rispettivamente 43.44 anni e 43.68 anni. Questi risultati potrebbero suggerire differenze stagionali nell'incidenza di decessi 
                nelle fasce di età più giovani o più anziane. 

                Considerando i giorni della settimana, Martedì e Giovedì mostrano le età medie più elevate (44.56 anni e 44.24 anni), 
                mentre Domenica e Sabato sono caratterizzati da età medie leggermente inferiori (43.61 anni e 43.85 anni). 
                Anche in questo caso, le donne tendono ad avere un'età media più alta rispetto agli uomini, in particolare nei giorni in cui i valori medi sono elevati, 
                come Martedì (45.07 anni per le donne). 

                Questi dati confermano l'evoluzione del fenomeno overdose verso una maggiore incidenza tra le persone di età avanzata, 
                evidenziando al contempo pattern stagionali e settimanali che potrebbero essere utili per indirizzare interventi preventivi più specifici. 
                """)


    # coinvolgimento per tipo di droga
    dati_morti_droga = (
        dati
        .select(["Year"] + colonne_droga)
        .group_by("Year")
        .agg([
            pl.sum(droga).alias(droga) for droga in colonne_droga
        ])
        .melt(id_vars=["Year"], variable_name="Droga", value_name="Morti") # equivale a un pivot della tabella
        .filter(pl.col("Morti") > 0)  # filtro per droghe con almeno un decesso
    )

    # Opzioni di visualizzazione
    opzioni_droga = ["Tutte le droghe"] + colonne_droga
    scelta_droga = st.selectbox("Seleziona una droga da visualizzare:", opzioni_droga)

    if scelta_droga == "Tutte le droghe":
        dati_visualizzati = dati_morti_droga.to_pandas()
        titolo = "Sviluppo temporale delle morti per tutte le droghe"
        color_col = "Droga"
    else:
        dati_visualizzati = dati_morti_droga.filter(pl.col("Droga") == scelta_droga).to_pandas()
        titolo = f"Sviluppo temporale delle morti per {scelta_droga}"
        color_col = scelta_droga  # Colore fisso per singola droga

    # creazione del grafico
    grafico_morti_droga = Grafici.crea_grafico_linea(
        dat=dati_visualizzati,
        x_col="Year",
        y_col="Morti",
        color_col="Droga" if scelta_droga == "Tutte le droghe" else color_col,
        title=titolo,
        width=900,
        height=500,
        label_angle=-45
    )

    # stampa deel grafico
    st.altair_chart(grafico_morti_droga, use_container_width =True)

    st.write("""
    L'analisi del coinvolgimento delle droghe nei decessi offre una prospettiva sui cambiamenti e le tendenze sul consumo/abuso di queste. 
    Una delle osservazioni più significative è l'incremento del coinvolgimento di **Fentanyl**, che ha raggiunto numeri impressionanti nel 2021 (1301 morti) e nel 2022 (1253 morti), 
    rispecchiando l'emergenza dell'epidemia da oppiacei. La presenza di droghe come **eroina** e **cocaina** si mantiene rilevante, con picchi rispettivamente nel 2016 (494 morti per eroina) 
    e nel 2023 (723 morti per cocaina), dimostrando che il problema delle droghe tradizionali non è diminuito nel tempo. 
    
    Altre sostanze come il **Metadone**, **Benzodiazepine** e **Etanolo** mostrano un andamento più stabile ma comunque significativo: ad esempio, le **Benzodiazepine** hanno raggiunto un massimo di 
    330 decessi nel 2017. Per quanto riguarda i decessi legati all'**Ossicodone**, i numeri sono più contenuti, con un massimo di 110 casi nel 2016. Tuttavia, la costante presenza di 
    questi farmaci indica che anche i farmaci prescritti possono contribuire ai decessi.
        
    Infine, emergono nuove sostanze come **Xylazine**, che ha visto una crescita significativa dal 2020 (140 morti) al 2022 (351 morti), sottolineando la comparsa di nuovi rischi 
    nel panorama delle droghe. Complessivamente, la categoria **'Any Opioid'** registra il numero più alto di decessi, con un picco nel 2021 (1413 morti), confermando l'importanza di 
    interventi focalizzati sugli oppiacei per affrontare la crisi delle droghe.
    """)

    # partizione causa di morte (conteggio)
    morti_cod = (
        dati
        .filter(pl.col("Cause of Death").is_not_null())  # filtra valori non nulli
        .group_by([pl.col("Cause of Death").str.to_lowercase(), "Sex"])
        .agg(pl.count().alias("Conteggio"))
        .sort("Conteggio", descending=True)
        .head(20)  # Considera solo le prime 20 cause di morte, perché tante si ripetono fra loro
    )

    # Creazione del grafico a barre con barre affiancate
    grafico_cod = Grafici.crea_grafico_barre(
        dat=morti_cod,
        x_col="Cause of Death",
        y_col="Conteggio",
        color_col="Sex",  # Colore per distinguere i sessi
        title="Top 20 Cause di morte per sesso",
        label_angle=-60,
        width=1000,
        horizontal=False,  # Imposta le barre in verticale
        sort="-y",
        show_legend=True  # Mostra la legenda per distinguere i sessi
    )

    st.altair_chart(grafico_cod, use_container_width = True)

    st.write("""
    L'analisi delle cause di morte evidenzia un ruolo predominante del Fentanyl e delle sue combinazioni con altre sostanze, sia tra gli uomini che tra le donne. 
    L'intossicazione acuta da Fentanyl rappresenta la causa principale, con 634 casi totali, di cui 553 riguardano uomini e 81 donne. 
    Questo dato sottolinea come il Fentanyl sia un elemento centrale della crisi degli oppioidi. 
   
    Le altre cause significative includono l'intossicazione acuta da cocaina, con 140 casi totali (107 maschili e 33 femminili), e la tossicità da più droghe (132 casi totali, 
    prevalentemente maschili con 90 casi). L'eroina, pur essendo meno rappresentata rispetto al Fentanyl, rimane rilevante con 115 decessi dovuti a intossicazione acuta e 105 
    attribuiti all'intossicazione semplice da eroina.

    Un aspetto critico è l'impatto delle combinazioni di droghe, come il Fentanyl e la cocaina (81 casi totali) o il Fentanyl e l'eroina (60 casi totali), che rappresentano un ulteriore 
    fattore di rischio, prevalentemente per gli uomini.
    
    Questi risultati confermano quanto già emerso: la crisi delle overdose è strettamente legata agli oppioidi sintetici e alle loro combinazioni, con una prevalenza di casi maschili. 

    
    L'assenza di alcune cause tra le donne potrebbe riflettere una cattiva inserzione dei dati all'interno del dataset. 

    """)


    """
    Distribuzione droghe per genere:
    devo prima effettuare un conteggio del coinvolgimento delle droghe, salvate in modo binario (1 = droga usata e 0 = altrimenti)
    """
    risultati = [] # lista vuota che conterrà i valori del conteggio della droga per maschi e femmina
    for droga in colonne_droga:
        maschi = (
            dati.filter(
                (pl.col(droga) == 1) & (pl.col("Sex") == "Male")
            ).height # height equivale al numero di righe della tabella creata ( = n_gruppo)
        )

        femmine = (
            dati.filter(
                (pl.col(droga) == 1) & (pl.col("Sex") == "Female")
            ).height
        )

        risultati.append({
            "Droga": droga,
            "Sesso": "Male",
            "Conteggio": maschi
        })

        risultati.append({
            "Droga": droga,
            "Sesso": "Female",
            "Conteggio": femmine
        })

    # trasformazione in dataframe plars
    morti_droga_genere = pl.DataFrame(risultati)

    # non mi andava bene il modo in cui venivano stampate i grafici a barre affiancati,
    # qundi opto per due grafici che riporteranno le info per ogni sesso

    # Creazione di due subset separati per maschi e femmine
    morti_maschi = morti_droga_genere.filter(pl.col("Sesso") == 'Male')
    morti_femmine = morti_droga_genere.filter(pl.col("Sesso") == 'Female')

    grafico_maschi = (
        Grafici.crea_grafico_barre(
            dat = morti_maschi,
            y_col = "Conteggio",
            x_col = "Droga",
            color_col = "Conteggio",
            horizontal = True,
            sort = "-x",
            title = "Maschi - Droghe più prevalenti",
            height = 600,
            width = 600,
            show_legend = False
        )
    )

    # grafico per le femmine
    grafico_femmine = (
        Grafici.crea_grafico_barre(
            dat = morti_femmine,
            y_col = "Conteggio",
            x_col = "Droga",
            color_col = "Conteggio",
            horizontal = True,
            sort = "-x",
            title = "Femmine - Droghe più prevalenti",
            height=600,
            width = 600,
            show_legend = False
        )
    )

    # Colonne affiancate
    col1, col2 = st.columns([1, 1])
    # Visualizzazione dei due grafici affiancati
    with col1:
        st.altair_chart(grafico_maschi)
    with col2:
        st.altair_chart(grafico_femmine)

    st.write("""
        I decessi maschili superano ampiamente quelli femminili in quasi tutte le categorie, con differenze marcate per Fentanyl, Cocaina ed Eroina.
        Il **Fentanyl** è la sostanza più coinvolta nei decessi per droga, con 6.203 casi tra i maschi e 1.834 tra le femmine. 
        Seguono la **Cocaina** (3.412 maschili e 1.160 femminili) e l'**Eroina** (2.787 maschili e 790 femminili).
    
        Gli oppioidi in generale rappresentano un contributo predominante, con 6.630 decessi tra i maschi e 2.188 tra le femmine. 
        Anche l'**Ethanol** (alcol) è rilevante, con 2.485 decessi maschili e 713 femminili. Le **Benzodiazepine** hanno una presenza significativa, con 1.724 decessi maschili e 989 femminili.
    
        Tra le altre sostanze spiccano **Xylazine** (807 maschili e 269 femminili), **Gabapentin** e **Tramadol**, pur avendo numeri inferiori. 
    
        Le femmine, tuttavia, mostrano una maggiore incidenza relativa nei casi legati a **Benzodiazepine** e **Gabapentin**, suggerendo differenze nei modelli di consumo. La crisi degli oppioidi rimane il fulcro del problema.
    """)


    """
        Distribuzione droghe per razza:
        devo prima effettuare un conteggio del coinvolgimento delle droghe, salvate in modo binario (1 = droga usata e 0 = altrimenti)
    """
    risultati = []  # lista vuota che conterrà i valori per razze
    for droga in colonne_droga:
        black = (
            dati.filter((pl.col(droga) == 1) & (pl.col("Race") == "Black")).height
        )

        white = (
            dati.filter((pl.col(droga) == 1) & (pl.col("Race") == "White")).height
        )

        # tutti i valori di race che non sono in Black o White
        altri = (
            dati.filter((pl.col(droga) == 1) & (~pl.col("Race").is_in(["Black", "White"]))).height
        )

        # Aggiunta dei risultati con valori coerenti
        risultati.append({"Droga": droga, "Race": "Black", "Conteggio": black})
        risultati.append({"Droga": droga, "Race": "White", "Conteggio": white})
        risultati.append({"Droga": droga, "Race": "Other", "Conteggio": altri})

    # Conversione in DataFrame polars
    morti_droga_genere = pl.DataFrame(risultati)

    @st.cache_data
    def genera_grafici(_morti_droga_genere):
        """
        funzione fatta salvare in cache i dati creati così da non dover fare ricaricare la pagiona a streamlit quando togglo l'etnia che voglio
        """
        # creazione di tre subset separati
        morti_black = morti_droga_genere.filter(pl.col("Race") == 'Black')
        morti_white = morti_droga_genere.filter(pl.col("Race") == 'White')
        morti_other = morti_droga_genere.filter(pl.col("Race") == 'Other')

        # Creazione dei grafici
        grafico_black = Grafici.crea_grafico_barre(morti_black, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort = "-y",show_legend = False, title="Black - Droghe più prevalenti",
                                                   width = 500, height = 400, label_angle = -90)

        grafico_white = Grafici.crea_grafico_barre(morti_white, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort="-y", title="White - Droghe più prevalenti",show_legend = False,
                                                   width = 500, height = 400, label_angle = -90)

        grafico_other = Grafici.crea_grafico_barre(morti_other, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort="-y", title="Other - Droghe più prevalenti", show_legend = False,
                                                   width = 500, height = 400, label_angle = -90)

        # Restituzione di un dizionario di grafici già pronti, a cui dovro accederci dopo
        return {
            "Black": grafico_black,
            "White": grafico_white,
            "Other": grafico_other
        }

    # Generazione e salvataggio dei grafici in un avariabile
    grafici = genera_grafici(morti_droga_genere)

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.altair_chart(grafici["White"])
    with col2:
        st.altair_chart(grafici["Black"])
    with col3:
        st.altair_chart(grafici["Other"])

    st.write("""
    Le morti per droga evidenziano differenze significative tra le etnie. La popolazione **White** registra il numero più alto in quasi tutte le categorie, con **Fentanyl** (6.653) come principale causa, seguita da **Cocaine** (3.535) ed **Heroin** (3.196). 
    Anche le morti associate agli **oppioidi** complessivi (categoria "Any Opioid", 7.362) sono elevate, ma questa categoria è molto generica, dato che molto probabilmente include sostanze già conteggiate come **Fentanyl**, un oppioide stesso e principale responsabile.

    Per la popolazione **Black**, i numeri sono inferiori ma notevoli. Le principali cause di morte sono legate a **Fentanyl** (488) e **Cocaine** (421), con un minore impatto di **Heroin** (262). 
    Anche qui, la categoria "Any Opioid" (521) è meno informativa poiché sovrapposta a dati più specifici.

    La categoria **Other** (cioè tutte le etnie al di fuori di White e Black) presenta un trend intermedio, con **Fentanyl** (906), **Cocaine** (622) ed **Ethanol** (313) come principali sostanze coinvolte. 
    Gli oppioidi complessivi (945) includono sostanze già analizzate, come il **Fentanyl**, che risulta il maggior contributore.

    In sintesi, il **Fentanyl** emerge chiaramente come la maggiore causa di mortalità in tutte le etnie ed è già incluso nella categoria generica "Any Opioid". 
    Pertanto, questa etichetta, sebbene utile per un quadro d'insieme, fornisce meno valore rispetto all'analisi delle singole sostanze. 

    """)


    ### STAMPA DEI LUOGHI DI DECESSO
    risultati_location = []  # lista vuota per salvare i risultati

    dati = dati.with_columns(
        pl.col("Location").str.to_lowercase().alias("Location_low")     #  per rendere il filtro case-insensitive
    )

    # Loop per calcolare i conteggi in base alle categorie di Location
    for droga in colonne_droga:
        home = dati.filter(
            (pl.col(droga) == 1) & (pl.col("Location_low").str.contains("home|residence"))
        ).height

        hospital = dati.filter(
            (pl.col(droga) == 1) & (pl.col("Location_low").str.contains("hospital|hiospital|nursing|shelter"))
        ).height

        # tutto cio che non è hospitola o home
        other = dati.filter(
            (pl.col(droga) == 1) &
            (~pl.col("Location_low").str.contains("home|residence|hospital|hiospital|nursing|shelter"))
        ).height

        # Aggiunta dei risultati alla lista
        risultati_location.append({"Droga": droga, "Location": "Home", "Conteggio": home})
        risultati_location.append({"Droga": droga, "Location": "Hospital", "Conteggio": hospital})
        risultati_location.append({"Droga": droga, "Location": "Other", "Conteggio": other})

    # Conversione in DataFrame Polars
    morti_droga_location = pl.DataFrame(risultati_location)

    # Funzione con cache per velocizzare il cambio di categoria
    @st.cache_data
    def genera_grafici_location(_dat):
        home = _dat.filter(pl.col("Location") == 'Home')
        hospital = _dat.filter(pl.col("Location") == 'Hospital')
        other = _dat.filter(pl.col("Location") == 'Other')

        # Creazione dei grafici con la classe Grafici
        grafico_home = Grafici.crea_grafico_barre(home, "Droga", "Conteggio",
                                                  color_col="Conteggio", horizontal=True,
                                                  sort="-x", title="Home - Droghe più prevalenti",
                                                  width = 700, height =400, show_legend = False)

        grafico_hospital = Grafici.crea_grafico_barre(hospital, "Droga", "Conteggio",
                                                      color_col="Conteggio", horizontal=True,
                                                      sort="-x", title="Hospital - Droghe più prevalenti",
                                                      width = 700, height =400, show_legend = False)

        grafico_other = Grafici.crea_grafico_barre(other, "Droga", "Conteggio",
                                                   color_col="Conteggio", horizontal=True,
                                                   sort="-x", title="Other - Droghe più prevalenti",
                                                   width=500, height=400, show_legend = False)

        return {
            "Home": grafico_home,
            "Hospital": grafico_hospital,
            "Other": grafico_other
        }

    # Generazione e caching dei grafici
    grafici_location = genera_grafici_location(morti_droga_location)


    # # Menu a tendina per la selezione del grafico
    # st.write("### Seleziona la categoria di Location per visualizzare il grafico:")
    # scelta_location = st.selectbox(
    #     "Scegli una categoria di Location:",
    #     options=["Home", "Hospital", "Other"]
    # )

    # Visualizzazione dei grafici
    col1, col2 = st.columns([1,1])
    with col1:
        st.altair_chart(grafici_location["Home"])
    with col2:
        st.altair_chart(grafici_location["Hospital"])


    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.altair_chart(grafici_location["Other"])

    st.write("""
    Le morti per luogo di decesso mostrano un chiaro predominio di **Fentanyl** come sostanza più letale in tutti i luoghi di decesso, confermando il suo ruolo centrale nella crisi degli oppioidi.

    **A casa**, il numero più elevato di decessi è attribuibile al **Fentanyl** (3.646), seguito da **Cocaine** (1.780) ed **Ethanol** (1.439).  
    Gli oppioidi nel complesso (categoria generica "Any Opioid") raggiungono 4.082 decessi.

    **In ospedale**, il trend generale si ripete: il **Fentanyl** registra 1.855 decessi, seguito da **Cocaine** (1.116) ed **Heroin** (1.057).  
    Anche in questa luogo, la categoria "Any Opioid" (2.054) include gran parte delle morti già attribuite a oppioidi specifici.

    Per quanto riguarda le morti classificate come **Other** (luoghi diversi da casa o ospedale), il **Fentanyl** continua a dominare con 1.419 casi, mentre **Cocaine** (956) ed **Ethanol** (628) seguono.

    In sintesi, la distribuzione per luogo evidenzia una maggiore incidenza di morti per **Fentanyl** in ambito domestico, rispetto a ospedali o altre location.  
    Questo suggerisce l'elevato consumo privato e la conseguente difficoltà di intervento medico immediato.  
 
    L'analisi della categoria "Any Opioid" deve essere interpretata con cautela poiché, come detto prima, molto probabilmente comprende sostanze come il **Fentanyl** (un oppioide), già chiaramente identificate come principali responsabili.
    """)



    #### CORRELAZIONI TRA VARIABILI NUMERICHE

    # funzione per tirare fuori le variabili di tipo numerico dal dataset
    def var_numeriche(dati):
        numeriche = []
        for col in dati.columns:
            if dati[col].dtype in [pl.Float64, pl.Int64, pl.Int32]:
                numeriche.append(col)
        return numeriche

    st.subheader("🔗 Correlazioni tra Variabili")

    numeriche = var_numeriche(dati)
    dati_numerici = (
        dati
        .select(numeriche)
        .drop(["Quarter", "Other","Month_num","Day_num", "Latitudine", "Longitudine"]) # non mi interessa calcolarle per queste variabili
        .to_pandas() # mi serve per buttare la tabella creata alla funzione corr che userò in seguito
    )


    correlazioni = dati_numerici.corr(method="pearson")

    st.write("""
    Una matrice di correlazione è uno strumento fondamentale per analizzare le relazioni tra variabili numeriche in un dataset. 
    Questa analisi permette di identificare legami positivi o negativi tra le variabili e di valutare la loro intensità attraverso un coefficiente che varia tra -1 e 1. 
    Valori vicini a 1 indicano una forte correlazione positiva (quando una variabile aumenta, l'altra tende ad aumentare), mentre valori vicini a -1 rappresentano una forte correlazione negativa 
    (quando una variabile aumenta, l'altra tende a diminuire). Valori prossimi a 0 indicano una relazione debole o assente.
    
    Nel contesto del presente studi, una matrice di correlazione può aiutare a comprendere come fattori demografici, temporali e relativi alle sostanze siano interconnessi. 
    Ad esempio, possiamo analizzare se l'anno è correlato all'aumento di determinate sostanze come Fentanyl o se l'età è un fattore che influenza l'incidenza di specifiche droghe. 
    Queste informazioni possono fornire spunti preziosi per interpretare i dati, individuare tendenze e supportare lo sviluppo di interventi mirati.
    """)

    st.write("Matrice di correlazione tra variabili numeriche:")

    mostra_corr = st.selectbox("Vuoi visualizzare la matrice di correlazione?", ["No", "Sì"])
    if mostra_corr == "No":
        st.warning("Matrice di correlazione nascosta. Scegliere *Si* dalla tendina per visualizzarla.")
    else:
        st.dataframe(correlazioni.style.background_gradient(cmap='coolwarm_r'))

    st.write("""
    **Analisi della matrice di correlazioni**
    
    La matrice delle correlazioni (di Pearson) analizzata evidenzia diverse relazioni interessanti tra variabili, con valori arrotondati alla seconda cifra decimale. 
    Emerge una correlazione significativa e positiva tra l'anno e la presenza di Fentanyl (0.51) e di oppioidi in generale (0.55), che conferma quanto osservato nei dati temporali: 
    l'aumento di queste sostanze, soprattutto Fentanyl, è un fenomeno recente e in crescita. Inoltre, una correlazione moderata è presente tra l'anno e Fentanyl Analogue (0.09), 
    indicando una diffusione recente anche di queste varianti. 
     
    Per quanto riguarda la variabile età, la correlazione con le droghe è generalmente bassa, ma si osservano valori leggermente positivi con Gabapentin (0.09) e Hydromorphone (0.03), 
    indicando una maggiore presenza di queste sostanze nei decessi di individui più anziani. D'altro canto, l'età è debolmente negativa con Eroina (-0.08) e Fentanyl (-0.06), 
    suggerendo che queste sostanze colpiscono principalmente le fasce di età più giovani e produttive, come già discusso.
    
    Anche le relazioni tra le sostanze offrono spunti interessanti: Fentanyl e Fentanyl Analogue mostrano una correlazione positiva (0.20), 
    indicando che spesso queste due sostanze sono presenti insieme. Analogamente, oppioidi generici ('Any Opioid') mostrano una forte correlazione con Fentanyl (0.53), 
    rafforzando l'idea che Fentanyl sia al centro della crisi attuale degli oppioidi.
    
    Un dato critico emerge dalla correlazione negativa tra Eroina e anno (-0.39): l'uso di eroina sembra diminuire nel tempo, 
    forse soppiantata da Fentanyl e altre sostanze sintetiche. Questo cambiamento potrebbe riflettere cambiamenti nelle preferenze dei consumatori o nella disponibilità delle droghe.
    
    Infine, la correlazione tra Xylazine e anno (0.30) conferma che questa sostanza è un fenomeno più recente, come evidenziato dai picchi nei dati annuali. 
    In sintesi, la matrice di correlazione sottolinea dinamiche già osservate nelle analisi temporali e demografiche.
    
    """)


    # CONCLUSIONE
    st.subheader("✅Conclusioni")
    st.markdown("""
    L'analisi delle morti correlate all'assunzione di droga in Connecticut tra il 2012 e il 2023 ha evidenziato tendenze preoccupanti e spunti cruciali per interventi futuri. 
    
    Le morti per overdose sono aumentate costantemente, raggiungendo un picco nel 2021. 
    Questo incremento è fortemente legato alla diffusione del Fentanyl e di altri oppioidi sintetici, che si confermano come principali responsabili della crisi.
    Al contempo, droghe più tradizionali come eroina e cocaina mantengono una rilevanza significativa, pur mostrando variazioni temporali nel loro impatto.
    
    Dal punto di vista demografico, gli adulti di mezza età, soprattutto tra i 36 e i 55 anni, risultano essere il gruppo più colpito, con un'età media delle vittime di circa 44 anni. 
    La distribuzione per sesso evidenzia una netta prevalenza maschile, con gli uomini che rappresentano oltre il 70% dei decessi. 
    Anche l'analisi per etnia mostra disparità marcate, con la popolazione bianca che registra il maggior numero di morti, seguita dalle comunità nere e da altre minoranze.
    
    Le correlazioni tra variabili hanno sottolineato l'incremento recente del Fentanyl, con una forte associazione temporale rispetto agli anni analizzati. 
    Inoltre, le analisi geografiche e sui luoghi di morte rivelano una prevalenza di decessi in contesti domestici, suggerendo un consumo privato che spesso impedisce interventi tempestivi.
    
    Questi risultati mettono in luce la necessità di interventi mirati per contrastare la crisi. 
    Politiche di prevenzione, programmi di educazione e strategie di riduzione del danno dovrebbero essere adattati alle specificità demografiche e geografiche emerse, con un focus particolare sul controllo degli oppioidi sintetici e sul supporto alle fasce di popolazione più vulnerabili.
     """)
