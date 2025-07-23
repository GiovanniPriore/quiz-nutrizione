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
    """Carica tutte le domande dal file JSON."""
    try:
        with open('domande.json', 'r', encoding='utf-8') as f:
            domande = json.load(f)
        return domande
    except FileNotFoundError:
        st.error("File 'domande.json' non trovato. Assicurati che sia nella stessa cartella del progetto su GitHub.")
        return []
    except json.JSONDecodeError:
        st.error("Errore di formato nel file 'domande.json'. Usa un validatore JSON online per controllare la sintassi.")
        return []

# --- INIZIALIZZAZIONE DELLO STATO DELLA SESSIONE ---
if 'quiz_in_progress' not in st.session_state:
    st.session_state.quiz_in_progress = False

tutte_le_domande = carica_domande()

# --- INTERFACCIA UTENTE ---
st.title("🧠 Quiz di Preparazione per l'Esame")

# --- SCHERMATA DI CONFIGURAZIONE (se il quiz non è in corso) ---
if not st.session_state.quiz_in_progress:
    st.header("Configura la tua sessione di studio")
    
    if not tutte_le_domande:
        st.warning("Nessuna domanda caricata. Controlla il file 'domande.json'.")
    else:
        st.write(f"Database completo: **{len(tutte_le_domande)} domande** disponibili.")
        
        num_domande_selezionate = st.slider(
            "Quante domande vuoi fare in questa sessione?",
            min_value=5, 
            max_value=len(tutte_le_domande),
            value=20,
            step=5
        )

        if st.button("🚀 Inizia Quiz!", type="primary", use_container_width=True):
            st.session_state.quiz_in_progress = True
            random.shuffle(tutte_le_domande)
            st.session_state.domande_del_quiz_corrente = tutte_le_domande[:num_domande_selezionate]
            st.session_state.indice_domanda_corrente = 0
            st.session_state.punteggio = 0
            st.session_state.risposta_sottomessa = False
            st.rerun()

# --- SCHERMATA DEL QUIZ (se il quiz è in corso) ---
else:
    # Controlla se il quiz è terminato
    if st.session_state.indice_domanda_corrente >= len(st.session_state.domande_del_quiz_corrente):
        st.success("🎉 Quiz Terminato! 🎉")
        
        num_domande_fatte = len(st.session_state.domande_del_quiz_corrente)
        punteggio_finale = st.session_state.punteggio
        
        st.write(f"Il tuo punteggio finale è: **{punteggio_finale} / {num_domande_fatte}**")
        
        try:
            percentuale = (punteggio_finale / num_domande_fatte) * 100
            st.metric(label="Percentuale di correttezza", value=f"{percentuale:.2f}%")

            if percentuale >= 90:
                st.balloons()
                st.info("Ottimo lavoro! Sei prontissimo per l'esame.")
            elif percentuale >= 60:
                st.info("Buon risultato! Continua a esercitarti sugli argomenti che hai sbagliato.")
            else:
                st.warning("Non male, ma puoi migliorare. Fai un altro tentativo!")
        except ZeroDivisionError:
            st.warning("Nessuna domanda in questa sessione.")

        if st.button("↩️ Torna alla Schermata Iniziale", use_container_width=True):
            st.session_state.quiz_in_progress = False
            # Pulisce lo stato del quiz precedente per sicurezza
            for key in ['domande_del_quiz_corrente', 'indice_domanda_corrente', 'punteggio', 'risposta_sottomessa']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    else:
        domanda_corrente = st.session_state.domande_del_quiz_corrente[st.session_state.indice_domanda_corrente]
        
        progress_bar_value = (st.session_state.indice_domanda_corrente) / len(st.session_state.domande_del_quiz_corrente)
        st.progress(progress_bar_value, text=f"Domanda {st.session_state.indice_domanda_corrente + 1} di {len(st.session_state.domande_del_quiz_corrente)}")
        st.write(f"Punteggio: {st.session_state.punteggio}")
        st.divider()

        st.subheader(f"{st.session_state.indice_domanda_corrente + 1}. {domanda_corrente['domanda']}")

        opzioni = domanda_corrente['opzioni']
        
        # Se la risposta non è ancora stata sottomessa, mostra il form
        if not st.session_state.risposta_sottomessa:
            with st.form(key=f"form_domanda_{st.session_state.indice_domanda_corrente}"):
                risposta_utente = st.radio(
                    "Seleziona la tua risposta:",
                    options=opzioni.keys(),
                    format_func=lambda key: f"{key}) {opzioni[key]}",
                    key=f"radio_{st.session_state.indice_domanda_corrente}"
                )
                submitted = st.form_submit_button("Conferma Risposta")

            if submitted:
                st.session_state.risposta_sottomessa = True
                st.session_state.risposta_utente = risposta_utente
                st.rerun()
        
        # Se la risposta è stata sottomessa, mostra il risultato e il pulsante "Prossima"
        else:
            risposta_corretta = domanda_corrente['risposta_corretta']
            risposta_utente = st.session_state.risposta_utente

            # Mostra di nuovo la domanda e le opzioni, ma disabilitate
            st.radio(
                "La tua risposta:",
                options=opzioni.keys(),
                format_func=lambda key: f"{key}) {opzioni[key]}",
                index=list(opzioni.keys()).index(risposta_utente), # Mostra la selezione dell'utente
                disabled=True
            )

            if risposta_utente == risposta_corretta:
                st.session_state.punteggio += 1 # Aumenta il punteggio solo la prima volta che viene visualizzato
                st.success("✅ Corretto!", icon="✅")
            else:
                st.error(f"❌ Sbagliato! La risposta corretta era: **{risposta_corretta}**) {opzioni[risposta_corretta]}", icon="❌")
            
            st.info(f"**Spiegazione:** {domanda_corrente['spiegazione']}", icon="💡")
            
            # Azzera il flag del punteggio per evitare di contarlo più volte
            st.session_state.risposta_utente = None 
            
            if st.button("Prossima Domanda ➡️", use_container_width=True):
                st.session_state.indice_domanda_corrente += 1
                st.session_state.risposta_sottomessa = False
                st.rerun()