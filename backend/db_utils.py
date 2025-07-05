from fastapi import HTTPException, status
from connection import *
import os

# --- Database Connection Dependency for FastAPI ---
def get_db():
    """
    Dipendenza FastAPI per ottenere una connessione al database.
    Assicura che la connessione e il cursore siano chiusi dopo la richiesta.
    """
    conn = None
    cur = None
    try:
        conn, cur = get_connection()
        #cur = conn.cursor()
        yield conn, cur
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
