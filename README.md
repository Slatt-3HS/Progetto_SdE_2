# Progetto_SdE_2
Progetto per l'esame di Sistemi di Elaborazione 2 (aa 2024/25 prof. Matteo Ceccarello)

# Analisi delle Morti da Overdose in Connecticut (2012-2023)

## Scopo del Progetto
Questo progetto utilizza dati reali per analizzare le morti da overdose in Connecticut dal 2012 al 2023. L'obiettivo è identificare tendenze temporali, differenze geografiche e sostanze coinvolte, fornendo spunti utili per la prevenzione e gestione del fenomeno.


## Struttura del Progetto
### File Python
- **`app.py`**: Script principale che integra tutte le analisi con Streamlit.
- **`preprocessing.py`**: Modulo per il caricamento e preprocessing dei dati.
- **`intro_descrittiva.py`**: Introduzione e contesto del problema.
- **`analisi_geografica.py`**: Analisi geografica e creazione di mappe interattive.
- **`analisi_stat.py`**: Modelli statistici per identificare correlazioni tra sostanze.
- **`classe_Grafici.py`**: Classe per la generazione di grafici standardizzati.
- **`barra_laterale.py`**: Creazione della barra laterale per la navigazione.

### File CSV
- **`morti_droga.csv`**: Dataset principale contenente le informazioni sui decessi.

---

## Dati Utilizzati
- **Fonte**: [Data.gov](https://catalog.data.gov/dataset/accidental-drug-related-deaths-2012-2018).
- **Descrizione**:
  - Morti per overdose con dettagli su data, luogo, età, sesso, etnia e sostanze implicate.
  - Variabili chiave: `Date`, `Age`, `Sex`, `Race`, `Death City`, `Death County`, `DeathCityGeo`, e sostanze stupefacenti.
- **Dimensione del dataset**: 11.981 record (2012-2023).

---

## Preprocessing Applicato
1. **Pulizia dei Dati**:
   - Rimozione valori nulli in variabili critiche (`Age`, `Sex`, `Race`) con strategie mirate (es. media, sostituzione con "Unknown").
   - Conversione delle variabili relative alle droghe in formato binario (`1 = rilevata`, `0 = non rilevata`).

2. **Trasformazioni**:
   - Estrazione di coordinate geografiche da `DeathCityGeo`.
   - Creazione di variabili temporali (`Year`, `Month`, `Quarter`, `DayOfWeek`) per analisi storiche.

3. **Ottimizzazione del Dataset**:
   - Riordino e formattazione delle colonne per una migliore leggibilità e analisi.

---

## Analisi e Visualizzazioni
### Analisi Geografica
- Mappe interattive (heatmap e cluster) per evidenziare le aree maggiormente colpite.
- Distribuzione geografica bivariata con altre variabili

### Analisi Statistica
- Modelli di regressione logistica per studaire la compresenzaz tra sostanze.
- Metriche di performance e interpretazione dei coefficienti.

### Visualizzazioni
- Grafici temporali, a barre, boxplot e grafici a torta per sintetizzare le informazioni.

---

## Guida all'Esecuzione del Progetto

`uv` è un gestore di dipendenze Python che automatizza la configurazione degli ambienti virtuali e semplifica l'installazione delle librerie richieste. 
Con `uv`, non è necessario configurare manualmente un ambiente virtuale o installare pacchetti, tutto viene gestito automaticamente.

**Comando principale:**
Dal terminale entrare nella cartella dove è salvato il progeeto e eseguire il comando:
```bash
uv run streamlit run app.py
```

## Studente
Telly Ibrahim Guindo (Mat. 2077790)

