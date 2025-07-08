 ## INtegrazione con LLM

from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Optional, Dict, Any, Tuple
import traceback

import config as config 
from models import ContextDocument, Suggestion 
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class LLMService:
    _embedding_model = None
    _llm_model = None
    _intent_llm_model = None

    _sentiment_model_it = None
    _tokenizer_it = None

    @classmethod
    def get_embedding_model(cls):
        """Inizializza e restituisce il modello di embedding (singleton)."""
        if cls._embedding_model is None:
            print(f"Caricamento modello embedding: {config.EMBEDDING_MODEL_NAME}...")
            cls._embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
            print("Modello embedding caricato.")
        return cls._embedding_model

    @classmethod
    def get_llm_model(cls):
        """Inizializza e restituisce il modello LLM (singleton) tramite Ollama."""
        if cls._llm_model is None:
            print(f"Inizializzazione LLM con Ollama: {config.OLLAMA_MODEL_NAME} da {config.OLLAMA_BASE_URL}...")
            cls._llm_model = Ollama(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL,
                                    )
            print("LLM inizializzato.")
        return cls._llm_model

    @classmethod
    def get_intent_llm_model(cls):
        intent_model_name = getattr(config, 'OLLAMA_INTENT_MODEL_NAME', config.OLLAMA_INTENT_MODEL_NAME)
        if cls._intent_llm_model is None: 
            print(f"Inizializzazione LLM (riconoscimento intento) con Ollama: {intent_model_name}...")
            cls._intent_llm_model = Ollama(model=intent_model_name, base_url=config.OLLAMA_BASE_URL,
                                          )
            print("LLM (riconoscimento intento) inizializzato.")
        return cls._intent_llm_model
    

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """Genera l'embedding vettoriale per un dato testo."""
        model = cls.get_embedding_model()
        return model.encode(text).tolist()
    
    @staticmethod
    def _build_context(docs: List[ContextDocument], max_docs: int = 5,
                    max_chars: int = 3_000) -> str:
        """
        Concatena al massimo `max_docs` documenti e tronca a `max_chars`.
        Ritorna stringa pronta da inserire nel prompt.
        """
        out, total = [], 0
        for i, d in enumerate(docs[:max_docs], 1):
            part = f"Contesto {i}:\n"
            if d.question:
                part += f"Domanda: {d.question}\n"
            if d.answer:
                part += f"Risposta: {d.answer[:500]}…\n"
            if d.context:
                part += f"Dettagli: {d.context[:500]}…\n"
            if total + len(part) > max_chars:
                break
            out.append(part.strip())
            total += len(part)
        return "\n---\n".join(out)

    # ------------------------------------------------------------------
    # RISPOSTA + SUGGERIMENTI (UNICA CALL)
    # ------------------------------------------------------------------
    @classmethod
    def answer_and_suggest(
        cls,
        user_query: str,
        context_docs: List[ContextDocument],
        n_suggestions: int = 3,
    ) -> Tuple[str, List[Suggestion]]:
        """Restituisce (answer, suggestions) con una sola chiamata LLM.
        """
        llm = cls.get_llm_model()
        context_text = cls._build_context(context_docs)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Sei un assistente medico professionale, conciso e gentile. "
                    "Rispondi usando SOLO il contesto. "
                    "Se non è sufficiente, di': 'Non ho dati sufficienti.' "
                    f"Dopo la risposta, vai a capo e scrivi esattamente {n_suggestions} "
                    "domande di follow-up concise (una per riga). "
                    "Se ritieni serva uno specialista, AGGIUNGI una riga finale nel "
                    "formato 'NECESSITA_MEDICO: <breve descrizione>'.",
                ),
                (
                    "user",
                    "Contesto:\n{context}\n\nDomanda: {question}\n\nRisposta e follow-up:",
                ),
            ]
        )

        raw = (prompt | llm | StrOutputParser()).invoke(
            {"context": context_text, "question": user_query}
        )

        answer: str = ""
        suggestions: List[Suggestion] = []
        doctor_rec: Optional[Dict[str, Any]] = None

        for idx, line in enumerate(l.strip(" •-*\t") for l in raw.split("\n") if l.strip()):
            # prima riga = answer
            if idx == 0:
                answer = line
                continue
            # riga raccomandazione medico
            if line.upper().startswith("NECESSITA_MEDICO:"):
                prob = line.split(":", 1)[1].strip() or "Generale"
                doctor_rec = {"problem_type": prob}
                continue
            # follow‑up question
            if line.endswith("?"):
                suggestions.append(Suggestion(type="question", value=line))

        # assicurati di avere al max n_suggestions domande
        suggestions = suggestions[:n_suggestions]

        if doctor_rec:
            suggestions.append(
                Suggestion(
                    type="doctor_recommendation",
                    value="Trova il medico più adatto o prenota un appuntamento",
                    data=doctor_rec,
                )
            )

        return answer, suggestions
    
    # ------------------------------------------------------------------
    # INTENT CLASSIFIER  ── FAST RULE → LLM BACKUP

    _INTENT_KEYWORDS: Dict[str, List[str]] = {
        "SALUTO_GENERALE": ["ciao", "buongiorno", "buonasera", "salve", "hey"],
        "INFORMAZIONE_ASSISTENTE": ["chi sei", "cosa sei", "che cosa fai", "puoi fare"],
        "PRENOTAZIONE_MEDICO": ["prenota", "prenotare", "appuntamento", "visita", "fissare"],
    }

    # Vettore di specializzazioni comunemente digitate (minuscole)
    _SPECIALTY_TERMS: List[str] = [
        "cardiologo", "cardiologia", "dermatologo", "dermatologia", "ginecologo", "ginecologia",
        "ortopedico", "ortopedia", "neurologo", "neurologia", "oculista", "oftalmologo",
        "urologo", "urologia", "pneumologo", "pneumologia", "psichiatra", "psichiatria",
        "psicologo", "psicologia", "endocrinologo", "endocrinologia", "allergologo", "allergologia",
        "fisiatra", "fisiatria", "pediatra", "pediatria", "angiologo", "angiologia",
        "reumatologo", "reumatologia", "oncologo", "oncologia", "otorino", "otorinolaringoiatra",
        "otorinolaringoiatria", "nutrizionista", "nefrologo", "nefrologia", "gastroenterologo",
        "gastroenterologia", "ematologo", "ematologia",
    ]
    @staticmethod
    def _rule_based_intent(query: str) -> Optional[str]:
        q = query.lower()
        # 1) keyword intent
        for intent, kws in LLMService._INTENT_KEYWORDS.items():
            if any(kw in q for kw in kws):
                return intent
        # 2) short mention of a medical specialty → booking
        if any(sp in q for sp in LLMService._SPECIALTY_TERMS):
            if len(q.split()) <= 5:  # es. "cardiologo", "visita cardiologica"
                return "PRENOTAZIONE_MEDICO"
        return None

    @classmethod
    def recognize_intent(cls, user_query: str) -> str:
        """
        Classificatore ibrido
        Restituisce sempre uno dei 5 intent definiti, altrimenti 'ALTRO'.
        """
        # -- 1. RULE-BASED 
        hit = cls._rule_based_intent(user_query)
        if hit:
            return hit

        # -- 2. LLM BACKUP (tiny)
        intents = [
            "SALUTO_GENERALE",
            "INFORMAZIONE_ASSISTENTE",
            "RICHIESTA_MEDICA_GENERALE",
            "PRENOTAZIONE_MEDICO",
            "ALTRO",
        ]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Classifica la query in: " + ", ".join(intents)),
                ("user", "{query}"),
            ]
        )

        try:
            raw = (
                prompt
                | cls.get_intent_llm_model()
                | StrOutputParser()
            ).invoke({"query": user_query}).strip().upper()

            return raw if raw in intents else "ALTRO"

        except Exception:
            traceback.print_exc()
            return "ALTRO"
        
    ## == SENTIMENT ANALYSIS 

    @classmethod
    def get_italian_sentiment_model(cls):
        if cls._sentiment_model_it is None or cls._tokenizer_it is None:
            print("Caricamento modello di sentiment...")
            cls._tokenizer_it = AutoTokenizer.from_pretrained("MilaNLProc/feel-it-italian-sentiment")
            cls._sentiment_model_it = AutoModelForSequenceClassification.from_pretrained("MilaNLProc/feel-it-italian-sentiment")
        return cls._sentiment_model_it, cls._tokenizer_it

    @classmethod
    def detect_sentiment_it(cls, text: str) -> str:
        model, tokenizer = cls.get_italian_sentiment_model()
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        predicted_class = torch.argmax(logits).item()
        labels = ['negative', 'neutral', 'positive']
        probs = torch.nn.functional.softmax(logits, dim=1)[0]
        return f"{labels[predicted_class]} ({probs[predicted_class]:.2f})"