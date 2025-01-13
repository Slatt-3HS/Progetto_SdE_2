import streamlit as st
import polars as pl
import pandas as pd
import altair as alt

import scipy.stats as stats

import matplotlib.pyplot as plt

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, PoissonRegressor
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix, classification_report


# vecchi test impostati
def analisi_stat_1(dati, colonne_droga):
    '''
    in questa funzione raccolgo tutti i test statistici
    '''
    st.header("Analisi statistica del dataset")

    ## scelta del test
    tipo_analisi = st.selectbox(
        "Selezionare l'analisi da effettuare",
        [
            "Test delle occorrenze delle droghe (Test Chi-quadro)",
            "Test di normalità della distribuzione dell'età dei soggetti",
            "Confronto sui tassi di mortalità"
        ]
    )

    if tipo_analisi == "Test delle occorrenze delle droghe (Test Chi-quadro)":
        st.subheader("Test delle occorrenze delle droghe (Test Chi-quadro)")

        # quest test va fatto su deu droghe per il confronto
        droga1, droga2 = st.multiselect(
            "Seleziona due droghe per il confronto",
            colonne_droga, default = colonne_droga[:2]
        )

        if droga1 and droga2:
            # creo una tabella di contingenza, utile per il test di seguito
            # devo per forza convertirla in un df in pandas per poi eseguire il test
            tab_contingenza = pd.crosstab(
                dati[droga1].to_pandas(),
                dati[droga2].to_pandas()
            )
            '''
            adesso faccio il Chi2 test
            usiamo la funzione specifica dalla libreria scipy
            https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
            '''
            print(tab_contingenza)
            chi_oss, pval, gdl, valatteso = stats.chi2_contingency(tab_contingenza)
            st.write(f"Statistica osservata Chi-quadro: {chi_oss}, con {gdl} gradi di libertà")
            st.write(f"p-value = Pr(X^2 > {chi_oss}) = {pval}")

            # conclusione test (accettto/rifiuto)
            alfa_std = 0.05
            if pval < alfa_std:
                st.success(f"Esiste una relazione significativa fra {droga1} e {droga2}")
            else:
                st.warning(f"Non esiste relazione significativa fra {droga1} e {droga2}")

    elif tipo_analisi == "Test di normalità della distribuzione dell'età dei soggetti":
        '''
        ipotesi statistica testante la normalità della distribuzione di Age
        fatta con la funzione normaltest() di scipy, di seguito link per approfondire:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html
        '''
        st.subheader("Analisi della distribuzione dell'età dei soggetti")

        # statistiche descrittive, arrotonda a due cifre decimali e trasponi
        stat_età = dati["Age"].to_pandas().describe()
        stat_età = pd.DataFrame(stat_età).T
        stat_età = stat_età.style.format("{:.2f}")


        st.write("Principali statistiche descrittive della distribuzione d'età dei soggetti")
        st.write(stat_età, use_container_width = True)

        # test di normalità
        z_oss, pval = stats.normaltest(dati["Age"].to_pandas())
        st.write()
        if pval<0.00000000005:
            st.write(f"Il Test di normalità ha restituito una statistica osservata pari a {z_oss.round(2)} e un p-value praticamente nullo.")
        else:
            st.write(f"Il Test di normalità ha restituito una statistica osservata pari a {z_oss.round(2)} e un p-value pari a {pval.round(2)}")

        # rigetto/non rigetto H0
        if pval < 0.05:
            st.warning("La dsitribuzione della variabile 'Age' devia in maniera significativa dalla distribuzione normale.")
        else:
            st.success("La ariabile 'Age' (età dei soggetti) è normlmente distribuita.")

        boxplot_età = (
            alt.Chart(
                dati.to_pandas()
            ).mark_boxplot()
            .encode(
                y = alt.Y("Age:Q")
            ).properties(title = "Boxplot della distribuzione d'età")
        )
        st.altair_chart(boxplot_età, use_container_width = True)

    elif tipo_analisi == "Confronto sui tassi di mortalità":
        st.subheader("Confronto sui tassi di mortalità")

        confronti = st.selectbox(
            "Confronto sui tassi di mortalità per",
            ["Sex", "Race", "Year"]
        )

        # vari raggruppamenti per i confronti scelti dal checkbox sopra
        if confronti == "Sex":
            perSex  = dati.groupby("Sex").agg([
                pl.count().alias("Morti totali"),
                pl.col("Age").mean().alias("Età media")
            ])
            st.dataframe(perSex)

        elif confronti == "Race":
            perRace = dati.groupby("Race").agg([
                pl.count().alias("Morti totali"),
                pl.col("Age").mean().alias("Età media")
            ])
            st.dataframe(perRace)

            # grafico mark_line sovrappoennte tutte le morti per razza con diversi colori
            # cona cnhe una legenda allegata
            grafico_razze = (
                alt.Chart(perRace.to_pandas())
                .mark_line(point=True).encode(
                    x = "Razza:O",
                    y = "Morti totali:Q",
                    color = "Race",
                )
            )

        elif confronti == "Year":
            perYear = dati.groupby("Year").agg([
                pl.count().alias("Morti totali"),
                pl.col("Age").mean().alias("Età media")
            ])
            st.dataframe(perYear)

            # grafici
            grafico_anni = (
                alt.Chart(perYear.to_pandas())
                .mark_line(point=True).encode(
                    x = "Anno:O",
                    y = "Morti totali:Q",
                    tooltip = ["Year","Morti totali","Età media"]
                ).properties(title="Morti legate alla droga per anno")
            )
            alt.altair_chart(grafico_anni, use_container_width = True)

def analisi_stat(dati, colonne_droga):
    st.title("Analisi statistica - Modelli")
    st.markdown("""
    ## Introduzione alla scelta dei modelli
    
    Il dataset presenta caratteristiche che richiedono l'utilizzo di modelli statistici appropriati, quali:
    
    1. **Natura dei dati**:
        - Conteggi discreti (numero di decessi)
        - Variabili binariae (presenza di sostanze)
        - Struttura temporale dei dati (data di morte AA/MM/DD)
    
    2. **Obiettivi modelli**:
        - Modellare il numero di decessi nel tempo e fare eventuali previsione
        - Identificare relazioni fra le diverse sostanze
        - Analizzare trend temporali e l'eventuale presenza di stagionalità
    
    Per rispondere a questi obiettivi adottiamo tre approcci statistici:
    
    ### 1. Regressione di Poisson
    Per eventi rilevati in natura discreta (nel nostro caso i conteggi delle morti per anno), la distribuzione di Poisson è la più adeguata.
    
    
    $Y_i \\sim Poisson(\\lambda_i)$ allora

    $$log(\\lambda_i) = \\beta_0 + \\beta_1x_{i1} + ... + \\beta_px_{ip}$$
    
    dove $\\lambda_i$ è il tasso di eventi (decessi) e $x_i$ sono le variabili predittive.
    
    ### 2. Regressione Logistica
    Per analizzare la compresenza di sostanze, utilizziamo la regressione logistica:
    
    $P(Y=1|X) = \\frac{1}{1 + e^{-(\\beta_0 + \\beta_1x_1 + ... + \\beta_px_p)}}$
    
    dove Y è la presenza di una specifica sostanza e X sono le altre sostanze.
    
    ### 3. Analisi delle Serie Temporali
    Per l'analisi temporale, consideriamo la decomposizione:
    
    $Y_t = T_t + S_t + \\epsilon_t$
    
    dove $T_t$ è il trend, $S_t$ la componente stagionale e $\\epsilon_t$ il termine di errore.
    """)

    # finestre selezionabili per la visione del modello voluto
    tab1, tab2, tab3 = (
        st.tabs([
            "Regressione di Poisson",
            "Regressione Logistica",
             "Analisi serie temporali"
        ])
    )

    with tab1:
        st.header("Modello di Regressione di Poisson")
        st.markdown("""
        ### Motivazione Teorica
        Il modello di Poisson è particolarmente adatto per questo dataset perché:
        1. Modella eventi rari e discreti
        2. Assume che gli eventi siano indipendenti nel tempo
        3. Il tasso di eventi (λ) può variare in base a predizioni

        La funzione di probabilità è:

        $P(Y=k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}$

        dove λ è il parametro di intensità che modelliamo attraverso i predizioni.
        """)

        morti_mensili = (
            dati
            .group_by(["Year", "Month"])
            .len()
            .sort(["Year", "Month"])
        )

        X = morti_mensili.select(["Year", "Month"]).to_numpy()
        y = morti_mensili.select("len").to_numpy().ravel() # rendo unidimensionale il dataset

        modello_poisson = PoissonRegressor()
        modello_poisson.fit(X, y)
        predizioni = modello_poisson.predict(X)

        risultati = pl.DataFrame({
            "Year": morti_mensili["Year"],
            "Month": morti_mensili["Month"],
            "Actual": y,
            "Predicted": predizioni
        })

        grafico_poisson = (
            alt.Chart(risultati).mark_line(point=True).encode(
                x=alt.X('Year:Q', title='Anno'),
                y=alt.Y('Actual:Q', title='Numero di Decessi'),
                color=alt.value('blue')
            ).properties(
                width=600,
                height=400,
                title='Decessi Reali vs Predetti (Regressione di Poisson)'
            ) + alt.Chart(risultati).mark_line(color='red').encode(
                x='Year:Q',
                y='Predicted:Q'
            )
        )

        st.altair_chart(grafico_poisson, use_container_width = False)

        # stampo anche i risultati delmodello
        mse = np.mean((y - predizioni) ** 2)
        st.markdown(f"""
            ### Metriche di Performance
            - MSE (Mean Squared Error): {mse:.2f}
            - Coefficienti del modello:
            - Intercetta: {modello_poisson.intercept_:.3f}
        """)

    with tab2:
        st.header("Modello di Regressione Logistica")
        st.markdown("""
        ### Motivazione Teorica
        La regressione logistica è appropriata per:
        1. Variabili dipendenti binarie (presenza/assenza di sostanze)
        2. Stima di probabilità di co-occorrenza
        3. Interpretabilità dei coefficienti in termini di odds ratio

        Il modello stima:

        $logit(p) = log(\\frac{p}{1-p}) = \\beta_0 + \\beta_1x_1 + ... + \\beta_px_p$

        dove p è la probabilità della presenza di una sostanza.
        """)
        droga_obiettivo = st.selectbox("Seleziona la droga da predire", colonne_droga)
        altre_droghe = [d for d in colonne_droga if d != droga_obiettivo]

        dati_nonull = dati.select(altre_droghe + [droga_obiettivo]).drop_nulls()

        X = dati_nonull.select(altre_droghe).to_numpy()
        y = dati_nonull.select(droga_obiettivo).to_numpy().ravel()


        #st.write(X[:5])  # Mostra i primi 5 elementi
        #st.write(y[:5])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        modello_reg_log = LogisticRegression(random_state=42)
        modello_reg_log.fit(X_train, y_train)

        coefficienti = pl.DataFrame({
            "Droga": altre_droghe,
            "Coefficiente": modello_reg_log.coef_[0]
        }).sort("Coefficiente", descending=True)

        chart = alt.Chart(coefficienti.to_pandas()).mark_bar().encode(
            x=alt.X('Coefficiente:Q', title='Importanza'),
            y=alt.Y('Droga:N', sort='-x', title='Droga'),
            color=alt.condition(
                alt.datum.Coefficiente > 0,
                alt.value("blue"),
                alt.value("red")
            )
        ).properties(
            width=600,
            height=400,
            title=f'Importanza delle Droghe nella Predizione di {droga_obiettivo}'
        )

        st.altair_chart(chart)

        # Aggiunta accuracy score
        accuracy = modello_reg_log.score(X_test, y_test)
        st.markdown(f"""
        ### Performance del Modello
        - Accuracy sul test set: {accuracy:.3f}
        - I coefficienti positivi indicano una correlazione positiva con la presenza della sostanza target
        - I coefficienti negativi indicano una correlazione negativa
        """)

    with tab3:
        st.header("Analisi delle Serie Temporali")
        st.markdown("""
        ### Motivazione Teorica
        L'analisi delle serie temporali è fondamentale per:
        1. Identificare pattern temporali ricorrenti
        2. Quantificare trend e stagionalità
        3. Prevedere futuri andamenti

        Il modello base considera:

        $Y_t = T_t + S_t + \\epsilon_t$

        dove:
        - $T_t$ è il trend temporale
        - $S_t$ è la componente stagionale
        - $\\epsilon_t$ è il termine di errore casuale
        """)


        def media_mobile(dati, colonna, finestra = 3):
            """Calcolo della media mobile in una finestra di tempo defintia"""
            mm = (
                dati.with_columns(
                    pl.col(colonna)
                    .rolling_mean(finestra)
                    .alias(f"{colonna}_media_mobile")
                )
            )

            return mm

        droga_selezionata = st.selectbox("Seleziona la droga da analizzare", colonne_droga)

        dati_temporali = (
            dati
            .group_by("Year")
            .agg([
                pl.col(droga_selezionata).sum().alias("Conteggio")
            ]).sort("Year")
        ).with_columns(
            pl.col("Conteggio").rolling_mean(3).alias("MediaMobile")
        )

        # semplice previsione per gli anni successivi
        ultimi_anni = (
            dati_temporali.filter(pl.col("Year") > 2018)
            .with_columns(
                (pl.col("MediaMobile").mean()).alias("Previsione")
            )
        )


        # Calcolo delle statistiche descrittive
        stat_descrittive = dati_temporali.select("Conteggio").describe()


        # Grafico Altair con previsioni
        grafico_temporale = (
            alt.Chart(dati_temporali).mark_line(point=True).encode(
                x="Year:Q",
                y="Conteggio:Q",
                tooltip=["Year", "Conteggio"]
            )
        )

        grafico_media_mobile = (
            alt.Chart(dati_temporali).mark_line(color="red").encode(
                x="Year:Q",
                y="MediaMobile:Q"
            )
        )

        grafico_previsioni = (
            alt.Chart(ultimi_anni).mark_line(color="green").encode(
                x="Year:Q",
                y="Previsione:Q"
            )
        )

        st.altair_chart(grafico_temporale + grafico_media_mobile + grafico_previsioni, use_container_width = True)


        media = float(stat_descrittive.filter(pl.col("statistic") == "mean")["Conteggio"][0])
        dev_std = float(stat_descrittive.filter(pl.col("statistic") == "std")["Conteggio"][0])
        minimo = float(stat_descrittive.filter(pl.col("statistic") == "min")["Conteggio"][0])
        massimo = float(stat_descrittive.filter(pl.col("statistic") == "max")["Conteggio"][0])

        # Metriche di previsione
        previsione_media = ultimi_anni["Previsione"].mean()
        st.markdown(f"**Valore Medio Previsto per gli Anni Futuri:** {previsione_media}:.2f")


        # Visualizzazione con Markdown
        st.markdown(f"""
        ### Statistiche Descrittive per {droga_selezionata}
        - **Media:** {media:.2f}
        - **Deviazione Standard:** {dev_std:.2f}
        - **Min:** {minimo:.2f}
        - **Max:** {massimo:.2f}
        """)

    st.markdown("""
    ### Considerazioni sui Modelli

    1. **Regressione di Poisson**:
       - Pro: Modella correttamente dati di conteggio
       - Pro: Gestisce bene la non-negatività
       - Contro: Assume equidispersione (cioè che la varianza e la media siano uguali)

    2. **Regressione Logistica**:
       - Pro: Ottima per variabili binarie
       - Pro: Facilmente interpretabile
       - Contro: Non cattura relazioni non lineari

    3. **Analisi delle Serie Temporali**:
       - Pro: Cattura pattern temporali
       - Pro: Considera la stagionalità
       - Contro: Richiede dati temporali sufficienti
    """)

def analisi_stat_2(dati, colonne_droga):
    st.title("Analisi Statistica del Dataset")
    st.markdown("""
        ## Introduzione alla Scelta dei Modelli Statistici
        Questa analisi esplora i decessi per droga attraverso diverse tecniche statistiche.  
        I modelli utilizzati sono:

        - **Regressione Binomiale Negativa** per dati di conteggio con overdispersion
        - **Regressione Logistica** per la probabilità di assunzione di una sostanza
        - **Serie Temporali con Decomposizione** per l'analisi e la previsione di tendenze
        ---
        """)

    tab1, tab2, tab3 = st.tabs(["Regressione Binomiale Negativa", "Regressione Logistica", "Serie Temporali"])

    # REGRESSIONE BINOMIALE NEGATIVA
    with tab1:
        st.header("Regressione Binomiale Negativa")
        st.markdown(r"""
            La regressione binomiale negativa è un'estensione della regressione di Poisson che gestisce l'overdispersion.
            Il modello assume che la varianza può essere maggiore della media secondo la formula:

            \[
            Var(Y) = \mu + \alpha\mu^2
            \]

            dove \(\alpha\) è il parametro di dispersione.
            """)

        # Preparazione dati con feature engineering
        morti_mensili = (
            dati.group_by(["Year", "Month"])
            .agg(pl.count().alias("Morti"))
            .sort(["Year", "Month"])
        )

        # Aggiunta feature temporali
        morti_mensili = morti_mensili.with_columns([
            (pl.col("Month").sin() * 2 * np.pi / 12).alias("Month_sin"),
            (pl.col("Month").cos() * 2 * np.pi / 12).alias("Month_cos")
        ])

        X = morti_mensili.select(["Year", "Month_sin", "Month_cos"]).to_numpy()
        y = morti_mensili.select("Morti").to_numpy().ravel()

        # Aggiunta costante per statsmodels
        X_sm = sm.add_constant(X)

        # Fit del modello binomiale negativo
        modelo_nb = sm.NegativeBinomial(y, X_sm).fit()

        # Predizioni
        predizioni = modelo_nb.predict(X_sm)

        # Calcolo intervalli di confidenza
        prediction_ci = modelo_nb.get_prediction(X_sm)
        ci_lower = prediction_ci.conf_int()[:, 0]
        ci_upper = prediction_ci.conf_int()[:, 1]

        # Metriche di valutazione
        r2 = r2_score(y, predizioni)
        rmse = np.sqrt(mean_squared_error(y, predizioni))
        alpha = modelo_nb.params[-1]  # parametro di dispersione

        # DataFrame per visualizzazione
        risultati_nb = pl.DataFrame({
            "Year": morti_mensili["Year"],
            "Month": morti_mensili["Month"],
            "Actual": y,
            "Predicted": predizioni,
            "CI_Lower": ci_lower,
            "CI_Upper": ci_upper
        })

        # Grafico migliorato
        base = alt.Chart(risultati_nb.to_pandas())

        # Area intervallo di confidenza
        confidence_area = base.mark_area(
            opacity=0.2,
            color='#8B9FBF'
        ).encode(
            x=alt.X('Year:Q', title='Anno'),
            y=alt.Y('CI_Lower:Q', title='Numero di Decessi'),
            y2=alt.Y2('CI_Upper:Q')
        )

        # Linea valori reali
        linea_actual = base.mark_line(
            color='#5276A7',
            strokeWidth=2
        ).encode(
            x='Year:Q',
            y='Actual:Q',
            tooltip=['Year:Q', 'Month:Q', 'Actual:Q']
        )

        # Punti valori reali
        punti_actual = base.mark_circle(
            color='#5276A7',
            size=60
        ).encode(
            x='Year:Q',
            y='Actual:Q'
        )

        # Linea predizioni
        linea_predicted = base.mark_line(
            color='#F18727',
            strokeDash=[6, 4],
            strokeWidth=2
        ).encode(
            x='Year:Q',
            y='Predicted:Q',
            tooltip=['Year:Q', 'Month:Q', 'Predicted:Q']
        )

        grafico_finale = (confidence_area + linea_actual + punti_actual + linea_predicted).properties(
            width=700,
            height=400,
            title='Confronto tra Valori Reali e Predetti (con Intervalli di Confidenza)'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(grafico_finale)

        # Metriche
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R² Score", f"{r2:.3f}")
        with col2:
            st.metric("RMSE", f"{rmse:.2f}")
        with col3:
            st.metric("Alpha (dispersione)", f"{alpha:.3f}")

        # Sommario del modello
        st.markdown("### Sommario del Modello")
        st.text(modelo_nb.summary().as_text())

    # REGRESSIONE LOGISTICA
    with tab2:
        st.header("Regressione Logistica")
        st.markdown(r"""
            La regressione logistica modella la probabilità di un evento binario.

            \[
            P(Y=1 | X) = \frac{1}{1 + e^{-(\beta_0 + \sum \beta_k X_k)}}
            \]
            """)

        droga_target = st.selectbox("Seleziona la droga target", colonne_droga)
        altre_droghe = [d for d in colonne_droga if d != droga_target]

        # Preprocessing
        dati_puliti = dati.select(altre_droghe + [droga_target]).drop_nulls()

        # Bilanciamento classi
        classe_minoritaria = dati_puliti[droga_target].sum()
        classe_maggioritaria = len(dati_puliti) - classe_minoritaria
        ratio = classe_minoritaria / classe_maggioritaria

        if ratio < 0.2:
            st.warning(f"Attenzione: Dataset sbilanciato (ratio: {ratio:.2f})")
            # Qui si potrebbe implementare SMOTE o altre tecniche di bilanciamento

        X = dati_puliti.select(altre_droghe).to_numpy()
        y = dati_puliti.select(droga_target).to_numpy().ravel()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        modello_logistico = LogisticRegression(class_weight='balanced')
        modello_logistico.fit(X_train, y_train)

        y_pred = modello_logistico.predict(X_test)

        # Metriche e visualizzazioni
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)

        # Visualizzazione coefficienti
        coef_df = pl.DataFrame({
            'Feature': altre_droghe,
            'Coefficient': modello_logistico.coef_[0]
        }).sort("Coefficient", reverse=True)

        grafico_coef = alt.Chart(coef_df.to_pandas()).mark_bar().encode(
            x=alt.X('Coefficient:Q', title='Coefficiente'),
            y=alt.Y('Feature:N', sort='-x', title='Droga'),
            color=alt.condition(
                alt.datum.Coefficient > 0,
                alt.value('#5276A7'),
                alt.value('#F18727')
            )
        ).properties(
            width=700,
            height=400,
            title='Importanza delle Features'
        )

        st.altair_chart(grafico_coef)

        # Metriche in colonne
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Accuracy", f"{report['accuracy']:.3f}")
        with col2:
            st.metric("Precision", f"{report['weighted avg']['precision']:.3f}")
        with col3:
            st.metric("Recall", f"{report['weighted avg']['recall']:.3f}")

    # SERIE TEMPORALI
    with tab3:
        st.header("Analisi delle Serie Temporali")
        st.markdown(r"""
            L'analisi delle serie temporali utilizza una decomposizione in:
            - Trend
            - Stagionalità
            - Componente residua

            La media mobile viene calcolata con una finestra ottimizzata.
            """)

        droga_selezionata = st.selectbox(
            "Seleziona una droga per l'analisi temporale",
            colonne_droga
        )

        # Preparazione serie temporale
        dati_temporali = (
            dati.group_by("Year")
            .agg(pl.col(droga_selezionata).sum().alias("Conteggio"))
            .sort("Year")
        )

        # Calcolo finestra ottimale per media mobile
        n = len(dati_temporali)
        window_size = min(max(3, n // 5), 7)  # Tra 3 e 7, scaled with data

        # Media mobile e trend
        dati_temporali = dati_temporali.with_columns([
            pl.col("Conteggio")
            .rolling_mean(window_size)
            .alias("Trend"),
            pl.col("Conteggio")
            .rolling_std(window_size)
            .alias("Volatilità")
        ])

        # Grafico migliorato
        base = alt.Chart(dati_temporali.to_pandas()).encode(
            x=alt.X('Year:Q', title='Anno')
        )

        area = base.mark_area(
            opacity=0.3,
            color='#5276A7'
        ).encode(
            y=alt.Y(
                'Conteggio:Q',
                title='Numero di Casi'
            )
        )

        linea = base.mark_line(
            color='#5276A7',
            strokeWidth=2
        ).encode(
            y='Conteggio:Q'
        )

        trend = base.mark_line(
            color='#F18727',
            strokeWidth=3
        ).encode(
            y='Trend:Q'
        )

        banda_confidenza = base.mark_area(
            opacity=0.2,
            color='#F18727'
        ).encode(
            y=alt.Y('ConfLow:Q', title='Intervallo di Confidenza'),
            y2=alt.Y2('ConfHigh:Q')
        ).transform_calculate(
            ConfLow="datum.Trend - datum.Volatilità",
            ConfHigh="datum.Trend + datum.Volatilità"
        )

        grafico_finale = (area + linea + banda_confidenza + trend).properties(
            width=700,
            height=400,
            title=f'Trend Temporale per {droga_selezionata}'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(grafico_finale)

        # Analisi del trend
        trend_attuale = dati_temporali["Trend"].tail(1)[0]
        trend_precedente = dati_temporali["Trend"].tail(2)[0]
        variazione = ((trend_attuale - trend_precedente) / trend_precedente) * 100

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Trend Attuale",
                f"{trend_attuale:.1f}",
                f"{variazione:+.1f}%"
            )
        with col2:
            st.metric(
                "Volatilità Media",
                f"{dati_temporali['Volatilità'].mean():.1f}"
            )


