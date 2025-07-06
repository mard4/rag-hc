# main.py
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import config as config 
from models import QueryRequest, QueryResponse, ContextDocument, ExtendedQueryResponse, PatientInDB 
from services.db_service import retrieve_relevant_data
from services.llm_service import LLMService
from db_utils import get_db
from login import router as auth_router 
from auth_utils import get_current_user 
import traceback


app = FastAPI(
    title="RAG API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permette tutte le origini per sviluppo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    print("Starting up FastAPI application...")
    LLMService.get_embedding_model()
    LLMService.get_llm_model()
    print("FastAPI startup complete.")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verifica lo stato di salute dell'API."""
    return {"status": "ok", "message": "Auth API is running."}

@app.post("/ask",
           response_model=QueryResponse,
             status_code=status.HTTP_200_OK)
async def ask_question(
    request: QueryRequest,
    db = Depends(get_db),                            
    current_user: PatientInDB = Depends(get_current_user) # CAMBIA IL TIPO QUI!
    ):
    """
    Endpoint per porre una domanda e ricevere una risposta generata dal sistema RAG.
    """
    conn, cur = db
    try:
        print(f"[DEBUG] Utente autenticato (ID): {current_user.id} (Email: {current_user.email})")
        print(f"[DEBUG] Query ricevuta: {request.query}")
        
        query_embedding = LLMService.embed_text(request.query)
        print(f"[{__name__}] Embedding della query generato. Dim: {len(query_embedding)}")

        # Recupera il contesto dal database vettoriale
        relevant_docs = retrieve_relevant_data(patient_id=current_user.id,
                                                query_embedding=query_embedding,
                                                  top_k=config.TOP_K_RESULTS, chat_k=config.CHAT_HISTORY_LIMIT)
        print(f"[{__name__}] Recuperati {len(relevant_docs)} documenti dal DB.")

        # Genera la risposta usando l'LLM con il contesto
        generated_answer = LLMService.generate_response(request.query, relevant_docs)
        print(f"[{__name__}] Risposta generata dall'LLM.")

        # CHat History 
        cur.execute(
            """
            INSERT INTO chat (patient_id, message, answer)
            VALUES (%s,%s,%s)
            """,
            (current_user.id, request.query, generated_answer) 
        )
        conn.commit()
        return QueryResponse(answer=generated_answer, context_used=relevant_docs)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )
    finally:
        conn.close()

@app.post(
    "/ask_with_suggestions",
    response_model=ExtendedQueryResponse,
    status_code=status.HTTP_200_OK
)
async def ask_with_suggestions(
    request: QueryRequest,
    db = Depends(get_db),
    current_user: PatientInDB = Depends(get_current_user), 
):
    """
    Stesso flusso di /ask, ma con suggerimenti di follow-up.
    """
    conn, cur = db
    try:
        # embedding
        query_embedding = LLMService.embed_text(request.query)

        # contesto
        relevant_docs = retrieve_relevant_data(
            patient_id=current_user.id, 
            query_embedding=query_embedding,
            top_k=config.TOP_K_RESULTS,
            chat_k=config.CHAT_HISTORY_LIMIT
        )

        # risposta
        generated_answer = LLMService.generate_response(request.query, relevant_docs)

        # persisti chat
        cur.execute(
            """
            INSERT INTO chat (patient_id, message, answer)
            VALUES (%s, %s, %s)
            """,
            (current_user.id, request.query, generated_answer) # current_user.id è l'ID numerico
        )
        conn.commit()

        # suggerimenti follow-up
        suggestions = LLMService.suggest_questions(request.query, relevant_docs)

        return ExtendedQueryResponse(
            answer=generated_answer,
            context_used=relevant_docs,
            suggestions=suggestions
        )

    except Exception as e:
        print(f"[ask_with_suggestions] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )
    finally:
        conn.close()

from routers import  doctors, chat, appointments

app.include_router(appointments.router)
app.include_router(doctors.router)
app.include_router(chat.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)