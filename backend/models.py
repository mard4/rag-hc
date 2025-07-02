from pydantic import BaseModel
from typing import List, Dict

# Modello per la richiesta di query (input dell'utente)
class QueryRequest(BaseModel):
    query: str

# Modello per un singolo documento contestuale recuperato
class ContextDocument(BaseModel):
    question: str
    answer: str

# Modello per la risposta dell'API RAG
class QueryResponse(BaseModel):
    answer: str # La risposta generata dall'LLM
    context_used: List[ContextDocument] # I documenti di contesto utilizzati per generare la risposta
