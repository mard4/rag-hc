#CRUD per bookings

from fastapi import APIRouter, Depends, HTTPException, status
from db_utils import get_db
from models import BookingCreate, BookingOut  
from auth_utils import get_current_user
from models import PatientInDB
from typing import List

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/me", response_model=List[BookingOut])
def get_my_appointments(current_user: PatientInDB = Depends(get_current_user), db=Depends(get_db)):
    conn, cur = db
    try:
        cur.execute("SELECT * FROM bookings WHERE patient_id = %s", (current_user.id,))
        rows = cur.fetchall()
        appointments = []

        for row in rows:
            d = dict(zip([desc[0] for desc in cur.description], row))
            appointments.append(BookingOut(**d))
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()



