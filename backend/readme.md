# Backend

## RAG

### Contesto
- Riceve query da utente
- Parte `services/db_service.py`:
    - Genererà l'embedding della query dell'utente
    - Eseguirà una query di similarità vettoriale sulla tabella medquad per trovare le domande/risposte più rilevanti
    - Eseguirà una query di similarità vettoriale sulla tabella mimic_notes per trovare le note cliniche più rilevanti 
    - Combinerà questi due set di risultati.prendendo i top-K (hyperaparameter in `config.py`) risultati dopo averli uniti e ordinati per similarità.
    - Passerà questo contesto combinato all'LLM.

- Parte `services/llm_service.py` LLM per Sintesi Multi-Contesto:
    - LLM riceverà un prompt che include sia le informazioni da MedQuAD (domande/risposte dirette) sia quelle da MIMIC-III (note cliniche più dettagliate/specifiche di casi reali).

## Struttura
- `services/`: Contiene i servizi per interagire con il database e l'LLM.
    - `db_service.py`: Gestisce le operazioni di database, inclusa la generazione di embedding e le query di similarità.
    - `llm_service.py`: Gestisce le interazioni con l'LLM, inclusa la sintesi delle risposte basate sui contesti forniti.

- `config.py`: chiavi API, hyperparametri per la similarità vettoriale.  
- `models.py`: 
- `main.py`:
- `connection.py`: funzione per connettersi al database  


## CRUD - GESTIONE APPUNTAMENTI




# TO-DO: 
- Better prompt, adesso fa un casino della madonna
- API rest per tutte le operazioni di CRUD su pazienti, dottori, appuntamenti, chat
- API to save chat history and stuff
- Ricevuta la risposta, adattarla al contesto e mostrare dottori liberi, appuntamenti

