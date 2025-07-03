from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # Per gestire le richieste da frontend diversi

import config as config 
from models import QueryRequest, QueryResponse, ContextDocument 
from services.db_service import retrieve_relevant_data
from services.llm_service import LLMService

app = FastAPI(
    title="MedQuAD RAG API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permette tutte le origini per sviluppo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
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
        # Genera l'embedding della query utente
        query_embedding = LLMService.embed_text(user_query)
        print(f"[{__name__}] Embedding della query generato. Dim: {len(query_embedding)}")

        # Recupera il contesto dal database vettoriale
        relevant_docs = retrieve_relevant_data(query_embedding, top_k=config.TOP_K_RESULTS)
        print(f"[{__name__}] Recuperati {len(relevant_docs)} documenti dal DB.")

        # Genera la risposta usando l'LLM con il contesto
        generated_answer = LLMService.generate_response(user_query, relevant_docs)
        print(f"[{__name__}] Risposta generata dall'LLM.")

        return QueryResponse(answer=generated_answer, context_used=relevant_docs)

    except Exception as e:
        print(f"[{__name__}] Errore durante l'elaborazione della domanda: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Errore interno del server: {e}")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verifica lo stato di salute dell'API."""
    return {"status": "ok", "message": "MedQuAD RAG API is running."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) # reload=False