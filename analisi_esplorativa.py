
import streamlit as st
import polars as pl
import altair as alt

from classe_Grafici import Grafici



def analisi_esplorativa(dati, colonne_droga):
    """
    Analisi esplorativa con studio univariato e bivariato delle variabili; include distribuzioni, correlazioni e statistiche principali.
    """

    st.write(
        """Di seguito viene riportato il dataset completo, pulito e messo in ordine, usato per l'analisi."""
    )
    st.dataframe(dati)
    st.write("---")

    # mossa inutile, ma lo faccio lo stesso
    grafici = Grafici()


    st.header("🔍 Analisi esplorativa del dataset")

    st.markdown("""
    In questo capitolo esploreremo il dataset...
    """)

    totale_per_anno = (
        dati
        .group_by("Year")
        .agg(pl.count().alias("Totale_Anno"))
    )

    morti_annuali_sesso = (
        dati
        .filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Year", "Sex"])
        .agg(pl.count().alias("Morti"))
        .join(totale_per_anno, on="Year")
        .with_columns(
            (pl.col("Morti") / pl.col("Totale_Anno") * 100).round(2).alias("Percentuale")
        )
        .sort("Year")
    )

    # Distribuzione per sesso
    morti_sesso = (
        dati
        .group_by("Sex")
        .agg(pl.count()
             .alias("Morti totali")
             )
        .filter(pl.col("Sex").is_in(["Male", "Female"]))
    )


    # Plot morti annuali
    grafico_morti = grafici.crea_grafico_linea(
        dat = morti_annuali_sesso,
        x_col="Year",
        y_col="Morti",
        color_col="Sex",
        totale = True,
        title="Numero di morti per anno",
        width = 700,
        label_angle = -60
    )


    torta_morti_sesso = (
        grafici.create_grafico_torta(
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
        st.altair_chart(grafico_morti)
    with col2:
        st.altair_chart(torta_morti_sesso)


    morti_mese = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Month", "Sex"])
        .agg(pl.count().alias("Conteggio"))
    )

    morti_giorno = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["DayOfWeek", "Sex"])
        .agg(pl.count().alias("Conteggio"))
    )

    grafico_mese = grafici.crea_grafico_barre(
        morti_mese,
        x_col="Month",
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Mese",
        label_angle = -60,
        show_legend=False,
        width = 680
    )

    grafico_giorno = grafici.crea_grafico_barre(
        morti_giorno,
        x_col="DayOfWeek",
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Giorno della Settimana",
        label_angle = -60
    )



    st.write("### Morti per giorno della settimana")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.altair_chart(grafico_mese, use_container_width=False)
    with col2:
        st.altair_chart(grafico_giorno, use_container_width=False)



    st.write("""
    Nel corso degli anni viene osservato un aumento progressivo delle morti, con un incremento significativo a partire dal 2015 e che culmina nel 2017 dove vengono registrati più di mille decessi.
    Quelli maschili risultano costantemente più elevati rispetto a quelli femminili, con un rapporto che tende a rimanere stabile nel tempo.
    
    La distribuzione rivela una costanza nei decessi durante l'anno, con una leggera tendenza all'aumento nei mesi estivi e invernali.
    Per gli uomini, i mesi con il più alto numero di decessi sono ottobre novembre, mentre per le donne l'incremento risulta uniforme, anche se con leggeri picchi nei mesi di dicembre e gennaio.
    Questa distribuzione potrebbe essere legata a fattori stagionali.
    
    L'analisi trimestrale conferma le tendenze scaturite prima, mostrando un incremento gruaduale (leggero) nel corso dellì'anno, con il quarto trimestre come periodo di maggiore incidenza per entrambi i generi.
    
    """)


    # morti per causa
    morti_cod = (
        dati.group_by(pl.col("Cause of Death").str.to_lowercase())
        .agg(pl.count().alias("Conteggio"))
        .sort("Conteggio", descending = True)
        .head(10)
    )

    grafico_cod = (
        grafici.crea_grafico_barre(
            dat = morti_cod,
            y_col = "Conteggio",
            x_col = "Cause of Death",
            horizontal = True,
            sort = "-x",
            color_col = "Conteggio",
            title = "Top 10 cause di decesso",
            width=800
        )
    )

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_cod, use_container_width = False)

    st.write("""
    Le principali cause di morte riportano una elevata prevalenza di intossicazioni acute da oppioide e cocaine.
    *Fentanyl* e *Eroina* sono i principali responsabili presentandosi con numeri elevati . Dalla dicitura *multiple drug toxicity* viene evevidenziata una tendenza significativa al consumo di più droghe insieme.
    L'eroina compare ripetutamente sotto diversi nomi (*acute intoxication, toxicity*). La cocaina è presente con frequenza inferiore rispetto al *fentanyl* e la *eroina*.
    """)


    # DISTRIBUZIONE PER CATEGORIE DI ETÀ
    def categorizza_età(età):
        if 20 >= età >= 0:
            return '21-'
        elif 30 >= età >= 21:
            return '21-30'
        elif 40 >= età >= 31:
            return '31-40'
        elif 50 >= età >= 41:
            return '41-50'
        elif 60 >= età >= 51:
            return '51-60'
        else:
            return '60+'

    # faccio con pandas che ha la funzione apply che è più diretta
    cat_età = dati.get_column('Age').to_pandas().apply(categorizza_età)
    morti_cat_età = cat_età.value_counts().reset_index()
    morti_cat_età.columns = ['Categoria Età', 'Morti totali']

    grafico_cat_età = (
        grafici.crea_grafico_barre(
            dat = morti_cat_età,
            x_col = "Categoria Età",
            y_col = "Morti totali",
            color_col="Morti totali",
            title = "Morti per Categorie di Età",
            horizontal = True
        )
    )

    # accentramento grafico
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_cat_età, use_container_width=False)

    morti_età = (
        dati
        .group_by("Age")
        .agg(pl.count()
             .alias("Morti totali")
             )
    )

    grafico_morti_età = (
        grafici.crea_grafico_barre(
            dat = morti_età,
            x_col = "Age",
            y_col = "Morti totali",
            color_col = "Morti totali",
            sort = "x",
            title = "Età al momento del decesso",
            width = 800,
            height = 600
        )
    )

    #col1, col2, col3 = st.columns([1,2,1])
    #with col2:
    st.altair_chart(grafico_morti_età, use_container_width=True)

    # statistiche principali
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Età minima", f"{dati['Age'].min()}")
    with col2:
        st.metric("Età media", f"{dati['Age'].mean():.2f}")
    with col3:
        st.metric("Deviazione standard età", f"{dati['Age'].std():.2f}")
    with col4:
        st.metric("Età massima", f"{dati['Age'].max()}")

    st.write(
        """
        Dal grafico sopra riportato vengono mostrati i dati relativi alle morti categorizzate per gruppi di età.
        Questi mostrano che la fascia più colpita è quella fra i 41 e i 50 anni, con 1266 decessi, seguita dalla fascia 31-40 con 1249 morti.
        Seguono poi, con numeri leggeremnte più bassi, le categorie 51-60 e 21-30 (1138 e 1046 morti rispettivamente).
        La mortalità cala in modo significativo nelle tà più avanzate, con 313 decessi nella fascia degli ultrasessantenni e raggiunge il valore più basso con 91 morti registrate nei 21- anni.
        """
    )

    # distribuzione delle morti per luogo
    morti_luogo = (
        dati
        .with_columns(
            pl.col("Location").str.to_lowercase().alias("Location")
        )
        .group_by("Location")
        .agg(pl.count().alias("Morti totali"))
        .sort("Morti totali", descending = True) # ordine decrescente delle morti toali
    )
    st.write(morti_luogo)

    grafico_morti_luogo = (
        grafici.crea_grafico_barre(
            dat = morti_luogo,
            y_col = "Morti totali",
            x_col = "Location",
            color_col = "Morti totali",
            horizontal = True,
            sort = "-x",
            title = "Morti per luogo di decesso"
        )
    )


    # grafico delle morti per luogo e per modo
    # accentramento grafico
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_morti_luogo, use_container_width = False)

    st.write(
        """
        L'abuso di sostanze risulta essere la causa più frequente di decesso, seguita dall'uso generico di droghe e dall'ingestione. 
        Tuttavia, è importante sottolineare una possibile sovrapposizione tra categorie come *substance abuse* e *drug abuse*, che sembrano descrivere lo stesso fenomeno con termini diversi.
        
        Per quanto riguarda i luoghi di decesso più comuni, la maggior parte delle morti avviene in ambienti al fuori di strutture sanitarie, sollevando il problema di mancanza di cure tempestive e delle emergenze;
        infatti la residenza privata risulta essere il luogo di decesso più prevalente (2677 morti), seguita dagli ospedali (1626 morti). 
        Ciò suggerisce che la 
        """
    )


    """
    Distribuzione droghe per genere:
    devo prima effettuare un conteggio del coinvolgimento delle droghe, salvate in modo binario (1 = droga usata e 0 = altrimenti)
    """
    risultati = [] # lista vuota che conterrà i valori per maschi e femmina
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

    # Normalizzazione del testo e conteggio per genere
    morti_droga_genere = pl.DataFrame(risultati)

    # non mi andava bene il modo in cui venivano stampate i grafici a barre affiancati,
    # qundi opto per due grafici che riporteranno le info per ogni sesso

    # Creazione di due subset separati per maschi e femmine
    morti_maschi = morti_droga_genere.filter(pl.col("Sesso") == 'Male')
    morti_femmine = morti_droga_genere.filter(pl.col("Sesso") == 'Female')

    grafico_maschi = (
        grafici.crea_grafico_barre(
            dat = morti_maschi,
            y_col = "Conteggio",
            x_col = "Droga",
            color_col = "Conteggio",
            horizontal = True,
            sort = "-x",
            title = "Maschi - Droghe più prevalenti"
        )
    )

    # grafico per le femmine
    grafico_femmine = (
        grafici.crea_grafico_barre(
            dat = morti_femmine,
            y_col = "Conteggio",
            x_col = "Droga",
            color_col = "Conteggio",
            horizontal = True,
            sort = "-x",
            title = "Femmine - Droghe più prevalenti"
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
    Nel complesso, il divario è marcato, con i maschi più frequentemente coinvolti in decessi legati alle droghe rispetto alle femmine. 
    I numeri ci dicono che gli oppioidi sono al centro del fenomeno, con sostanze come l'eroina, fentanyl e i loro derivati tra le droghe più coinvolte.
    La cocaina è un'altra sostanza frequentemente coinvolta, seepure con incidenza inferiore rispetto agli oppioidi.
    Anche altre droghe, in particolari farmaci da prescrizione, contribuiscono al fenomeno, sebbene con influenza inferiore rispetto agli oppioidi.
    """)


    # DISTRIBUZIONE PER RAZZA
    morti_razza = (
        dati
        .filter(pl.col("Race") != "Unknown")
        .group_by("Race")
        .agg(pl.count().alias("Conteggio"))
        .sort("Conteggio", descending = True)
    )

    # morti per razza e sesso (per fare il secondo grafico)
    morti_razza_sesso = (
        dati
        .filter(pl.col("Race") != "Unknown")
        .group_by(["Race", "Sex"])
        .agg(pl.count().alias("Conteggio"))
        .sort("Conteggio", descending=True)
    )


    grafico_razza = (
        grafici.crea_grafico_barre(
            dat = morti_razza,
            x_col = "Race",
            y_col = "Conteggio",
            color_col = "Conteggio",
            title = "Morti per razza",
            horizontal = True,
            sort = "-x"
        )
    )

    grafico_razza_sesso = (
        grafici.crea_grafico_barre(
            dat = morti_razza_sesso,
            x_col = "Race",
            y_col = "Conteggio",
            color_col = "Sex",
            title = "Morti per razza",
            horizontal = True,
            sort = "-x",
            add_text = False
        )
    )

    # accentramento grafico
    col1, col2 = st.columns([1,1])
    with col1:
        st.altair_chart(grafico_razza, use_container_width = False)
    with col2:
        st.altair_chart(grafico_razza_sesso, use_container_width=False)

    st.write("""
    La distribuzione delle morti suddivise per razza riflette principalmente la composizione demografica della popolazione analizzata.
    Infatti si nota subito la netta prevalenza del gruppo *White* con un numero più alto di decessi rispetto agli altri gruppi etnici, con oltre 4000 decessi totali (la cui maggioranza sono uomini).
    Seguono i gruppi *Hispanic White* e *black*.\n
    Nei rimanenti gruppi (minoritari), anche avendo un numero di decessi relativamente basso, si mantiene il trend di maggiore coinvolgimento maschile.
    """)

    st.markdown("Morti per razza e categoria di età")




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

        altri = (
            dati.filter((pl.col(droga) == 1) & (~pl.col("Race").is_in(["Black", "White"]))).height
        )

        # Aggiunta dei risultati con valori coerenti
        risultati.append({"Droga": droga, "Race": "Black", "Conteggio": black})
        risultati.append({"Droga": droga, "Race": "White", "Conteggio": white})
        risultati.append({"Droga": droga, "Race": "Other", "Conteggio": altri})

    # Conversione in DataFrame
    morti_droga_genere = pl.DataFrame(risultati)

    @st.cache_data
    def genera_grafici(_morti_droga_genere):
        """
        funzione fatta salvare in cache i dati creati così da non dover fare ricaricare la pagiona a streamlit quando togglo l'etnia che voglio
        """
        # Creazione di tre subset separati
        morti_black = morti_droga_genere.filter(pl.col("Race") == 'Black')
        morti_white = morti_droga_genere.filter(pl.col("Race") == 'White')
        morti_other = morti_droga_genere.filter(pl.col("Race") == 'Other')

        # Creazione dei grafici con la classe Grafici
        grafico_black = Grafici.crea_grafico_barre(morti_black, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort = "-y",show_legend = False, title="Black - Droghe più prevalenti",
                                                   width = 500, height = 400, label_angle = -90)

        grafico_white = Grafici.crea_grafico_barre(morti_white, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort="-y", title="White - Droghe più prevalenti",show_legend = False,
                                                   width = 500, height = 400, label_angle = -90)

        grafico_other = Grafici.crea_grafico_barre(morti_other, "Droga", "Conteggio", color_col="Conteggio",
                                                   sort="-y", title="Other - Droghe più prevalenti", show_legend = False,
                                                   width = 500, height = 400, label_angle = -90)

        # Restituzione di un dizionario di grafici già pronti
        return {
            "Black": grafico_black,
            "White": grafico_white,
            "Other": grafico_other
        }

    # Generazione e caching dei grafici
    grafici = genera_grafici(morti_droga_genere)

    # Aggiunta del selettore con Streamlit
    #st.write("### Seleziona il gruppo razziale per visualizzare il grafico:")
    # scelta_grafico = st.selectbox(
    #     "Scegli un gruppo razziale:",
    #     options=["Black", "White", "Other"]
    # )

    # # Visualizzazione del grafico scelto
    # col1, col2, col3 = st.columns([1,2,1])
    # with col2:
    #     st.altair_chart(grafici[scelta_grafico])

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.altair_chart(grafici["White"])
    with col2:
        st.altair_chart(grafici["Black"])
    with col3:
        st.altair_chart(grafici["Other"])

    st.write("""
    Il gruppo *White* presenta i valori più elevati di decessi in quasi tutte le sostanze analizzate, in particolare con eroina, fentanyl e benzodiazepine, con numeri particolarmente alti anche per fentanyl_analogue e methadone. 
    Seguono i gruppi *Hispanic White* e *Black*, che mostrano anch'essi un'elevata incidenza di decessi, seppur con una netta differenza rispetto ai numeri osservati nel gruppo *White*. L'eroina e il fentanyl emergono come le sostanze più ricorrenti anche in queste categorie, ma con un'incidenza numerica inferiore.

    Le altre categorie etniche riportano un numero di decessi molto più contenuto.

    Nel complesso, i risultati rispecchiano la composizione demografica del dataset analizzato (maggioranza popolazione *White*)
    """
             )


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
                                                  sort="-x", title="Home - Droghe più prevalenti")

        grafico_hospital = Grafici.crea_grafico_barre(hospital, "Droga", "Conteggio",
                                                      color_col="Conteggio", horizontal=True,
                                                      sort="-x", title="Hospital - Droghe più prevalenti")

        grafico_other = Grafici.crea_grafico_barre(other, "Droga", "Conteggio",
                                                   color_col="Conteggio", horizontal=True,
                                                   sort="-x", title="Other - Droghe più prevalenti")

        return {
            "Home": grafico_home,
            "Hospital": grafico_hospital,
            "Other": grafico_other
        }

    # Generazione e caching dei grafici
    grafici_location = genera_grafici_location(morti_droga_location)

    # Menu a tendina per la selezione del grafico
    st.write("### Seleziona la categoria di Location per visualizzare il grafico:")
    scelta_location = st.selectbox(
        "Scegli una categoria di Location:",
        options=["Home", "Hospital", "Other"]
    )

    # Visualizzazione del grafico scelto al centro
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.altair_chart(grafici_location[scelta_location])








    # CORRELAZIONI TRA VARIABILI NUMERICHE

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
        .drop(["Month", "Day", "Quarter", "Heroin death certificate (DC)", "Other"]) # non mi interessa calcolarle per queste variabili
        .to_pandas() # mi serve per buttare la tabella creata alla funzione corr che userò in seguito
    )
    st.write("Tabella contenente le variabili per cui si vogliono calcolare la correlaioni")
    st.write(dati_numerici)

    correlazioni = dati_numerici.corr(method="pearson")

    st.write("Matrice di correlazione tra variabili numeriche:")

    st.dataframe(correlazioni.style.background_gradient(cmap='PuBu'))

    st.write("""
    **Analisi della matrice di correlazioni**

    L'analisi della matrice di correlazione di Pearson (soprariportata) rivela dinamiche interessanti fra le variabili d'interesse. 

    Il dato più significativo emerge dalla stretta relazione tra l'anno e la diffusione del Fentanyl, con una correlazione di 0.515. Questo indica un aumento drammatico delle morti legate a questo oppioide sintetico nel corso degli anni. Tale tendenza si riflette anche nelle correlazioni con gli analoghi del Fentanyl e con la categoria generica "Qualsiasi Oppioide".

    Le interrelazioni tra le diverse sostanze mostrano interessanti pattern di sostituzione e interconnessione. Ad esempio, Ossicodone e Ossimorphone presentano una correlazione di 0.320, suggerendo comportamenti simili nell'uso di oppioidi da prescrizione. 

    Le correlazioni con l'età sono generalmente deboli, con lievi variazioni: l'Ossicodone mostra una leggera correlazione positiva (0.121), mentre l'eroina presenta una correlazione negativa (-0.129), potenzialmente indicando differenti pattern di consumo tra fasce d'età.

    Il trend temporale più preoccupante riguarda l'incremento degli oppioidi sintetici. L'anno correla positivamente con Fentanyl (0.515), Oppioidi in generale (0.430) e Analoghi del Fentanyl (0.304), delineando una chiara evoluzione verso sostanze sempre più pericolose e potenti.

    Questi risultati sollevano importanti questioni di salute pubblica, evidenziando la necessità di strategie di intervento mirate, specialmente rivolte al dilagante fenomeno degli oppioidi sintetici.
    """)



    # CONCLUSIONE
    st.markdown("""
    ✅ **Conclusione**: 
            - L'analisi esplorativa mostra trend temporali, distribuzioni demografiche e le principali droghe coinvolte.    
            - La matrice di correlazione offre spunti su relazioni tra variabili, utili per analisi successive.
            - La fascia d'età più vulnerabile e le sostanze più pericolose emergono chiaramente dall'analisi.
            """)
