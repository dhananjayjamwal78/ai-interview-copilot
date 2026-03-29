# Developer Guide

## Overview

This project is organized to keep transport, domain logic, persistence, and AI-specific behavior separated.

## How To Read The Backend

Start here:

1. `backend/app/main.py`
2. `backend/app/api/api_v1.py`
3. `backend/app/api/routes/`
4. `backend/app/services/`
5. `backend/app/models/`

Suggested mental model:

- routes validate and translate HTTP requests
- schemas define contracts
- services hold workflow logic
- models represent persisted entities
- utils contain reusable low-level helpers

## Local Development Workflow

Backend:

```bash
cd backend
cp .env.example .env
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Full stack:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
docker compose up --build
```

## Testing Workflow

```bash
cd backend
python3 -m pytest
```

Tests use:

- FastAPI `TestClient`
- dependency overrides for database access
- SQLite for isolated test execution
- mocked LLM output for stable generation tests

## Extending The Project

### Add a new API workflow

1. Add or update schema definitions in `schemas/`
2. Add service logic in `services/`
3. Add a route in `api/routes/`
4. Register the route in `api/api_v1.py`
5. Add tests in `backend/tests/`

### Improve the AI layer

Current question generation goes through:

- `backend/app/prompts/question_generation.py`
- `backend/app/services/llm_service.py`
- `backend/app/services/question_generation_service.py`

To add another provider, extend the provider abstraction in `llm_service.py` rather than calling a model directly from route code.

### Improve evaluation

Current scoring is deterministic and intentionally simple. The clean expansion point is:

- `backend/app/services/evaluation_service.py`

## Developer Notes

- The repo defaults to free local models through Ollama.
- Auth is bearer-token based and all product data is user-scoped.
- The current DB initialization flow creates tables on startup and is structured to support future migration improvements.
- Streamlit is used for speed and demoability, not because the frontend is intended to stay minimal forever.
