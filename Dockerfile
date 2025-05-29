FROM python:3.12-slim

WORKDIR /code

# Install PostgreSQL client (psql) and any system deps
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

COPY ./app ./app
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic

COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh
