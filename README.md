# rag-hc

source venv/bin/activate 

### STart project
docker compose up -d
docker compose run --rm data_ingestion python ingest_data.py

docker exec -it rag-hc-db-1  psql -U user -d medquad_db
SELECT COUNT(*) FROM medquad;
SELECT question, SUBSTRING(answer, 1, 50) || '...' as answer_preview, question_embedding FROM medquad LIMIT 5;
