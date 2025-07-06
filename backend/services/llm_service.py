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
                    ("system", 
                    "Sei un assistente medico utile. Basati solo sulle informazioni contestuali fornite. "
                    "Se le informazioni non contengono la risposta, rispondi brevemente che non hai dati sufficienti."),
                    ("user", 
                    "Informazioni contestuali:\n{context}\n\n"
                    "Domanda: {question}\nRisposta:"),
                ]
            )
        else:
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system",
                    "Sei un assistente medico utile. Non hai accesso a informazioni specifiche. "
                    "Rispondi basandoti sulla tua conoscenza generale, ma avvisa brevemente l'utente che potresti non avere tutti i dati."),
                    ("user", 
                    "Domanda: {question}\nRisposta:"),
                ]
            )


        # Crea la catena di esecuzione: prompt -> llm -> parser
        chain = prompt_template | llm | StrOutputParser()
        full_response = chain.invoke({"context": context_text, "question": user_query})
        return full_response
    
    @classmethod
    def suggest_questions(cls, last_question: str, context_docs: List[ContextDocument]) -> List[str]:
        llm = cls.get_llm_model()
        prompt = (
            "Sei un assistente medico. Sulla base delle informazioni fornite, "
            "suggerisci 3 domande che l'utente potrebbe fare per chiarire o approfondire "
            f"l'argomento: «{last_question}».\n\n"
            "Rispondi con elenco puntato, italiano."
        )
        resp = llm.invoke(prompt) 
        return [line.strip(" –• ") for line in resp.splitlines() if line.strip()]
        #return resp.split("\n")  # parse in lista
            