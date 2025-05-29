# Async Task Management API 🚀

## Overview

This project provides a fully async task management API built with FastAPI, SQLAlchemy (async), and PostgreSQL, supporting background processing for long-running tasks. The API is containerized with Docker for easy local and production deployment.

**Features:**
- Create, list (with filtering and pagination), update, and delete tasks
- Background processing of tasks with status logs
- Async programming for scalable performance
- Alembic-managed database schema and migrations
- Full request validation and error handling
- Dockerized PostgreSQL and API app
- Unit tests

---

## Architecture

- **FastAPI:** for API endpoints and background tasks
- **SQLAlchemy (async):** for database ORM
- **Alembic:** for database migrations
- **Docker Compose:** to orchestrate app and database
- **Pytest:** for unit testing

---

## Getting Started

### Prerequisites

- Docker & Docker Compose installed
- Git installed

### Quick Start

1. **Clone the repository:**
    ```sh
    git clone https://github.com/danilomarkovic99/Async-Task-Management-API-with-Background-Processing
    cd Async-Task-Management-API-with-Background-Processing
    ```

2. **(Optional) Edit the environment file:**
    `.env` adjust settings if needed.

3. **Start services:**
    ```sh
    docker-compose up --build
    ```
    This will:
    - Start the Postgres database
    - Run Alembic migrations
    - Launch the FastAPI app on [http://localhost:8000/docs#]

4. **Run tests:**
    ```sh
    pytest
    ```

---

## API Endpoints

- `POST /tasks`: Create a new task
- `GET /tasks`: List all tasks (supports filtering & pagination)
- `GET /tasks/{task_id}`: Get details of a specific task
- `PUT /tasks/{task_id}`: Update a task’s data
- `DELETE /tasks/{task_id}`: Delete a task
- `POST /tasks/{task_id}/process`: Start background processing for a task

---

## Database Migration

- Alembic is used to manage the database schema.
- Migrations are run automatically on startup, or manually using:
    ```sh
    docker-compose exec api alembic revision --autogenerate -m "Your migration name"
    docker-compose exec api alembic upgrade head
    ```

---

## Security & Best Practices

- All inputs are validated with Pydantic.
- Database queries are parameterized (ORM).
- Secrets and configs should be managed with environment variables.

---

*Made with ❤️ by [Rade Stojkovic]*

