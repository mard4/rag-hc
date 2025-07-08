## Integrazione con database
import psycopg2
from pgvector.psycopg2 import register_vector
from typing import List, Dict, Tuple

import config as config
from models import ContextDocument
from connection import *

from typing import List
from db_utils import get_connection
from models import ContextDocument

def retrieve_relevant_data(
    patient_id: int,
    query_embedding: List[float],
    top_k: int = config.TOP_K_RESULTS,
    chat_k: int = config.CHAT_HISTORY_LIMIT
) -> List[ContextDocument]:
    """
    Recupera:
      1) i top_k documenti più simili da medquad (solo Q/A),
      2) i top_k documenti più simili da mimic (context/Q/A),
      3) gli ultimi chat_k messaggi dallo storico chat per il paziente.
    Ritorna una lista di ContextDocument da usare come contesto RAG.
    """
    conn = None
    all_relevant_docs = []

    try:
        conn, cur = get_connection()

        # --- 1) MedQuAD ---
        cur.execute(
            """
            SELECT question, answer, question_embedding <-> %s::vector AS distance
            FROM medquad
            ORDER BY distance
            LIMIT %s;
            """,
            (query_embedding, top_k)
        )
        for question, answer, _ in cur.fetchall():
            all_relevant_docs.append(ContextDocument(question=question, answer=answer))

        # --- 2) MIMIC ---
        cur.execute(
            """
            SELECT context, question, answer, question_embedding <-> %s::vector AS distance
            FROM mimic
            ORDER BY distance
            LIMIT %s;
            """,
            (query_embedding, top_k)
        )
        for context, question, answer, _ in cur.fetchall():
            all_relevant_docs.append(ContextDocument(context=context, question=question, answer=answer))

        # --- 3) Cronologia chat ---
        cur.execute(
            """
            SELECT COUNT(*) FROM chat
            WHERE patient_id = %s;
            """,
            (patient_id,)
        )
        total_chat_messages = cur.fetchone()[0]
        print(f"[DEBUG] Total chat messages for patient {patient_id}: {total_chat_messages}")

        if total_chat_messages >= config.MIN_TOTAL_CHAT_MESSAGES_FOR_HISTORY and config.CHAT_HISTORY_LIMIT > 0:
            cur.execute(
                """
                SELECT message, answer
                FROM chat
                WHERE patient_id = %s
                ORDER BY timestamp DESC
                LIMIT %s;
                """,
                (patient_id, chat_k)
            )
            for message, answer in cur.fetchall():
                all_relevant_docs.append(ContextDocument(question=message, answer=answer))
        else:
            print(f"[DEBUG] Chat history not included: total messages ({total_chat_messages}) below threshold ({config.MIN_TOTAL_CHAT_MESSAGES_FOR_HISTORY}) or CHAT_HISTORY_LIMIT is 0.")


        print(f"[{__name__}] Got {len(all_relevant_docs)} documents (medquad+mimic+chat).")
        return all_relevant_docs

    finally:
        if conn:
            conn.close()
