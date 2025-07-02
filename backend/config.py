import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB", "medquad_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "db") 
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384 

# --- Configurazione LLM (Ollama) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434") # 'ollama' = servizio docker
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3") # O mistral, gemma, .......

# --- Configurazione RAG ---
TOP_K_RESULTS = 5 # Numero di documenti da recuperare dal DB per il contesto