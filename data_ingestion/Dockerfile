FROM python:3.10-slim-buster

WORKDIR /app

COPY data_ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_ingestion/ingest_data.py .

CMD ["python", "ingest_data.py"]