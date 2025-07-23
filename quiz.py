import json
import random
import os

# Nome del file JSON con le domande
NOME_FILE_JSON = "domande.json"

def pulisci_schermo():
    """Pulisce la console per una migliore leggibilità."""
    # Per Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Per Mac e Linux
    else:
        _ = os.system('clear')

def avvia_quiz(domande):
    """Funzione principale che gestisce il quiz."""
    punteggio = 0
    # Mescola le domande per renderlo diverso ogni volta
    random.shuffle(domande)
    
    for i, item in enumerate(domande):
        pulisci_schermo()
        print(f"--- Domanda {i + 1} di {len(domande)} ---")
        print(f"\nPunteggio attuale: {punteggio}/{i}\n")
        
        print(item['domanda'])
        print("-" * 20)
        
        # Stampa le opzioni in ordine alfabetico
        opzioni = item['opzioni']
        for chiave, valore in sorted(opzioni.items()):
            print(f"{chiave}) {valore}")
        
        # Chiede la risposta all'utente e la valida
        risposta_utente = ""
        while risposta_utente not in opzioni.keys():
            risposta_utente = input("\nLa tua risposta (A, B, C, D): ").upper()
            if risposta_utente not in opzioni.keys():
                print("Input non valido. Per favore, inserisci A, B, C o D.")

        # Controlla la risposta
        if risposta_utente == item['risposta_corretta']:
            print("\n✅ Corretto!")
            punteggio += 1
        else:
            print(f"\n❌ Sbagliato! La risposta corretta era {item['risposta_corretta']}.")
        
        # Mostra la spiegazione
        print("\n--- Spiegazione ---")
        print(item['spiegazione'])
        print("-" * 20)
        
        input("\nPremi Invio per la prossima domanda...")

    # Fine del quiz
    pulisci_schermo()
    print("--- Quiz Terminato! ---")
    percentuale = (punteggio / len(domande)) * 100 if len(domande) > 0 else 0
    print(f"\nHai risposto correttamente a {punteggio} domande su {len(domande)}.")
    print(f"Percentuale di correttezza: {percentuale:.2f}%")

if __name__ == "__main__":
    try:
        with open(NOME_FILE_JSON, 'r', encoding='utf-8') as f:
            dati_domande = json.load(f)
        avvia_quiz(dati_domande)
    except FileNotFoundError:
        print(f"Errore: Il file '{NOME_FILE_JSON}' non è stato trovato.")
        print("Assicurati di aver creato il file e di averlo messo nella stessa cartella dello script.")
    except json.JSONDecodeError:
        print(f"Errore: Il file '{NOME_FILE_JSON}' non è un JSON valido.")