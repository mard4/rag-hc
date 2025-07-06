from pydantic import BaseModel, EmailStr
from typing import List, Dict,Optional
from datetime import date
from datetime import datetime

## =========== RAG ================== ##

# richiesta di query (input dell'utente)
class QueryRequest(BaseModel):
    query: str

#singolo documento contestuale recuperato
class ContextDocument(BaseModel):
    question: str
    answer: Optional[str] = None
    context: Optional[str] = None     

#risposta dell'API RAG
class QueryResponse(BaseModel):
    answer: str # La risposta generata dall'LLM
    context_used: List[ContextDocument] # I documenti di contesto utilizzati per generare la risposta

class ExtendedQueryResponse(QueryResponse):
    suggestions: List[str]
    
## =========== Login ================== ##

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None

# Modello per la richiesta di registrazione (include la password)
class UserCreate(UserBase):
    password: str
    sex: str
    birth_date: date 
    address: str
    phone_number: str

# Modello per la richiesta di login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Modello per la risposta del token JWT
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Aggiungi qui i dati dell'utente se vuoi che il frontend li abbia subito dopo il login
    user: UserBase 

# Modello per i dati decodificati dal token JWT
class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None
    surname: Optional[str] = None

# Modello per l'utente come è memorizzato nel DB (include la password hashata)
class PatientInDB(UserBase):
    id: int
    password_hash: str 
    sex: str
    birth_date: date   
    address: str
    phone_number: str

# CRUD: bookings
class BookingCreate(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    reason_for_visit: str

class BookingOut(BookingCreate):
    id: int
    doctor_id: int
    appointment_date: datetime
    reason_for_visit: str
    status: str
    created_at: datetime

# CRUD: doctors

class DoctorOut(BaseModel):
    id: int
    name: str
    surname: str
    specialization: str
    rating: float


class AvailabilitySlot(BaseModel):
    doctor_id: int
    available_slots: List[datetime]

# CRUD: chat
class ChatMessage(BaseModel):
    id: int
    message: str
    answer: str
    timestamp: datetime