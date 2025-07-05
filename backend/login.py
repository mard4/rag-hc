from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
import os

# Importa i modelli Pydantic aggiornati
from models import UserBase, UserCreate, UserLogin, Token, TokenData, PatientInDB # Assicurati che PatientInDB sia importato

# Importa le utility per DB e hashing/JWT
from db_utils import get_db
from bcrypt import hashpw, gensalt, checkpw
from jose import JWTError, jwt
from dotenv import load_dotenv

# Carica le variabili d'ambiente all'avvio del modulo (meglio riabilitarlo)
load_dotenv()

# --- Configurazione JWT ---
# Recupera la SECRET_KEY dalle variabili d'ambiente in modo più sicuro
SECRET_KEY = os.getenv("SECRET_KEY", "fsdiojfosjfdosifjd_default_fallback_key_") # Aggiungi un fallback per sviluppo
if SECRET_KEY == "fsdiojfosjfdosifjd_default_fallback_key_":
    print("WARNING: Using default fallback SECRET_KEY. Please set SECRET_KEY in your .env file for production.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# --- Funzioni di Utilità per Hashing e JWT ---
def get_password_hash(password: str) -> str:
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

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
async def get_current_user(token: str = Depends(oauth2_scheme), db_conn_cur: tuple = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Assicurati che questi campi siano nel payload quando crei il token
        email: str = payload.get("sub")
        patient_id: int = payload.get("id")
        
        # Recupera altri campi dal payload se li hai inclusi, altrimenti potresti recuperarli dal DB
        user_name: str = payload.get("name")
        user_surname: str = payload.get("surname")

        if email is None or patient_id is None:
            raise credentials_exception
        
        # Non è necessario creare TokenData se si recupera direttamente dal DB
        # token_data = TokenData(email=email, id=patient_id, name=user_name, surname=user_surname)

    except JWTError:
        raise credentials_exception
    
    conn, cur = db_conn_cur
    try:
        # Recupera tutti i dettagli del paziente dal DB usando l'ID dal token
        cur.execute(
            """SELECT id, name, surname, sex, birth_date, address, phone_number, email, password_hash
               FROM patients WHERE id = %s;""", (patient_id,)
        )
        patient_data = cur.fetchone()

        if patient_data is None:
            raise credentials_exception # Utente non trovato nel DB
        
        # Mappa i dati recuperati dal DB al modello PatientInDB
        # Assicurati che l'ordine dei campi corrisponda alla query SQL
        current_patient = PatientInDB(
            id=patient_data[0],
            name=patient_data[1],
            surname=patient_data[2],
            sex=patient_data[3],
            birth_date=patient_data[4], # Sarà un oggetto date
            address=patient_data[5],
            phone_number=patient_data[6],
            email=patient_data[7],
            password_hash=patient_data[8]
        )
        return current_patient
    except JWTError:
        # Mantieni la gestione specifica per errori JWT
        raise credentials_exception
    except Exception as e:
        print(f"Errore nel recupero utente corrente dal DB: {e}")
        # Solleva un errore 500 per problemi di database o altro
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching user: {e}"
        )
    
    
# --- Endpoint di Autenticazione ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_patient(user: UserCreate, db_conn_cur: tuple = Depends(get_db)):
    conn, cur = db_conn_cur
    try:
        # Controlla se l'email è già registrata
        cur.execute("SELECT id FROM patients WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email già registrata."
            )

        # Controlla se il numero di telefono è già registrato (se è UNIQUE)
        cur.execute("SELECT id FROM patients WHERE phone_number = %s", (user.phone_number,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Numero di telefono già registrato."
            )

        hashed_password = get_password_hash(user.password)

        # DEBUG: Stampa i dati che stai cercando di inserire
        print(f"Tentativo di inserimento: Name={user.name}, Surname={user.surname}, Sex={user.sex}, BirthDate={user.birth_date}, Address={user.address}, PhoneNumber={user.phone_number}, Email={user.email}")


        # Aggiorna la query INSERT per includere tutti i campi e rimuovere la virgola extra
        cur.execute(
            """INSERT INTO patients (name, surname, sex, birth_date, address, phone_number, email, password_hash)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;""",
            (user.name, user.surname, user.sex, user.birth_date, user.address, user.phone_number, user.email, hashed_password)
        )
        patient_id = cur.fetchone()[0]
        conn.commit()

        return {"message": "Registrazione avvenuta con successo!", "user_id": patient_id}
    except HTTPException:
        conn.rollback() # Esegui il rollback anche per le HTTPException
        raise
    except Exception as e:
        conn.rollback()
        print(f"Errore grave durante la registrazione: {e}") # Debug print
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
                detail="Email o password non valide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        patient_id, email, password_hash, name, surname, sex, birth_date, address, phone_number = db_patient

        if not verify_password(user_credentials.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o password non valide",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            # Includi tutti i dati che vuoi nel token JWT (ID, email, nome, cognome)
            data={"sub": email, "id": patient_id, "name": name, "surname": surname},
            expires_delta=access_token_expires
        )
        
        # Crea l'oggetto UserBase per la risposta del login
        user_info = UserBase(email=email, name=name, surname=surname)
        
        return Token(access_token=access_token, token_type="bearer", user=user_info)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Errore grave durante il login: {e}") # Debug print
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore interno del server durante il login: {e}")

# --- Esempio di endpoint protetto ---
@router.get("/patients/me", response_model=UserBase) # Nota: il prefisso /api/auth/ sarà aggiunto automaticamente
async def read_current_patient(current_patient: PatientInDB = Depends(get_current_user)):
    # Questo endpoint ritorna solo le info base UserBase
    return UserBase(email=current_patient.email, name=current_patient.name, surname=current_patient.surname)

# Se vuoi un endpoint che ritorna TUTTI i dettagli del paziente
@router.get("/patients/details", response_model=PatientInDB)
async def read_patient_details(current_patient: PatientInDB = Depends(get_current_user)):
    # Ritorna l'intera istanza di PatientInDB
    return current_patient