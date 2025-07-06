import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ["POSTGRES_DB"],
DB_USER = os.environ["POSTGRES_DB"],
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"],
DB_HOST = os.environ["POSTGRES_HOST"],  
DB_PORT = os.environ["POSTGRES_PORT"]

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384 

# --- Configurazione LLM (Ollama) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434") # 'ollama' = servizio docker
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3") # O mistral, gemma, .......

# --- Configurazione RAG ---
TOP_K_RESULTS = 5 # Numero di documenti da recuperare dal DB per il contesto
CHAT_HISTORY_LIMIT = 5