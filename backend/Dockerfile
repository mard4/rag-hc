# backend/Dockerfile

# Usa un'immagine base Python
FROM python:3.10-slim-buster

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia il file delle dipendenze del backend e installale
# È una buona pratica copiare solo le dipendenze e installarle
# per sfruttare la cache di Docker.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione backend
# (tutti i file e le sottocartelle dentro 'backend/')
COPY backend/ .

# Espone la porta su cui l'applicazione FastAPI sarà in ascolto
EXPOSE 8000

# Comando di avvio dell'applicazione.
# Nota: per la produzione, non useresti 'reload'.
# Per sviluppo, puoi sovrascrivere questo in docker-compose.yml.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]