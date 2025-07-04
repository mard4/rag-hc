## Integrazione con database

import psycopg2
from pgvector.psycopg2 import register_vector
from typing import List, Dict

import config as config
from models import ContextDocument
from connection import *

def retrieve_relevant_data(query_embedding: List[float], top_k: int = config.TOP_K_RESULTS) -> List[ContextDocument]:
    """
    Recupera i dati più rilevanti dalla tabella 'medquad' usando la similarità vettoriale.

    Args:
        query_embedding (List[float]): L'embedding vettoriale della query dell'utente.
        top_k (int): Il numero di record più simili da recuperare.

    Returns:
        List[ContextDocument]: Una lista di oggetti ContextDocument (domanda e risposta) pertinenti.
    """
    conn = None
    try:
        conn, cur = get_connection()  

        # query di similarità vettoriale
        # <-> per la distanza coseno (più piccola = più simile)
        cur.execute(
            "SELECT question, answer FROM medquad ORDER BY question_embedding <-> %s LIMIT %s;",
            (query_embedding, top_k)
        )
        results = cur.fetchall()

        # Formatta i risultati come lista di oggetti ContextDocument
        formatted_results = [ContextDocument(question=q, answer=a) for q, a in results]
        return formatted_results

    except Exception as e:
        print(f"Errore nel recupero dati dal database: {e}")
        return [] 
    finally:
        if conn:
            conn.close() 