import streamlit as st
import polars as pl
import altair as alt


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# esempio usato per la regressione logistica
# https://www.datacamp.com/tutorial/understanding-logistic-regression-python

# documentazione ufficiale di scikit learn
# https://scikit-learn.org/1.5/modules/generated/sklearn.linear_model.LogisticRegression.html


def analisi_stat(dati, colonne_droga):
    st.title("Analisi statistica - Modelli")
    st.markdown("""

    ### Regressione Logistica
    
    La regressione logistica è appropriata per:
    1. Variabili dipendenti binarie (presenza/assenza di sostanze)
    2. Stima di probabilità di co-occorrenza
    3. Interpretabilità dei coefficienti in termini di odds ratio

    La forma generale del modello di regressione è:
    
    $$P(Y=1|X) = \\frac{1}{1 + e^{-(\\beta_0 + \\beta_1x_1 + ... + \\beta_px_p)}}$$
    
    dove Y è la presenza di una specifica sostanza e X sono le altre sostanze.
    
    Mentre quello per la regressione logistica è:
    
    $logit(p) = log(\\frac{p}{1-p}) = \\beta_0 + \\beta_1x_1 + ... + \\beta_px_p$

    dove p è la probabilità della presenza di una sostanza.
    
    """)


    droga_obiettivo = st.selectbox("Seleziona la droga da predire", colonne_droga)
    altre_droghe = [d for d in colonne_droga if d != droga_obiettivo] # tutte le droghe meno la droga selezionata

    @st.cache_data
    def carica_dati_RL():
        # funzione per caching del dataset
        return dati.select(altre_droghe + [droga_obiettivo]).drop_nulls()

    dati_nonull = carica_dati_RL() # carico i dati con la funzione fatta prima

    # variabili per la definizioned el modello
    X = dati_nonull.select(altre_droghe).to_numpy()
    y = dati_nonull.select(droga_obiettivo).to_numpy().ravel() # trasformo in un vettore riga


    # variabili per il training del modello
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=16)


    @st.cache_resource
    def addestra_modello(X_train, y_train):
        # addestramento del modeello
        modello = LogisticRegression(random_state=16)
        modello.fit(X_train, y_train)
        return modello

    # salvo in una varubaile i risultati del modello
    modello_reg_log = addestra_modello(X_train, y_train)

    # coefficienti del modello
    coefficienti = pl.DataFrame({
        "Droga": altre_droghe,
        "Coefficiente": modello_reg_log.coef_[0]
    }).sort("Coefficiente", descending=True)

    grafico = alt.Chart(coefficienti).mark_bar().encode(
        x=alt.X('Coefficiente:Q', title='Coefficiente'),
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

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.altair_chart(grafico)

    # Aggiunta accuracy score
    accuracy = modello_reg_log.score(X_test, y_test)
    st.markdown(f"""
    ### Performance del Modello
    - Accuracy sul test set: {accuracy:.3f}
    - I coefficienti positivi indicano una correlazione positiva con la presenza della sostanza target
    - I coefficienti negativi indicano una correlazione negativa
    """)


    st.markdown("""
    ### Considerazioni sul Modello
       - Pro: Ottima per variabili binarie
       - Pro: Facilmente interpretabile
       - Contro: Non cattura relazioni non lineari
    """)

