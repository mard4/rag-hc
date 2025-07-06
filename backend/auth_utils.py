from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import os 
from datetime import datetime, timedelta 

from models import PatientInDB, UserBase 
from db_utils import get_db 


SECRET_KEY = "fsdiojfosjfdosifjd_default_fallback_key_"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    user_id: int
    role: str

# --- Funzione per creare il token di accesso ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dipendenza per ottenere l'utente corrente da un token JWT ---
async def get_current_user(token: str = Depends(oauth2_scheme), db_conn_cur: tuple = Depends(get_db)) -> PatientInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        patient_id: int = payload.get("id") 
        email: str = payload.get("sub")   
        # user_name: str = payload.get("name")
        # user_surname: str = payload.get("surname")  

        if patient_id is None or not isinstance(patient_id, int) or email is None:
            raise credentials_exception
        
    except (JWTError, ValueError): # Cattura JWTError per problemi di token e ValueError se int() fallisce
        raise credentials_exception
    
    conn, cur = db_conn_cur 
    try:
        # Recupera tutti i dettagli del paziente dal DB usando l'ID numerico dal token
        cur.execute(
            """SELECT id, name, surname, sex, birth_date, address, phone_number, email, password_hash
               FROM patients WHERE id = %s;""", (patient_id,) 
        )
        patient_data = cur.fetchone()

        if patient_data is None:
            raise credentials_exception # Token valido, ma l'ID paziente non corrisponde a un utente esistente
        
        # Mappa i dati recuperati dal DB al modello PatientInDB
        current_patient = PatientInDB(
            id=patient_data[0],
            name=patient_data[1],
            surname=patient_data[2],
            sex=patient_data[3],
            birth_date=patient_data[4],
            address=patient_data[5],
            phone_number=patient_data[6],
            email=patient_data[7],
            password_hash=patient_data[8]
        )
        return current_patient
    except Exception as e:
        print(f"Errore nel recupero utente corrente dal DB: {e}")
        # Solleva un errore 500 per problemi di database o altro non direttamente legati al token JWT
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno del server durante il recupero dettagli utente: {e}"
        )

