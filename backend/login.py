# login.py
from fastapi import APIRouter, HTTPException, status, Depends
from models import UserBase, UserCreate, UserLogin, Token, PatientInDB 
from db_utils import get_db
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime, timedelta 

from auth_utils import (
    get_current_user,
    create_access_token,
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    oauth2_scheme 
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# --- Funzioni di Utilità per Hashing 
def get_password_hash(password: str) -> str:
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- Endpoint di Autenticazione

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_patient(user: UserCreate, db_conn_cur: tuple = Depends(get_db)):
    conn, cur = db_conn_cur
    try:
        # Controlla se l'email è già registrata
        cur.execute("SELECT id FROM patients WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already present in the database."
            )

        # Controlla se il numero di telefono è già registrato (se è UNIQUE)
        cur.execute("SELECT id FROM patients WHERE phone_number = %s", (user.phone_number,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Telephone number already present in the database."
            )

        hashed_password = get_password_hash(user.password)

        # DEBUG: Stampa i dati che stai cercando di inserire
        print(f"Registering: Name={user.name}, Surname={user.surname}, Sex={user.sex}, BirthDate={user.birth_date}, Address={user.address}, PhoneNumber={user.phone_number}, Email={user.email}")


        # Aggiorna la query INSERT per includere tutti i campi e rimuovere la virgola extra
        cur.execute(
            """INSERT INTO patients (name, surname, sex, birth_date, address, phone_number, email, password_hash)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;""",
            (user.name, user.surname, user.sex, user.birth_date, user.address, user.phone_number, user.email, hashed_password)
        )
        patient_id = cur.fetchone()[0]
        conn.commit()

        return {"message": "Registered! ", "user_id": patient_id}
    except HTTPException:
        conn.rollback() # Esegui il rollback anche per le HTTPException
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error during registration: {e}") # Debug print
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore interno del server durante la registrazione: {e}")

@router.post("/login", response_model=Token)
async def login_for_access_token(user_credentials: UserLogin, db_conn_cur: tuple = Depends(get_db)):
    conn, cur = db_conn_cur
    try:
        # Recupera tutti i campi necessari dal DB per la verifica e la creazione del token
        cur.execute(
            """SELECT id, email, password_hash, name, surname, sex, birth_date, address, phone_number
               FROM patients WHERE email = %s;""", (user_credentials.email,)
        )
        db_patient = cur.fetchone()

        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password not valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        patient_id, email, password_hash, name, surname, sex, birth_date, address, phone_number = db_patient

        if not verify_password(user_credentials.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password not valid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
        
        access_token = create_access_token(
            data={"sub": email, "id": patient_id, "name": name, "surname": surname},
            expires_delta=access_token_expires
        )
        
        # la risposta del login
        user_info = UserBase(email=email, name=name, surname=surname)
        
        return Token(access_token=access_token, token_type="bearer", user=user_info)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in Login: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal error during login: {e}")


@router.get("/patients/me", response_model=UserBase)
async def read_current_patient(current_patient: PatientInDB = Depends(get_current_user)):
    # ritorna solo le info base UserBase
    return UserBase(email=current_patient.email, name=current_patient.name, surname=current_patient.surname)

# endpoint che ritorna TUTTI i dettagli del paziente
@router.get("/patients/details", response_model=PatientInDB)
async def read_patient_details(current_patient: PatientInDB = Depends(get_current_user)):
    return current_patient