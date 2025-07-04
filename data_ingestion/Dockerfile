FROM python:3.10-slim-buster

WORKDIR /app

COPY data_ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_ingestion/*.py .

CMD ["sh", "-c", "python create_tables.py && python ingest_data_medquad.py"]
