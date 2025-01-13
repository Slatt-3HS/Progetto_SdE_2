
import streamlit as st
import polars as pl
import altair as alt



class Grafici:
    """
    In questa classe creo le funzioni per la stampa dei grafici
    così da standardizzare il più possibile

    Includo anche @staticmethod alle funzioni cosicché non abbiano bisogno dell'argomento self
    """

    @staticmethod
    def crea_grafico_linea(dat,
                           x_col: str,
                           y_col: str,
                           color_col: str = None,
                           title: str = None,
                           width: int = 800,
                           height: int = 400,
                           totale: bool = False):
        """
        Funzione avanzata per creare un grafico a linee con opzioni di highlight e interattività
        """
        base = alt.Chart(dat).mark_line(point=True).encode(
            x=alt.X(f"{x_col}:O", title=x_col.title()),
            y=alt.Y(f"{y_col}:Q", title=y_col.title()),
            tooltip=[
                alt.Tooltip(f"{x_col}:O"),
                alt.Tooltip(f"{y_col}:Q"),
                alt.Tooltip("Percentuale:Q", format=".2f", title="% sul totale"),
                alt.Tooltip(f"{color_col}:N")
            ]
        ).properties(
            width=width,
            height=height,
            title={
                'text': title or f"{y_col} by {x_col}",
                'anchor': 'middle'
            }
        )

        if color_col == "Sex" and not totale:
            base = base.encode(
                color=alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male'],
                        range=['#e377c2', '#1f77b4']
                    )
                )
            )
        elif color_col == "Sex" and totale:
            base = base.encode(
                color=alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male', 'Total'],
                        range=['#e377c2', '#1f77b4', 'black']
                    )
                )
            )
        else:
            base = base.encode(color=alt.Color(f"{color_col}:N"))

        # Highlight con barra verticale
        highlight = alt.selection_single(
            on='mouseover',
            fields=[x_col],
            nearest=False
        )

        punti_highlight = base.mark_point(size=100, filled=True).encode(
            opacity=alt.condition(highlight, alt.value(1), alt.value(0))
        ).add_selection(highlight)

        barra_hover = alt.Chart(dat).mark_rule(color='gray').encode(
            x=alt.X(f"{x_col}:O"),
            size=alt.condition(highlight, alt.value(2), alt.value(0))
        ).transform_filter(highlight)

        grafico = base + punti_highlight + barra_hover

        # calcolo del totale per anno
        if totale:
            totale_annuale = (
                dat.group_by(x_col)
                .agg(pl.sum(y_col).alias("Totale"))
                .with_columns(pl.lit("Total").alias(color_col))
            )

            linea_totale = (
                alt.Chart(totale_annuale).mark_line(point=True).encode(
                    x=alt.X(f"{x_col}:O"),
                    y=alt.Y("Totale:Q"),
                    color=alt.Color(
                        f"{color_col}:N",
                        scale=alt.Scale(
                            domain=['Female', 'Male', 'Total'],
                            range=['#e377c2', '#1f77b4', 'black']
                        )
                    ),
                    tooltip=[
                        alt.Tooltip(f"{x_col}:O"),
                        alt.Tooltip("Totale:Q")
                    ]
                )
            )
            grafico = grafico + linea_totale

        return grafico

    @staticmethod
    def crea_grafico_barre(dat,
                           x_col: str,
                           y_col: str,
                           color_col: str = None,
                           sort: str = "-y",
                           horizontal: bool = False,
                           width: int = 700,
                           height: int = 400,
                           title: str = None,
                           add_text: bool = True):
        """
        Funzione avanzata per creare grafici a barre interattivi e personalizzati con barre affiancate,
        highlight selettivi ed etichette posizionate correttamente.
        """
        if horizontal:
            x_encoding = alt.X(f"{y_col}:Q", title=y_col.title())
            y_encoding = alt.Y(f"{x_col}:N", title=x_col.title(), sort=sort)
        else:
            x_encoding = alt.X(f"{x_col}:N", title=x_col.title(), sort=sort)
            y_encoding = alt.Y(f"{y_col}:Q", title=y_col.title())

        encoding = {'x': x_encoding, 'y': y_encoding}

        if color_col:
            if color_col == "Sex":
                encoding['color'] = alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male'],
                        range=['#e377c2', '#1f77b4']
                    )
                )
                encoding['xOffset'] = alt.XOffset(f"{color_col}:N")
            else:
                encoding["color"] = alt.Color(f"{color_col}:Q", scale=alt.Scale(scheme='blues'))

        # Modifica del sistema di selezione per funzionare su tutte le categorie
        highlight = alt.selection_point(
            on='mouseover',
            nearest=False,
            fields = [x_col, color_col],
            resolve = "global"
        )

        # Tooltip personalizzato
        tooltip = [
            alt.Tooltip(x_col, title="Anno"),
            alt.Tooltip(y_col, title="Morti", format=","),
        ]
        if color_col:
            tooltip.append(alt.Tooltip(color_col, title="Categoria"))

        # Grafico base con highlight sui bordi
        grafico = (
            alt.Chart(dat)
            .mark_bar(strokeWidth=2)
            .encode(
                **encoding,
                tooltip=tooltip,
                opacity=alt.condition(highlight, alt.value(1), alt.value(0.6)),
                stroke=alt.condition(highlight, alt.value('black'), alt.value(None))
            )
            .properties(
                width=width,
                height=height,
                title={'text': title or f"{y_col} by {x_col}", 'anchor': 'middle'}
            )
            .add_selection(highlight)
        )

        # Aggiunta delle etichette sopra ogni barra
        if add_text:
            # Text labels configuration
            text_encoding = {
                'text': alt.Text(f"{y_col}:Q", format=","),
                'opacity': alt.condition(highlight, alt.value(1), alt.value(0.6))  # Add highlight to labels
            }

            # Add xOffset to labels if color_col exists
            if color_col:
                text_encoding['xOffset'] = alt.XOffset(f"{color_col}:N")

            etichette_grafico = (
                alt.Chart(dat)
                .mark_text(
                    align='left' if horizontal else "center",
                    baseline='middle' if horizontal else "bottom",
                    dy=0 if horizontal else -5,
                    dx = 5 if horizontal else 0
                )
                .encode(
                    x=x_encoding,
                    y=y_encoding,
                    **text_encoding
                )
            )

            grafico = grafico + etichette_grafico

        return grafico


    @staticmethod
    def create_grafico_torta(dat, category_col: str, value_col: str, title: str = None,
                         width: int = 600, height: int = 300, inner_radius: int = 50):
        """
        grafico a torta
        """
        total = dat.get_column(value_col).sum()
        dat = dat.with_columns(
            (pl.col(value_col) / total * 100).round(1).alias('percentage'),
            (pl.col(value_col).cast(pl.Utf8)).alias('total_str')
        )

        # Configurazione colori condizionali
        if category_col == "Sex":
            color_scale = alt.Scale(domain=["Female", "Male"], range=['#e377c2', '#1f77b4'])
        else:
            color_scale = alt.Scale(scheme='category20')

        # Selezione per highlight
        highlight = alt.selection_point(
            name='select',
            on='mouseover',
            fields=[category_col]
        )
        # Grafico base con highlight separati
        pie = alt.Chart(dat).mark_arc(innerRadius=inner_radius).encode(
            theta=alt.Theta(f"{value_col}:Q", stack=True),
            color=alt.Color(f"{category_col}:N", scale=color_scale,
                            legend=alt.Legend(title=category_col.title())),
            tooltip=[
                alt.Tooltip(category_col, title="Categoria"),
                alt.Tooltip('percentage', title="Percentuale", format='.1f')
            ]
        ).properties(
            width=width,
            height=height,
            title={
                'text': title or f"{value_col} by {category_col}",
                'anchor': 'middle'
            }
        ).add_selection(highlight).encode(
            opacity=alt.condition(highlight, alt.value(1), alt.value(0.6)),
            stroke=alt.condition(highlight, alt.value('black'), alt.value('transparent')),
            # Bordo nero quando selezionato
            strokeWidth=alt.condition(highlight, alt.value(2), alt.value(0))  # Spessore del bordo
        )

        # Etichette con totali interi sopra ciascuna fetta, colorate in base alla fetta
        text = pie.mark_text(
            size=14
        ).encode(
            text=alt.Text('total_str:N'),
            theta=alt.Theta(f"{value_col}:Q", stack=True),
            radius=alt.value(inner_radius + 90),
            color=alt.Color(f"{category_col}:N", scale=color_scale),
            # Colore delle etichette uguale a quello della fetta
            opacity=alt.condition(highlight, alt.value(1), alt.value(0.8))
        )

        return pie + text

    @staticmethod
    def crea_heatmap(dat,
                     x_col:str,
                     y_col:str,
                     color_col:str,
                     width: int = 800,
                     height: int = 400,
                     title:str = None):
        """
        creo una heatmap
        """
        grafico = (
            alt.Chart(dat).mark_rect().encode(
                x=alt.X(f"{x_col}:O", title=x_col.title()),
                y=alt.Y(f"{y_col}:O", title=y_col.title()),
                color=alt.Color(f"{color_col}:Q", scale=alt.Scale(scheme='viridis')),
                tooltip=[x_col, y_col, color_col]
            ).properties(
                width=width,
                height=height,
                title={'text': title or f"{color_col} by {x_col} and {y_col}", 'anchor': 'middle'}
            )
        )



def analisi_esplorativa(dati, colonne_droga):
    """
    Analisi esplorativa con studio univariato e bivariato delle variabili; include distribuzioni, correlazioni e statistiche principali.
    """

    grafici = Grafici() # inizializzo la classe

    st.header("🔍 Analisi esplorativa del dataset")
    st.write(
        """Di seguito viene riportato il dataset completo, pulito e messo in ordine, usato per l'analisi."""
    )
    st.dataframe(dati)
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


    # Plot morti annuali
    grafico_morti = grafici.crea_grafico_linea(
        dat = morti_annuali_sesso,
        x_col="Year",
        y_col="Morti",
        color_col="Sex",
        totale = True,
        title="Numero di morti per anno"
    )

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico_morti, use_container_width= False)


    morti_mese = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Month", "Sex"])
        .agg(pl.count().alias("Conteggio"))
        #.sort("Conteggio")
    )

    morti_quarter = (
        dati.filter(pl.col("Sex").is_in(["Male", "Female"]))
        .group_by(["Quarter", "Sex"])
        .agg(pl.count().alias("Conteggio"))
        #.sort("Conteggio")
    )

    # Plot morti per mese e trimestre
    grafico_mese = grafici.crea_grafico_barre(
        morti_mese,
        x_col="Month",
        #horizontal = True,
        #sort = "-x",
        #add_text = False,
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Mese"
    )

    grafico_quarter = grafici.crea_grafico_barre(
        morti_quarter,
        x_col="Quarter",
        y_col="Conteggio",
        color_col="Sex",
        title="Morti per Trimestre"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.altair_chart(grafico_mese, use_container_width=False)
    with col2:
        st.altair_chart(grafico_quarter, use_container_width=False)

    st.write("""
    Nel corso degli anni viene osservato un aumento progressivo delle morti, con un incremento significativo a partire dal 2015 e che culmina nel 2017 dove vengono registrati più di mille decessi.
    Quelli maschili risultano costantemente più elevati rispetto a quelli femminili, con un rapporto che tende a rimanere stabile nel tempo.
    
    La distribuzione rivela una costanza nei decessi durante l'anno, con una leggera tendenza all'aumento nei mesi estivi e invernali.
    Per gli uomini, i mesi con il più alto numero di decessi sono ottobre novembre, mentre per le donne l'incremento risulta uniforme, anche se con leggeri picchi nei mesi di dicembre e gennaio.
    Questa distribuzione potrebbe essere legata a fattori stagionali.
    
    L'analisi trimestrale conferma le tendenze scaturite prima, mostrando un incremento gruaduale (leggero) nel corso dellì'anno, con il quarto trimestre come periodo di maggiore incidenza per entrambi i generi.
    
    """)

    # Distribuzione per sesso
    morti_sesso = (
        dati
        .group_by("Sex")
        .agg(pl.count()
             .alias("Morti totali")
             )
        .filter(pl.col("Sex").is_in(["Male", "Female"]))
    )

    torta_morti_sesso = (
        grafici.create_grafico_torta(
            dat = morti_sesso,
            category_col = "Sex",
            value_col = "Morti totali",
            title = "Distribuzione genere"
        )
    )

    # Accentramento grafico
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(torta_morti_sesso, use_container_width=False)
    st.write(
        "📊 Il sesso più colpito dal fenomeno oggetto di studio è, come visibile dal grafico a torta sopra, quello maschile (circa 74% sul totale)."
    )

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
        st.altair_chart(grafico_maschi, use_container_width=False)
    with col2:
        st.altair_chart(grafico_femmine, use_container_width=False)

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
        alt.Chart(morti_razza).mark_bar().encode(
            y=alt.Y("Race:N", title="Razza", sort = "-x"),
            x=alt.X("Conteggio:Q", title="Numero di Morti"),
            tooltip=["Race", "Conteggio"]
        ).properties(
            title={'text':"Distribuzione dei Decessi per Razza", 'anchor':'middle'},
            width=600,
            height=400
        )
    )

    etichette_razza = (
        alt.Chart(morti_razza).mark_text(
            align='left',
            baseline='middle',
            dx=5,
            fontWeight='bold'
        ).encode(
            y=alt.Y("Race:N", sort= '-x'),
            x='Conteggio:Q',
            text='Conteggio:Q'
        )
    )

    # grafico_razza_sesso = crea_grafico_barre(morti_razza_sesso, "Race", "Morti per razza (suddivisi per sesso)")


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

    risultati = []
    for droga in colonne_droga:
        conteggio = (
            dati
            .filter(pl.col(droga) == 1)
            .group_by("Race")
            .agg(pl.count().alias("Conteggio"))
            .with_columns(pl.lit(droga).alias("Droga"))
        )
        risultati.append(conteggio)

    morti_razza_droga = pl.concat(risultati)

    # grafico a barre
    grafico_razza_droga = (
        alt.Chart(morti_razza_droga).mark_bar().encode(
            y=alt.Y("Droga:N", title="Droga", sort='-x'),
            x=alt.X("Conteggio:Q", title="Numero di Morti"),
            color=alt.Color('Race:N'),
            tooltip=["Droga", "Race", "Conteggio"]
        ).properties(
            title={'text':"Droghe più Prevalenti per Razza", 'anchor':'middle'}
            #width=1200,
            #height=400
        )
    )

    st.altair_chart(grafico_razza_droga, use_container_width=True)

    st.write("""
    Il gruppo *White* presenta i valori più elevati di decessi in quasi tutte le sostanze analizzate, in particolare con eroina, fentanyl e benzodiazepine, con numeri particolarmente alti anche per fentanyl_analogue e methadone. 
    Seguono i gruppi *Hispanic White* e *Black*, che mostrano anch'essi un'elevata incidenza di decessi, seppur con una netta differenza rispetto ai numeri osservati nel gruppo *White*. L'eroina e il fentanyl emergono come le sostanze più ricorrenti anche in queste categorie, ma con un'incidenza numerica inferiore.

    Le altre categorie etniche riportano un numero di decessi molto più contenuto.

    Nel complesso, i risultati rispecchiano la composizione demografica del dataset analizzato (maggioranza popolazione *White*)
    """)


    """
    st.write("Colonne presenti:", dati.columns)

    morti_cat = (
        dati.with_columns(
            pl.col("Age").map_elements(categorizza_età).alias("cat_età")
        )
    )

    morti_cat_razza = (
        morti_cat.with_columns(
            pl.when(pl.col("Race").str.contains("White")).then("White")
            .when(pl.col("Race").str.contains("Black")).then("Black")
            .when(pl.col("Race").str.contains("Hispanic")).then("Hispanic")
            .otherwise("Other")
            .alias("Race_raccolte")
        )
    )

    morti_eta_razza = (
        morti_cat_razza
        .group_by(["cat_età", "Race_raccolte"])
        .agg(pl.count().alias("Conteggio"))
        .sort("Conteggio", descending=True)
    )

    # ✅ Funzione per creare il grafico di ciascun gruppo etnico
    def crea_grafico_razza(data, razza):
        subset = data[data["Race_raccolte"] == razza]
        return alt.Chart(subset).mark_bar().encode(
            x=alt.X("cat_età:N", title="Categoria di Età", sort=['21-', '21-30', '31-40', '41-50', '51-60', '60+']),
            y=alt.Y("Conteggio:Q", title="Numero di Morti"),
            tooltip=["cat_età", "Conteggio"]
        ).properties(
            title=f"Morti per Categoria di Età - {razza}",
            width=300,
            height=400
        )

    grafico_white = crea_grafico_razza(morti_eta_razza, "White")
    grafico_black = crea_grafico_razza(morti_eta_razza, "Black")
    grafico_hispanic_white = crea_grafico_razza(morti_eta_razza, "Hispanic_White")
    grafico_other = crea_grafico_razza(morti_eta_razza, "Other")

    st.write("### Distribuzione delle Morti per Categoria di Età e Razza")
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(grafico_white, use_container_width=False)
        st.altair_chart(grafico_hispanic_white, use_container_width=False)
    with col2:
        st.altair_chart(grafico_black, use_container_width=False)
        st.altair_chart(grafico_other, use_container_width=False)
    
    """












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
