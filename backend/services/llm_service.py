 ## INtegrazione con LLM

from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List

import config as config 
from models import ContextDocument 

class LLMService:
    _embedding_model = None
    _llm_model = None

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
            cls._llm_model = Ollama(model=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL)
            print("LLM inizializzato.")
        return cls._llm_model

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """Genera l'embedding vettoriale per un dato testo."""
        model = cls.get_embedding_model()
        return model.encode(text).tolist()

    @classmethod
    def generate_response(cls, user_query: str, context_docs: List[ContextDocument]) -> str:
        """
        Genera una risposta usando l'LLM basandosi sulla query dell'utente e il contesto fornito.
        """
        llm = cls.get_llm_model()

        # Formatta i documenti di contesto in una stringa leggibile dall'LLM
        context_text = ""
        if context_docs:
            formatted_contexts = []
            for i, doc in enumerate(context_docs):
                formatted_contexts.append(f"Document {i+1}:\nQuestion: {doc.question}\nAnswer: {doc.answer}")
            context_text = "\n\n".join(formatted_contexts)
        
        if context_text:
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system", "Sei un assistente medico utile."
                    " Basati solo sulle informazioni contestuali fornite per rispondere alla domanda."
                    "SOLO Se le informazioni non contengono la risposta, "
                    "devi dire educatamente ed in brevissimo (poche parole) che non hai informazioni sufficienti nel contesto fornito per rispondere."),
                    ("user", "Informazioni contestuali:\n{context}\n\Question: {question}\n\Answer:"),
                ]
            )
        else:
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system", "Sei un assistente medico utile."
                    " Non hai accesso a informazioni specifiche."
                    " Rispondi alla domanda basandoti sulla tua conoscenza generale,"
                    " ma brevemente in poche parole avvisa l'utente che la tua risposta potrebbe non essere basata su dati specifici e potresti non avere tutte le informazioni."),
                    ("user", "{question}\n\Answer:"),
                ]
            )

        # Crea la catena di esecuzione: prompt -> llm -> parser
        chain = prompt_template | llm | StrOutputParser()
        full_response = chain.invoke({"context": context_text, "question": user_query})
        return full_response