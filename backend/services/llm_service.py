 ## INtegrazione con LLM

from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Optional, Dict, Any, Tuple
import traceback

import config as config 
from models import ContextDocument, Suggestion 

class LLMService:
    _embedding_model = None
    _llm_model = None
    _intent_llm_model = None

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

    # @classmethod
    # def generate_response(cls, user_query: str, context_docs: List[ContextDocument]) -> str:
    #     """
    #     Genera una risposta usando l'LLM basandosi sulla query dell'utente e il contesto fornito.
    #     """
    #     llm = cls.get_llm_model()
        
    #     context_text = ""
    #     if context_docs:
    #         formatted_contexts = []
    #         for i, doc in enumerate(context_docs):
    #             context_part = f"Contesto {i+1}:\n"
    #             if doc.question: 
    #                 context_part += f"Domanda: {doc.question}\n"
    #             if doc.answer: 
    #                 context_part += f"Risposta: {doc.answer}\n"
    #             if doc.context: 
    #                 context_part += f"Dettagli: {doc.context}\n"
    #             formatted_contexts.append(context_part.strip()) # strip per pulire spazi extra
    #         context_text = "\n---\n".join(formatted_contexts) # Separatore chiaro tra i documenti
        
    #     if context_text:
    #         prompt_template = ChatPromptTemplate.from_messages(
    #             [
    #                 ("system", 
    #                  "Sei un assistente medico professionale,conciso e gentile. "
    #                  "Non ripetere al paziente la domanda che ha fatto"
    #                  "Rispondi direttamente alla domanda basandoti *esclusivamente* sulle informazioni contestuali fornite. "
    #                  "Se le informazioni non contengono una risposta chiara, rispondi semplicemente: 'Non ho dati sufficienti per rispondere a questa domanda specifica basandomi sulle informazioni fornite.' "
    #                  "Mantieni la risposta breve e al punto, senza saluti o frasi aggiuntive."
    #                 #  "Dopodichè, genera esattamente 1 domande di follow-up pertinenti e concise che potresti fare all'utente per capire meglio e per approfondire l'argomento. "
    #                 # "Le domande devono essere solo domande, senza introduzioni, spiegazioni o elenchi puntati. "
    #                 ),
    #                 ("user", 
    #                  "Contesto rilevante:\n{context}\n\n"
    #                  "Domanda: {question}\n\n"
    #                  "Risposta:" 
    #                 ),
    #             ]
    #         )
    #     else: # Nessun contesto recuperato
    #         prompt_template = ChatPromptTemplate.from_messages(
    #             [
    #                 ("system",
    #                  "Sei un assistente medico utile, conciso e gentile. "
    #                 "Non ripetere al paziente la domanda che ha fatto"
    #                  "Non hai accesso a informazioni specifiche del paziente o a un database di conoscenze approfondito. "
    #                  "Rispondi alla domanda basandoti solo sulla tua conoscenza generale. "
    #                 #   "Dopodichè, genera esattamente 1 domande di follow-up pertinenti e concise che potresti fare all'utente per capire meglio e per approfondire l'argomento. "
    #                 # "Le domande devono essere solo domande, senza introduzioni, spiegazioni o elenchi puntati. "
    #                  "Avvisa brevemente l'utente che la tua risposta è generica e che per informazioni più accurate dovrebbe consultare un medico o fornire più dettagli. "
    #                  "Mantieni la risposta concisa e diretta."
    #                 ),
    #                 ("user", 
    #                  "Domanda: {question}\n\n"
    #                  "Risposta:"
    #                 ),
    #             ]
    #         )

    #     # prompt -> llm -> parser
    #     chain = prompt_template | llm | StrOutputParser()
    #     full_response = chain.invoke({"context": context_text, "question": user_query})
    #     return full_response
    
    # ## =======================
    # @classmethod
    # def suggest_questions(cls, user_query: str, relevant_docs: List[ContextDocument]) -> List[str]:
    #         llm = cls.get_llm_model()

    #         context_text = ""
    #         if relevant_docs:
    #             formatted_contexts = []
    #             for i, doc in enumerate(relevant_docs):
    #                 context_part = f"Contesto {i+1}:\n"
    #                 if doc.question:
    #                     context_part += f"Domanda originale del documento: {doc.question}\n"
    #                 if doc.answer:
    #                     context_part += f"Risposta originale del documento: {doc.answer}\n"
    #                 if doc.context:
    #                     context_part += f"Dettagli aggiuntivi: {doc.context}\n"
    #                 formatted_contexts.append(context_part.strip())
    #             context_text = "\n---\n".join(formatted_contexts)

    #         prompt_template = ChatPromptTemplate.from_messages(
    #                     [
    #                         ("system",
    #                         "Sei un assistente medico utile e gentile. "
    #                         "Il tuo compito è suggerire 3-4 domande di follow-up pertinenti e concise. "
    #                         "Le domande devono essere formulate come se l'utente le stesse ponendo a te, cercando ulteriori informazioni sulla conversazione corrente o sul contesto fornito. "
    #                         "Non fare domande all'utente. Invece, formula le domande che l'utente potrebbe voler porre per approfondire. "
    #                         "Ogni domanda dovrebbe essere su una riga separata. Non aggiungere introduzioni come 'Potresti essere interessato a:'."
    #                         "Assicurati che le domande siano concise, chiare e dirette a ottenere nuove informazioni."
    #                         "\n\n"
    #                         "IMPORTANTE: Se, basandoti sulla query dell'utente o sul contesto, ritieni che una consulenza medica specialistica sia appropriata, aggiungi *una singola riga* alla fine del tuo output nel formato esatto:"
    #                         "\n'NECESSITA_MEDICO: [Descrizione breve del problema o specializzazione suggerita, es. Problemi respiratori, Dermatologia, Controllo generale]'"
    #                         "\nEsempio: 'NECESSITA_MEDICO: Problemi di digestione'"
    #                         "\nEsempio: 'NECESSITA_MEDICO: Oculista'" # Se l'LLM è bravo a inferirlo
    #                         "\nNon includere questa riga se non è necessaria una raccomandazione specifica."
    #                         ),
    #                         ("user",
    #                         "Conversazione corrente o query dell'utente:\n{query}\n\n"
    #                         "Contesto recuperato (se disponibile):\n{context}\n\n"
    #                         "Suggerisci domande di follow-up e/o necessità medico (una per riga):"
    #                         ),
    #                     ]
    #                 )

    #         chain = prompt_template | llm | StrOutputParser()
    #         full_output_text = chain.invoke({"query": user_query, "context": context_text})
            
    #         generated_suggestions: List[Suggestion] = []
    #         doctor_recommendation_data: Optional[Dict[str, Any]] = None

    #         for line in full_output_text.split('\n'):
    #             cleaned_line = line.strip(" –•*-\t")

    #             # 1. Cerca la necessità del medico
    #             if cleaned_line.startswith("NECESSITA_MEDICO:"):
    #                 try:
    #                     problem_description = cleaned_line.split("NECESSITA_MEDICO:", 1)[1].strip()
    #                     if problem_description:
    #                         doctor_recommendation_data = {"problem_type": problem_description}
    #                     else:
    #                         doctor_recommendation_data = {"problem_type": "Generale"} # Default se l'LLM non specifica
    #                 except IndexError:
    #                     print(f"Errore nel parsing di NECESSITA_MEDICO: {cleaned_line}")
    #                     pass
    #             # 2. Se non è una necessità medico e la riga non è vuota e finisce con '?', aggiungi come domanda
    #             elif cleaned_line and cleaned_line.endswith('?'):
    #                 generated_suggestions.append(Suggestion(type='question', value=cleaned_line))
                
    #             # Limita le domande per non sovraccaricare la UI
    #             if len([s for s in generated_suggestions if s.type == 'question']) >= 4:
    #                 break # Abbiamo raggiunto il numero di domande desiderato

    #         # Aggiungi il suggerimento per la raccomandazione del medico solo alla fine, se rilevato
    #         if doctor_recommendation_data:
    #             generated_suggestions.append(
    #                 Suggestion(
    #                     type='doctor_recommendation',
    #                     value='Trova il medico più adatto o prenota un appuntamento',
    #                     data=doctor_recommendation_data # Passa il tipo di problema inferito
    #                 )
    #             )
            
    #         return generated_suggestions
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

        Il prompt chiede *n_suggestions* follow‑up; supporta la riga
        "NECESSITA_MEDICO: …" per raccomandazione medico.
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
    

    # @classmethod
    # def recognize_intent(cls, user_query: str) -> str:
    #     """
    #     Riconosce l'intento dell'utente tra un set predefinito.
    #     """
    #     intent_llm = cls.get_intent_llm_model()

    #     intents = [
    #         "SALUTO_GENERALE",
    #         "INFORMAZIONE_ASSISTENTE",
    #         "RICHIESTA_MEDICA_GENERALE",
    #         "PRENOTAZIONE_MEDICO",
    #         "ALTRO"
    #     ]

    #     prompt_template = ChatPromptTemplate.from_messages(
    #         [
    #             ("system",
    #              "Sei un classificatore di intenti. Analizza la seguente query dell'utente e classificala in una delle seguenti categorie. "
    #              "Restituisci SOLO il nome della categoria, senza spiegazioni o testo aggiuntivo. "
    #              f"Categorie disponibili: {', '.join(intents)}."
    #              "\n\n"
    #              "Esempi:\n"
    #              "Query: Ciao\nIntento: SALUTO_GENERALE\n"
    #              "Query: Chi sei?\nIntento: INFORMAZIONE_ASSISTENTE\n"
    #              "Query: Mi fa male la testa\nIntento: RICHIESTA_MEDICA_GENERALE\n"
    #              "Query: Voglio fissare un appuntamento\nIntento: PRENOTAZIONE_MEDICO\n"
    #              "Query: Fammi una battuta\nIntento: ALTRO"
    #             ),
    #             ("user", "Query: {query}\nIntento:")
    #         ]
    #     )

    #     chain = prompt_template | intent_llm | StrOutputParser()
    #     try:
    #         raw_intent = chain.invoke({"query": user_query}).strip().upper()
    #         print(f"[DEBUG] Intento grezzo riconosciuto dall'LLM: '{raw_intent}'")
    #         if raw_intent in intents:
    #             return raw_intent
    #         else:
    #             return "ALTRO" # Fallback per intenti non riconosciuti o formattati male
    #     except Exception as e:
    #         print(f"[ERROR] Errore nel riconoscimento intento: {e}")
    #         traceback.print_exc()
    #         return "ALTRO" # Fallback in caso di errore

       # ------------------------------------------------------------------
    # INTENT CLASSIFIER  ── FAST RULE → LLM BACKUP
    # ------------------------------------------------------------------
# ------------------------------------------------------------------
    # LISTE KEYWORDS / SPECIALITÀ
    # ------------------------------------------------------------------
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
        Classificatore ibrido:
        1. Regole/keyword per intercettare i casi frequenti (≈0 ms).
        2. Se non matcha, fallback su LLM «tiny» con risposta secca a 1 token.
        Restituisce sempre uno dei 5 intent definiti, altrimenti 'ALTRO'.
        """
        # ── 1. RULE-BASED ────────────────────────────────────────────────
        hit = cls._rule_based_intent(user_query)
        if hit:
            return hit

        # ── 2. LLM BACKUP (tiny) ────────────────────────────────────────
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
