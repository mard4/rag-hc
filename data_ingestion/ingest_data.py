from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector
import os

ds = load_dataset("lavita/MedQuAD")
data = ds['train']
print(f"# data in MedQuAD: {len(data)}")

## Embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Modello di embedding caricato.")

## Postgres
print("Connessione al database PostgreSQL...")
try:
    conn = psycopg2.connect(
        dbname="medquad_db",
        user="user",
        password="password",
        host="db", # O il nome del servizio Docker 'db' se lo script gira in un altro container
        port="5432"
    )
    register_vector(conn) # Registra il tipo VECTOR per psycopg2
    cur = conn.cursor()
    print("Connessione al database riuscita.")
except Exception as e:
    print(f"Errore di connessione al database: {e}")
    exit()

# Creazione della tabella
# dimensione del vettore == dimensione dell'output del modello di embedding.
# all-MiniLM-L6-v2 produce vettori di dimensione 384
vector_dimension = model.get_sentence_embedding_dimension()
print(f"Dimensione del vettore attesa: {vector_dimension}")

cur.execute(f"""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS medquad (
        id SERIAL PRIMARY KEY,
        question TEXT,
        answer TEXT,
        
        question_embedding vector({vector_dimension})
    );
""")
conn.commit()
print("Tabella 'medquad' creata o già esistente.")

# Inserimento dei dati
def data_ingestion(data, cur, conn):
    """Data ingestion con batch"""
    print("Inizio dell'ingestione dei dati...")
    batch_size = 1000
    processed_count = 0

    df = data.to_pandas()
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]

        questions = batch_df['question'].tolist()
        answers = batch_df['answer'].tolist()

        # embeddings per le domande nel batch
        question_embeddings = model.encode(questions).tolist()

        # valori per l'inserimento batch
        values = []
        for q, a, q_emb in zip(questions, answers, question_embeddings):
            values.append((q, a, q_emb))

        try:
            cur.executemany(
                "INSERT INTO medquad (question, answer, question_embedding) VALUES (%s, %s, %s)",
                values
            )
            conn.commit()
            processed_count += len(batch_df) 
            print(f"Inseriti {processed_count}/{len(df)} record.")
        except Exception as e:
            conn.rollback()
            print(f"Errore durante l'inserimento batch {i}-{i+batch_size}: {e}")
            break

    print("Ingestione dei dati completata.")

cur.close()
conn.close()
print("Connessione al database chiusa.")