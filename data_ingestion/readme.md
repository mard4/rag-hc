# Data Ingestion

## RAG

### Contesto
Ingestione dei Dataset in database (Postgres+PgVector)
## Data
- MedQuAD: dataset di domande e risposte mediche, utile per rispondere a domande dirette basate su informazioni cliniche.
- MIMIC-III: dataset di note cliniche, utile per fornire contesti più dettagliati e specifici su casi reali.

## Struttura
- `create_tables.py`: crea le tabelle necessarie nel database (patients, doctors, appointments, chat)
- `ingest_data_medquad.py`: ingestione del dataset MedQuAD nel database (crea tabella medquad e inserisce i dati)
- `ingest_data_mimic.py`: ingestione del dataset MIMIC-III nel database (crea tabella mimic_notes e inserisce i dati)
- `connection.py`: funzione per connettersi al database  

### Reference
https://huggingface.co/datasets/lavita/MedQuAD

https://physionet.org/content/mimic-iii-question-answer/1.0.0/


# TO-DO: 
- Finire ingest_data_mimic.py
- Vedere se add altre info from medquad/mimic-iii columns


