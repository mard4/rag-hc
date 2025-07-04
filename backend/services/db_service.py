## Integrazione con database
import psycopg2
from pgvector.psycopg2 import register_vector
from typing import List, Dict, Tuple

import config as config
from models import ContextDocument
from connection import *

def retrieve_relevant_data(query_embedding: List[float], top_k: int = config.TOP_K_RESULTS) -> List[ContextDocument]:
    """
    Recupera i dati più rilevanti sia dalla tabella 'medquad' che da 'mimic'
    usando la similarità vettoriale e combinando i risultati.
    """
    conn = None
    all_relevant_docs_with_distance = []

    try:
        conn, cur = get_connection()  

        # --- QUERY PER LA TABELLA MEDQUAD ---
        # Recupera question, answer e la distanza per ordinare
        # Per medquad, title e context saranno None o stringhe vuote
        cur.execute(
            "SELECT question, answer, question_embedding <-> %s::vector AS distance FROM medquad ORDER BY distance LIMIT %s;",
            (query_embedding, top_k)
        )
        medquad_results: List[Tuple[str, str, float]] = cur.fetchall() # (question, answer, distance)

        for q, a, dist in medquad_results:
            all_relevant_docs_with_distance.append({
                "distance": dist,
                "document": ContextDocument(question=q, answer=a) # context saranno None per default
            })

        # --- QUERY PER LA TABELLA MIMIC ---
        # Recupera title, context, question, answer e la distanza
        cur.execute(
            "SELECT context, question, answer, question_embedding <-> %s::vector AS distance FROM mimic ORDER BY distance LIMIT %s;",
            (query_embedding, top_k)
        )
        mimic_results: List[Tuple[str, str, str, float]] = cur.fetchall() # (title, context, question, answer, distance)
        
        for c, q, a, dist in mimic_results:
            all_relevant_docs_with_distance.append({
                "distance": dist,
                "document": ContextDocument(context=c, question=q, answer=a)
            })

        ## combina results
        all_relevant_docs_with_distance.sort(key=lambda x: x["distance"])
        final_rel_docs= [item["document"] for item in all_relevant_docs_with_distance[:top_k]]

        print(f"[{__name__}] Recuperati {len(final_rel_docs)} documenti totali dal Medquad+MIMIC.")
        
        return final_rel_docs


    except Exception as e:
        print(f"Errore nel recupero dati dal database: {e}")
        return [] 
    finally:
        if conn:
            conn.close()