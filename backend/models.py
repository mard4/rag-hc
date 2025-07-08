from pydantic import BaseModel, EmailStr
from typing import List, Dict,Optional,Any
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


class Suggestion(BaseModel):
    type: str # 'question' o 'doctor_recommendation'
    value: str 
    data: Optional[Dict[str, Any]] = None

class ExtendedQueryResponse(QueryResponse):
    answer: str
    context_used: List[ContextDocument]
    suggestions: List[Suggestion]
    
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
    patient_id: int
    doctor_id: int
    appointment_date: datetime 
    reason_for_visit: Optional[str] = None

# class BookingIn(BaseModel):
#     doctor_id: int
#     appointment_date: datetime 
#     reason_for_visit: Optional[str] = None 
# class BookingOut(BaseModel):
#     id: int
#     patient_id: int
#     doctor_id: int
#     name: str
#     surname: str
#     appointment_date: datetime
#     reason_for_visit: Optional[str] = None
#     status: str
#     created_at: datetime
class BookingIn(BaseModel):
    doctor_id: int
    appointment_date: datetime 
    reason_for_visit: str

# For retrieving a booking (what the backend sends back)
class BookingOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    doctor_name: str
    doctor_surname: str # Added, comes from JOIN with doctors table
    appointment_date: datetime
    reason_for_visit: str
    status: str
    created_at: datetime
# CRUD: doctors

class DoctorOut(BaseModel):
    id: int
    name: str
    surname: str
    sex: str
    birth_date: date
    address: str
    phone_number: str
    email: EmailStr
    experience_years: int
    specialization: str
    rating: float

# CRUD: patients
class PatientOut(BaseModel):
    id: int
    name: str
    surname: str
    sex: str
    birth_date: str
    address: str
    phone_number: str
    email: EmailStr
    created_at: date

# TODO get patients bookings BookingsSlot    

class AvailabilitySlot(BaseModel):
    doctor_id: int
    available_slots: List[datetime]

# CRUD: chat
class ChatMessage(BaseModel):
    id: int
    message: str
    answer: str
    timestamp: datetime


