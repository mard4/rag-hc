#CRUD per doctors

from fastapi import APIRouter, Depends, HTTPException
from db_utils import get_db
from models import PatientInDB
from auth_utils import get_current_user
from typing import List
from pydantic import BaseModel
from datetime import datetime
from models import DoctorOut, AvailabilitySlot

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/", response_model=List[DoctorOut])
def list_doctors(db=Depends(get_db)):
    """Restituisce la lista di tutti i medici"""
    conn, cur = db
    try:
        cur.execute("""
            SELECT id, name, surname, specialization, rating FROM doctors
            ORDER BY rating DESC
        """)
        rows = cur.fetchall()
        return [DoctorOut(**dict(zip([desc[0] for desc in cur.description], row))) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/{doctor_id}/availability", response_model=AvailabilitySlot)
def get_doctor_availability(doctor_id: int, db=Depends(get_db)):
    """TO DO EDIT 
    Restituisce slot fittizi di disponibilità di un medico"""
    from datetime import datetime, timedelta
    conn, cur = db
    try:
        
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        slots = [now + timedelta(days=i, hours=9) for i in range(1, 6)]  
        return AvailabilitySlot(doctor_id=doctor_id, available_slots=slots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
