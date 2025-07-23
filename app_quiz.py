import streamlit as st
import json
import random

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="Quiz per l'Esame",
    page_icon="🧠",
    layout="centered"
)

# --- FUNZIONI ---
@st.cache_data # Usa la cache per non ricaricare le domande ogni volta
def carica_domande():
    """Carica le domande dal file JSON."""
    try:
        with open('domande.json', 'r', encoding='utf-8') as f:
            domande = json.load(f)
        return domande
    except FileNotFoundError:
        st.error("File 'domande.json' non trovato. Assicurati che sia nella stessa cartella.")
        return []
    except json.JSONDecodeError:
        st.error("Errore di formato nel file 'domande.json'. Usa un validatore JSON online per controllare la sintassi (virgole, parentesi, etc.).")
        return []

# --- INIZIALIZZAZIONE DELLO STATO DELLA SESSIONE ---
# Lo stato della sessione permette di mantenere i valori tra le interazioni dell'utente

def inizializza_stato():
    """Inizializza o resetta lo stato della sessione per il quiz."""
    st.session_state.domande_quiz = carica_domande()
    random.shuffle(st.session_state.domande_quiz)
    st.session_state.indice_domanda_corrente = 0
    st.session_state.punteggio = 0
    st.session_state.risposta_sottomessa = False # Nuovo stato per controllare se la risposta è stata data

if 'domande_quiz' not in st.session_state:
    inizializza_stato()

# --- LAYOUT DELL'APP ---
st.title("🧠 Quiz di Preparazione per l'Esame")
st.write("Mettiti alla prova con queste domande generate dalle slide. In bocca al lupo!")
st.divider()

# Controlla se il quiz è terminato
if st.session_state.indice_domanda_corrente >= len(st.session_state.domande_quiz):
    st.success(f"🎉 Quiz Terminato! 🎉")
    st.write(f"Il tuo punteggio finale è: **{st.session_state.punteggio} / {len(st.session_state.domande_quiz)}**")
    
    try:
        percentuale = (st.session_state.punteggio / len(st.session_state.domande_quiz)) * 100
        st.metric(label="Percentuale di correttezza", value=f"{percentuale:.2f}%")

        if percentuale >= 90:
            st.balloons()
            st.info("Ottimo lavoro! Sei prontissimo per l'esame.")
        elif percentuale >= 60:
            st.info("Buon risultato! Continua a esercitarti sugli argomenti che hai sbagliato.")
        else:
            st.warning("Non male, ma puoi migliorare. Fai un altro tentativo!")
            
    except ZeroDivisionError:
        st.warning("Nessuna domanda trovata. Carica il file 'domande.json'.")


    if st.button("Ricomincia Quiz"):
        inizializza_stato()
        st.rerun()

else:
    # Mostra la domanda corrente
    domanda_corrente = st.session_state.domande_quiz[st.session_state.indice_domanda_corrente]
    
    # Mostra la barra di progresso e il punteggio
    progress_bar_value = (st.session_state.indice_domanda_corrente) / len(st.session_state.domande_quiz)
    st.progress(progress_bar_value, text=f"Domanda {st.session_state.indice_domanda_corrente + 1} di {len(st.session_state.domande_quiz)}")
    st.write(f"Punteggio: {st.session_state.punteggio}")
    st.divider()

    st.subheader(f"{st.session_state.indice_domanda_corrente + 1}. {domanda_corrente['domanda']}")

    opzioni = domanda_corrente['opzioni']
    
    # Crea un form per raggruppare i radio button e il pulsante di conferma
    with st.form(key=f"form_domanda_{st.session_state.indice_domanda_corrente}"):
        risposta_utente = st.radio(
            "Seleziona la tua risposta:",
            options=opzioni.keys(),
            format_func=lambda key: f"{key}) {opzioni[key]}",
            key=f"radio_{st.session_state.indice_domanda_corrente}" # Chiave unica per i radio
        )
        submitted = st.form_submit_button("Conferma Risposta")

    # Logica che si attiva DOPO aver premuto "Conferma Risposta"
    if submitted:
        risposta_corretta = domanda_corrente['risposta_corretta']
        
        if risposta_utente == risposta_corretta:
            st.session_state.punteggio += 1
            st.success("✅ Corretto!", icon="✅")
        else:
            st.error(f"❌ Sbagliato! La risposta corretta era: **{risposta_corretta}**) {opzioni[risposta_corretta]}", icon="❌")
        
        st.info(f"**Spiegazione:** {domanda_corrente['spiegazione']}", icon="💡")
        
        # Imposta lo stato a "risposta sottomessa" per mostrare il pulsante "Prossima"
        st.session_state.risposta_sottomessa = True

    # Mostra il pulsante "Prossima Domanda" solo dopo che una risposta è stata confermata
    if st.session_state.risposta_sottomessa:
        if st.button("Prossima Domanda"):
            st.session_state.indice_domanda_corrente += 1
            st.session_state.risposta_sottomessa = False # Resetta per la prossima domanda
            st.rerun()