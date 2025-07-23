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
@st.cache_data
def carica_domande():
    """Carica tutte le domande dal file JSON."""
    try:
        with open('domande.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("File 'domande.json' non trovato. Assicurati che sia nella stessa cartella del progetto su GitHub.")
        return []
    except json.JSONDecodeError:
        st.error("Errore di formato nel file 'domande.json'. Usa un validatore JSON online per controllare la sintassi.")
        return []

# --- INIZIALIZZAZIONE DELLO STATO ---
def inizializza_quiz(num_domande):
    """Prepara una nuova sessione di quiz."""
    st.session_state.quiz_in_progress = True
    tutte_le_domande = carica_domande()
    random.shuffle(tutte_le_domande)
    st.session_state.domande_sessione = tutte_le_domande[:num_domande]
    st.session_state.indice_corrente = 0
    st.session_state.punteggio = 0
    st.session_state.risultati = [None] * len(st.session_state.domande_sessione)

# --- LAYOUT PRINCIPALE ---
st.title("🧠 Quiz di Preparazione per l'Esame")

if 'quiz_in_progress' not in st.session_state:
    st.session_state.quiz_in_progress = False

# --- SCHERMATA DI CONFIGURAZIONE ---
if not st.session_state.quiz_in_progress:
    st.header("Configura la tua sessione di studio")
    tutte_le_domande = carica_domande()
    
    if not tutte_le_domande:
        st.warning("Nessuna domanda caricata. Controlla il file 'domande.json'.")
    else:
        st.write(f"Database completo: **{len(tutte_le_domande)} domande** disponibili.")
        num_selezionate = st.slider(
            "Quante domande vuoi fare?",
            min_value=5, max_value=len(tutte_le_domande), value=20, step=5
        )
        if st.button("🚀 Inizia Quiz!", type="primary", use_container_width=True):
            inizializza_quiz(num_selezionate)
            st.rerun()

# --- GESTIONE DEL QUIZ IN CORSO ---
else:
    indice = st.session_state.indice_corrente
    domande_sessione = st.session_state.domande_sessione

    # --- VISUALIZZAZIONE FINE QUIZ E REVISIONE ---
    if indice >= len(domande_sessione):
        st.success("🎉 Quiz Terminato! 🎉")
        punteggio = st.session_state.punteggio
        totale = len(domande_sessione)
        
        st.write(f"Il tuo punteggio finale è: **{punteggio} / {totale}**")
        
        try:
            percentuale = (punteggio / totale) * 100
            st.metric(label="Percentuale di correttezza", value=f"{percentuale:.2f}%")
            if percentuale >= 90:
                st.balloons()
        except ZeroDivisionError:
            st.warning("Nessuna domanda in questa sessione.")

        st.divider()
        st.header("🔍 Revisione Domande")

        for i, domanda in enumerate(domande_sessione):
            risultato = st.session_state.risultati[i]
            risposta_data = risultato['risposta_data']
            risposta_corretta = domanda['risposta_corretta']
            
            st.subheader(f"Domanda {i+1}: {domanda['domanda']}")
            
            if risultato['corretta']:
                st.success(f"La tua risposta: **{risposta_data}**. Corretta!", icon="✅")
            else:
                st.error(f"La tua risposta: **{risposta_data}**. Sbagliata!", icon="❌")
                st.info(f"Risposta corretta: **{risposta_corretta}**) {domanda['opzioni'][risposta_corretta]}", icon="💡")
            
            with st.expander("Mostra spiegazione"):
                st.write(domanda['spiegazione'])
            st.divider()

        if st.button("↩️ Fai un altro quiz", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()

    # --- VISUALIZZAZIONE DOMANDA CORRENTE ---
    st.progress(indice / len(domande_sessione), text=f"Domanda {indice + 1} di {len(domande_sessione)}")
    st.write(f"Punteggio: {st.session_state.punteggio}")
    st.divider()

    domanda_corrente = domande_sessione[indice]
    st.subheader(f"{indice + 1}. {domanda_corrente['domanda']}")
    opzioni = domanda_corrente['opzioni']
    
    if st.session_state.risultati[indice] is None:
        with st.form(key=f"form_{indice}"):
            risposta_utente = st.radio("Seleziona la tua risposta:", opzioni.keys(), format_func=lambda k: f"{k}) {opzioni[k]}")
            submitted = st.form_submit_button("Conferma Risposta")
        if submitted:
            corretta = (risposta_utente == domanda_corrente['risposta_corretta'])
            if corretta: st.session_state.punteggio += 1
            st.session_state.risultati[indice] = {'risposta_data': risposta_utente, 'corretta': corretta}
            st.rerun()
    else:
        risultato = st.session_state.risultati[indice]
        risposta_data = risultato['risposta_data']
        st.radio("La tua risposta:", opzioni.keys(), format_func=lambda k: f"{k}) {opzioni[k]}", index=list(opzioni.keys()).index(risposta_data), disabled=True)
        
        if risultato['corretta']:
            st.success("✅ Corretto!", icon="✅")
        else:
            risposta_giusta_key = domanda_corrente['risposta_corretta']
            st.error(f"❌ Sbagliato! La risposta corretta era: **{risposta_giusta_key}**) {opzioni[risposta_giusta_key]}", icon="❌")
        
        st.info(f"**Spiegazione:** {domanda_corrente['spiegazione']}", icon="💡")
        
        if st.button("Prossima Domanda ➡️", use_container_width=True):
            st.session_state.indice_corrente += 1
            st.rerun()