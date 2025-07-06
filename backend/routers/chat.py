#chat history

from fastapi import APIRouter, Depends, HTTPException
from db_utils import get_db
from models import PatientInDB
from auth_utils import get_current_user
from pydantic import BaseModel
from typing import List
from datetime import datetime
from models import ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/history", response_model=List[ChatMessage])
def get_chat_history(current_user: PatientInDB = Depends(get_current_user), db=Depends(get_db)):
    """Restituisce lo storico della chat per l'utente autenticato"""
    conn, cur = db
    try:
        cur.execute("""
            SELECT id, message, answer, timestamp
            FROM chat
            WHERE patient_id = %s
            ORDER BY timestamp DESC
        """, (current_user.id,))
        rows = cur.fetchall()
        messages = []
        for row in rows:
            d = dict(zip([desc[0] for desc in cur.description], row))
            messages.append(ChatMessage(**d))
        return messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
