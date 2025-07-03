from pydantic import BaseModel
from typing import List, Dict

# richiesta di query (input dell'utente)
class QueryRequest(BaseModel):
    query: str

#singolo documento contestuale recuperato
class ContextDocument(BaseModel):
    question: str
    answer: str

#risposta dell'API RAG
class QueryResponse(BaseModel):
    answer: str # La risposta generata dall'LLM
    context_used: List[ContextDocument] # I documenti di contesto utilizzati per generare la risposta
