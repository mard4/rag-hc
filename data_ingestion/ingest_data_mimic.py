import os
import pandas as pd
from connection import *
from sentence_transformers import SentenceTransformer

conn, cur = get_connection()

print("---------------------------------- \n Starting data ingestion for MIMIC-III...")

def read_json_mimic():
    extracted_data = []

    filepath = "./data/mimic.json"
    with open(filepath, 'r', encoding='utf-8') as file:
        data = pd.read_json(file)
        
    for record in data['data']:
        title = record['title']
        paragraphs = record['paragraphs']

        for paragraph in paragraphs:
            context = paragraph.get('context')
            questions = paragraph['qas']
            for question in questions:
                question_text = question['question']
                answers = question['answers']
                for answer in answers:
                    answer_text = answer['text']
                    #print(f"Context: {context}")
                    extracted_data.append({
                        'context': context,
                        'question': question_text,
                        'answer': answer_text
                    })
    ##df = pd.DataFrame(extracted_data)
    return extracted_data #df

data = read_json_mimic()

## Embedding model
model = "all-MiniLM-L6-v2"
model = SentenceTransformer(model)
print(f"Loaded embedding model {model}")

conn, cur = get_connection()

# Creazione della tabella
# dimensione del vettore == dimensione dell'output del modello di embedding.
# all-MiniLM-L6-v2 produce vettori di dimensione 384
vector_dimension = model.get_sentence_embedding_dimension()
##print(f"Dimensione del vettore attesa: {vector_dimension}")

cur.execute(f"""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS mimic (
        id SERIAL PRIMARY KEY,
        context TEXT,
        question TEXT,
        answer TEXT,
        
        question_embedding vector({vector_dimension})
    );
""")
conn.commit()
print("Table mimic created successfully.")

def data_ingestion(data, cur, conn):
    """Data ingestion con batch"""
    print("Inizio dell'ingestione dei dati...")
    batch_size = 1000
    processed_count = 0

    df = pd.DataFrame(data)
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]

        questions = batch_df['question'].tolist()
        answers = batch_df['answer'].tolist()
        ##titles = batch_df['title'].tolist()
        contexts = batch_df['context'].tolist()

        # aggiunta context to questions
        texts_to_embed = contexts

        # embeddings per le domande nel batch
        question_embeddings = model.encode(texts_to_embed).tolist()

        # valori per l'inserimento batch
        values = []
        for c,q,a, q_emb in zip(contexts, questions, answers, question_embeddings):
            values.append((c,q, a, q_emb))

        try:
            cur.executemany(
                "INSERT INTO mimic (context, question, answer, question_embedding) VALUES ( %s, %s, %s, %s)",
                values
            )
            conn.commit()
            processed_count += len(batch_df) 
            print(f"Inseriti {processed_count}/{len(df)} record.")
        except Exception as e:
            conn.rollback()
            print(f"Errore durante l'inserimento batch {i}-{i+batch_size}: {e}")
            break

    print("Ingestione dei dati mimic completata.")

data_ingestion(data, cur, conn)

cur.close()
conn.close()
print("Connection closed for mimic")

