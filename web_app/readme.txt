DATABASE_NAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_USER=postgres

SERVICE_BADLISTED_WORDS=http://0.0.0.0:8018/badlisted_words
SERVICE_SPACY_NOUNPHRASES=http://0.0.0.0:8006/respond


docker compose -f docker-compose.yml -f assistant_dists/dream_script_based/docker-compose.override.yml -f assistant_dists/dream_script_based/dev.yml up --build -d badlisted-words spacy-nounphrases web db && sleep 1 && docker compose exec web alembic revision --autogenerate && docker compose exec web alembic upgrade head
