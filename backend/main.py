from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # Per gestire le richieste da frontend diversi

import config as config # Importa la configurazione
from models import QueryRequest, QueryResponse, ContextDocument # Importa i modelli Pydantic
from services.db_service import retrieve_relevant_data
from services.llm_service import LLMService

app = FastAPI(
    title="MedQuAD RAG API",
    description="API per un sistema di Generazione Aumentata dal Recupero (RAG) sul dataset MedQuAD.",
    version="1.0.0"
)

# Configurazione CORS per permettere richieste da un frontend (se avrai uno sviluppo separato)
# Modifica 'origins' con l'URL del tuo frontend in produzione
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permette tutte le origini per sviluppo. CAMBIARE IN PRODUZIONE!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Carica i modelli di embedding e LLM all'avvio dell'applicazione."""
    # Questo assicura che i modelli vengano inizializzati una sola volta
    LLMService.get_embedding_model()
    LLMService.get_llm_model()

@app.post("/ask", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def ask_question(request: QueryRequest):
    """
    Endpoint per porre una domanda e ricevere una risposta generata dal sistema RAG.
    """
    user_query = request.query
    print(f"[{__name__}] Ricevuta domanda: '{user_query}'")

    try:
        # 1. Genera l'embedding della query utente
        query_embedding = LLMService.embed_text(user_query)
        print(f"[{__name__}] Embedding della query generato. Dim: {len(query_embedding)}")

        # 2. Recupera il contesto dal database vettoriale
        relevant_docs = retrieve_relevant_data(query_embedding, top_k=config.TOP_K_RESULTS)
        print(f"[{__name__}] Recuperati {len(relevant_docs)} documenti dal DB.")

        # 3. Genera la risposta usando l'LLM con il contesto
        generated_answer = LLMService.generate_response(user_query, relevant_docs)
        print(f"[{__name__}] Risposta generata dall'LLM.")

        return QueryResponse(answer=generated_answer, context_used=relevant_docs)

    except Exception as e:
        print(f"[{__name__}] Errore durante l'elaborazione della domanda: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore interno del server: {e}")

# Endpoint di health check per verificare che l'API sia attiva
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verifica lo stato di salute dell'API."""
    return {"status": "ok", "message": "MedQuAD RAG API is running."}

# Per avviare l'applicazione (per sviluppo, tipicamente gestito da uvicorn via docker-compose)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) # reload=True utile per sviluppo