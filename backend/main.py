from fastapi import FastAPI, HTTPException, status, Depends, Query 
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import config as config 
from models import QueryRequest, QueryResponse, ContextDocument, ExtendedQueryResponse, PatientInDB, Suggestion
from services.db_service import retrieve_relevant_data 
from services.llm_service import LLMService
from db_utils import get_db, insert_chat_message
from login import router as auth_router 
from auth_utils import get_current_user 
import traceback
from typing import List
import time

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
    LLMService.get_intent_llm_model() 
    print("FastAPI startup complete.")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verifica lo stato di salute dell'API."""
    return {"status": "ok", "message": "Auth API is running."}

@app.post("/ask",
          response_model=ExtendedQueryResponse,
          status_code=status.HTTP_200_OK)
async def ask_question(
    request: QueryRequest,
    include_suggestions: bool = Query(False,
        description="Set to true to include follow-up questions."),
    db=Depends(get_db),
    current_user: PatientInDB = Depends(get_current_user),
):
    conn, cur = db
    user_query = request.query
    generated_answer = ""
    relevant_docs: List[ContextDocument] = []
    suggestions: List[Suggestion] = []

    try:
        print(f"[DEBUG] Utente autenticato (ID): {current_user.id} "
              f"(Email: {current_user.email})")
        print(f"[DEBUG] Query ricevuta: {user_query}")

        # ── INTENT ────────────────────────────────────────────────────────
        t0 = time.time()
        intent = LLMService.recognize_intent(user_query)
        print(f"[{__name__}] Intento riconosciuto: '{intent}' "
              f"(Tempo: {time.time() - t0:.4f}s)")

        # ── RISPOSTE RAPIDE SENZA RAG ────────────────────────────────────
        if intent == "SALUTO_GENERALE":
            generated_answer = "Ciao! Come posso aiutarti oggi?"

        elif intent == "INFORMAZIONE_ASSISTENTE":
            generated_answer = ("Sono un assistente medico virtuale, creato per "
                                "rispondere alle tue domande mediche e aiutarti "
                                "a trovare un medico.")

        elif intent == "PRENOTAZIONE_MEDICO":
            generated_answer = ("Certo, posso aiutarti a trovare un medico. "
                                "Che specializzazione cerchi o quali sono i tuoi sintomi?")
            suggestions.append(
                Suggestion(
                    type="doctor_recommendation",
                    value="Trova il medico più adatto o prenota un appuntamento",
                    data={"problem_type": user_query or "Generale"},
                )
            )

        # ── PIPELINE RAG ─────────────────────────────────────────────────
        elif intent in ("RICHIESTA_MEDICA_GENERALE", "ALTRO"):
            # 1) embedding + retrieval
            t1 = time.time()
            query_emb = LLMService.embed_text(user_query)
            print(f"[{__name__}] Embedding OK (Tempo: {time.time() - t1:.4f}s)")

            t2 = time.time()
            relevant_docs = retrieve_relevant_data(
                patient_id=current_user.id,
                query_embedding=query_emb,
                top_k=config.TOP_K_RESULTS,
                chat_k=config.CHAT_HISTORY_LIMIT,
            )
            print(f"[{__name__}] Retrieval {len(relevant_docs)} doc "
                  f"(Tempo: {time.time() - t2:.4f}s)")

            # 2) risposta + follow-up in una sola call
            t3 = time.time()
            if include_suggestions:
                generated_answer, suggestions = LLMService.answer_and_suggest(
                    user_query, relevant_docs, n_suggestions=3
                )
            else:
                generated_answer, _ = LLMService.answer_and_suggest(
                    user_query, relevant_docs, n_suggestions=0
                )
            print(f"[{__name__}] LLM risposta+suggest "
                  f"(Tempo: {time.time() - t3:.4f}s)")

        # ── PERSISTENZA CHAT ────────────────────────────────────────────
        insert_chat_message(conn, cur, current_user.id, user_query, generated_answer)
        conn.commit()

        return ExtendedQueryResponse(
            answer=generated_answer,
            context_used=relevant_docs,
            suggestions=suggestions,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


from routers import doctors, chat, bookings

app.include_router(bookings.router)
app.include_router(doctors.router)
app.include_router(chat.router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)