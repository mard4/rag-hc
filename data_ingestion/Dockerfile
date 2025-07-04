FROM python:3.10-slim-buster

WORKDIR /app

COPY data_ingestion/ .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python create_tables.py && python ingest_data_medquad.py && python ingest_data_mimic.py"]
