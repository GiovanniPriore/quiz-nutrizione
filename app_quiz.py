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

# --- INIZIALIZZAZIONE DELLO STATO DELLA SESSIONE ---
# Lo stato della sessione permette di mantenere i valori tra le interazioni dell'utente
if 'domande' not in st.session_state:
    st.session_state.domande = carica_domande()
    # Mescola le domande solo all'inizio della sessione
    random.shuffle(st.session_state.domande)

if 'indice_domanda_corrente' not in st.session_state:
    st.session_state.indice_domanda_corrente = 0

if 'punteggio' not in st.session_state:
    st.session_state.punteggio = 0

if 'risposta_data' not in st.session_state:
    st.session_state.risposta_data = None


# --- LAYOUT DELL'APP ---
st.title("🧠 Quiz di Preparazione per l'Esame")
st.write("Mettiti alla prova con queste domande generate dalle slide. In bocca al lupo!")

# Controlla se il quiz è terminato
if st.session_state.indice_domanda_corrente >= len(st.session_state.domande):
    st.success(f"🎉 Quiz Terminato! 🎉")
    st.write(f"Il tuo punteggio finale è: **{st.session_state.punteggio} / {len(st.session_state.domande)}**")
    
    percentuale = (st.session_state.punteggio / len(st.session_state.domande)) * 100
    st.metric(label="Percentuale di correttezza", value=f"{percentuale:.2f}%")

    if st.button("Ricomincia Quiz"):
        # Resetta lo stato per un nuovo quiz
        st.session_state.indice_domanda_corrente = 0
        st.session_state.punteggio = 0
        st.session_state.risposta_data = None
        random.shuffle(st.session_state.domande)
        st.rerun() # Ricarica l'app
else:
    # Mostra la domanda corrente
    domanda_corrente = st.session_state.domande[st.session_state.indice_domanda_corrente]
    
    # Mostra la barra di progresso
    progress_bar_value = (st.session_state.indice_domanda_corrente) / len(st.session_state.domande)
    st.progress(progress_bar_value, text=f"Domanda {st.session_state.indice_domanda_corrente + 1} di {len(st.session_state.domande)}")

    st.subheader(domanda_corrente['domanda'])

    # Crea i pulsanti per le opzioni
    opzioni = domanda_corrente['opzioni']
    # Estrai e mescola le chiavi per randomizzare la posizione delle risposte
    chiavi_opzioni = list(opzioni.keys())
    random.shuffle(chiavi_opzioni)
    
    risposta_selezionata = st.radio(
        "Seleziona la tua risposta:",
        options=chiavi_opzioni,
        format_func=lambda key: f"{key}) {opzioni[key]}",
        index=None # Nessuna opzione preselezionata
    )

    if st.button("Conferma Risposta", disabled=(risposta_selezionata is None)):
        st.session_state.risposta_data = risposta_selezionata
        
        # Controlla la risposta e aggiorna il punteggio
        if st.session_state.risposta_data == domanda_corrente['risposta_corretta']:
            st.session_state.punteggio += 1
            st.success("✅ Risposta Corretta!", icon="✅")
        else:
            st.error(f"❌ Risposta Sbagliata! La risposta corretta era: {domanda_corrente['risposta_corretta']}", icon="❌")

        # Mostra la spiegazione
        st.info(f"**Spiegazione:** {domanda_corrente['spiegazione']}", icon="💡")

        # Prepara per la prossima domanda
        st.session_state.indice_domanda_corrente += 1

        if st.session_state.indice_domanda_corrente < len(st.session_state.domande):
             if st.button("Prossima Domanda"):
                 st.session_state.risposta_data = None # Resetta per la prossima domanda
                 st.rerun()
        else: # Se era l'ultima domanda
            if st.button("Vedi Risultato Finale"):
                 st.rerun()