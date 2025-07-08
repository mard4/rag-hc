from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from db_utils import get_db
from auth_utils import get_current_user
from models import PatientInDB, BookingIn, BookingOut, DoctorOut 

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("/me", response_model=List[BookingOut])
def get_my_bookings(current_user: PatientInDB = Depends(get_current_user), db=Depends(get_db)):
    conn, cur = db
    try:
        cur.execute(
            """
            SELECT 
                b.id, 
                b.patient_id, 
                b.doctor_id, 
                d.name AS doctor_name,  -- Alias for doctor's name
                d.surname AS doctor_surname, -- Alias for doctor's surname
                b.appointment_date, 
                b.reason_for_visit, 
                b.status, 
                b.created_at 
            FROM bookings AS b
            JOIN doctors AS d ON b.doctor_id = d.id
            WHERE b.patient_id = %s
            ORDER BY b.appointment_date DESC; -- Order by date for better display
            """,
            (current_user.id,)
        )
        rows = cur.fetchall()
        bookings = []

        # Map results to BookingOut model
        column_names = [desc[0] for desc in cur.description]
        for row in rows:
            d = dict(zip(column_names, row))
            bookings.append(BookingOut(**d))
        return bookings
    except Exception as e:
        print(f"Error fetching bookings: {e}") 
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

# Prenotazione di un appuntamento
@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    booking_data: BookingIn, 
    current_user: PatientInDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Crea una nuova prenotazione per l'utente autenticato.
    """
    conn, cur = db
    try:
        # Check if the doctor_id exists 
        cur.execute("SELECT id, name, surname FROM doctors WHERE id = %s", (booking_data.doctor_id,))
        doctor_info = cur.fetchone()
        if not doctor_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
        
        doctor_name, doctor_surname = doctor_info[1], doctor_info[2]


        # Insert the new booking into the bookings table
        # Note: The bookings table should only store doctor_id, not doctor_name/surname
        cur.execute(
            """
            INSERT INTO bookings (patient_id, doctor_id, appointment_date, reason_for_visit, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, patient_id, doctor_id, appointment_date, reason_for_visit, status, created_at;
            """,
            (
                current_user.id,
                booking_data.doctor_id,
                booking_data.appointment_date,
                booking_data.reason_for_visit,
                'scheduled' # Default status
            )
        )
        conn.commit()
        
        # Retrieve the newly inserted row for returning as BookingOut
        new_booking_row = cur.fetchone()
        if new_booking_row:
            new_booking_dict = dict(zip([desc[0] for desc in cur.description], new_booking_row))
            # Add doctor name and surname to the booking output
            new_booking_dict['doctor_name'] = doctor_name
            new_booking_dict['doctor_surname'] = doctor_surname
            
            return BookingOut(**new_booking_dict)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve created booking")

    except HTTPException as http_exc: 
        conn.rollback()
        raise http_exc
    except Exception as e:
        conn.rollback()
        print(f"Error creating appointment: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
    finally:
        conn.close()