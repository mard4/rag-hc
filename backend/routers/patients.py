#CRUD per ottenree tutti i patients
from fastapi import APIRouter, Depends, HTTPException
from db_utils import get_db
from models import PatientInDB
from auth_utils import get_current_user
from typing import List
from pydantic import BaseModel
from datetime import datetime
from models import PatientOut

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[PatientOut])
def list_patients(db=Depends(get_db)):
    """Restituisce la lista di tutti i pazienti"""
    conn, cur = db
    try:
        cur.execute("""
            SELECT id, name, surname, sex, birth_date, address, phone_number, email, created_at  
            FROM patients
            ORDER BY rating DESC
        """)
        rows = cur.fetchall()
        return [PatientOut(**dict(zip([desc[0] for desc in cur.description], row))) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# @router.get("/{patient_id}/bookings", response_model=BookingsSlot)
# def get_patient_bookings(patient_id: int, db=Depends(get_db)):
#     """TODO """
#     from datetime import datetime, timedelta
#     conn, cur = db
#     try:
#         return BookingsSlot(patient_id=patient_id, available_slots=slots)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         conn.close()
