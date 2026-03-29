# AI Interview Copilot

AI Interview Copilot is a production-style interview preparation platform that helps a user upload a resume and job description, generate tailored interview questions with free local LLMs or a hosted production model, submit answers, receive structured feedback, and track progress over time.

The repository is intentionally built as a portfolio-ready full-stack project: FastAPI on the backend, Streamlit on the frontend, PostgreSQL for persistence, Docker Compose for local orchestration, Ollama for free local model inference, Hugging Face for hosted production inference, and a modular codebase that is easy to extend.

## Why This Project Exists

Interview prep tools are often either generic question banks or thin wrappers around an LLM prompt. This project takes a more product-oriented approach:

- personalize interview questions using resume and JD context
- store sessions, questions, answers, and evaluations in a real database
- keep the AI layer modular and free to run locally
- expose clear APIs and a usable frontend for demos
- support future expansion into better scoring, richer analytics, and stronger UX

## Features

- Resume ingestion from text or uploaded files
- Job description ingestion and storage
- Deterministic parsing for skills, domains, roles, and experience
- Local LLM-powered interview question generation with Ollama
- Hosted production inference via Hugging Face Inference Providers
- Interview sessions with persisted generated questions
- Answer submission with rubric-style evaluation
- Authenticated user accounts with JWT-based access control
- Analytics for score trends, category performance, and weak areas
- Dockerized local development with PostgreSQL and Ollama
- Backend test setup with end-to-end core flow coverage
- Deployment-oriented Docker and config separation

## Tech Stack

- Backend: FastAPI, Pydantic, SQLAlchemy
- Frontend: Streamlit
- Database: PostgreSQL
- Local AI runtime: Ollama
- Hosted production AI runtime: Hugging Face Inference Providers
- Auth: JWT + passlib/bcrypt
- Testing: pytest, FastAPI TestClient
- Containers: Docker, Docker Compose

## Architecture

```text
Frontend (Streamlit)
        |
        v
Backend API (FastAPI)
        |
        +--> PostgreSQL
        |
        +--> Ollama (local open-source models)
```

Core backend layers:

- `api/`: route definitions and request handling
- `schemas/`: request and response contracts
- `services/`: business logic and orchestration
- `models/`: SQLAlchemy ORM entities
- `db/`: engine, session, and initialization flow
- `prompts/`: reusable LLM prompt templates
- `utils/`: parsing, file handling, and text helpers

More detail lives in [docs/architecture.md](docs/architecture.md).

## Repository Structure

```text
ai-interview-copilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── docs/
├── frontend/
│   ├── utils/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Local Stack

The default local stack is fully free to run:

- PostgreSQL for persistent application data
- Ollama for local model serving
- FastAPI backend for APIs and business logic
- Streamlit frontend for demo and user workflow

No paid LLM provider is required by default.

## Quick Start

### Option 1: Docker Compose

1. Create environment files:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

2. Start the full stack:

```bash
docker compose up --build
```

3. Pull the local models once Ollama is up:

```bash
docker exec -it ai_interview_copilot_ollama ollama pull llama3.1:8b
docker exec -it ai_interview_copilot_ollama ollama pull nomic-embed-text
```

4. Open the apps:

- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`
- Ollama API: `http://localhost:11434`

### Option 2: Local Development Without Docker

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

If you run the backend locally without Docker, make sure `DATABASE_URL` and `OLLAMA_BASE_URL` point to services reachable from your machine.

## Deployment

The recommended production split is:

- Frontend: Streamlit Community Cloud
- Backend: Render Web Service
- Database: Render Postgres
- Hosted model provider: Hugging Face Inference Providers

### Backend on Render

The repository includes a Render blueprint at [`render.yaml`](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/render.yaml). It provisions:

- a Python web service for `backend/`
- a managed PostgreSQL database

Important production environment variables:

```env
DATABASE_URL=<Render Postgres connection string>
MODEL_PROVIDER=huggingface
HF_API_TOKEN=<your Hugging Face token>
HF_CHAT_MODEL=google/gemma-2-2b-it
HF_BASE_URL=https://router.huggingface.co/v1/chat/completions
CORS_ALLOW_ORIGINS=https://your-streamlit-app.streamlit.app
SECRET_KEY=<strong random secret>
RUN_RELOAD=false
```

The backend uses:

- `GET /health`
- `GET /livez`
- `GET /readyz`

for operational checks in production.

### Frontend on Streamlit Community Cloud

Deploy the frontend with:

- branch: `production`
- main file: `frontend/app.py`

Set the frontend runtime values to point at the public backend:

```toml
BACKEND_URL = "https://your-backend.onrender.com"
BACKEND_BROWSER_URL = "https://your-backend.onrender.com"
API_TIMEOUT_SECONDS = "180"
```

## Product Flow

1. Sign up or log in from the frontend sidebar.
2. Upload or paste a resume.
3. Add a job description.
4. Generate interview questions from the stored context.
5. Submit answers inside a session.
6. Review structured evaluation and analytics.

## API Overview

Public endpoints:

- `GET /`
- `GET /health`
- `POST /auth/signup`
- `POST /auth/login`

Authenticated endpoints:

- `GET /auth/me`
- `POST /ingestion/resumes/text`
- `POST /ingestion/resumes/upload`
- `POST /ingestion/job-descriptions`
- `POST /parsing/resumes/{resume_id}`
- `POST /parsing/job-descriptions/{job_description_id}`
- `POST /generation/questions`
- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `POST /answers`
- `GET /analytics/summary`

See [docs/api-overview.md](docs/api-overview.md) for a more structured endpoint summary.

## Docker Usage

Main services in [docker-compose.yml](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/docker-compose.yml):

- `db`: PostgreSQL database
- `ollama`: local open-source model runtime
- `backend`: FastAPI service
- `frontend`: Streamlit UI

Useful commands:

```bash
docker compose up --build
docker compose down
docker compose logs backend
docker compose logs frontend
docker compose logs ollama
```

## Testing

Backend tests live in [backend/tests](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/backend/tests).

Run them with:

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m pytest
```

The current test setup includes:

- auth flow tests
- protected route checks
- startup smoke coverage
- end-to-end core flow coverage
- validation-focused API tests

## Environment Variables

The repo includes two templates:

- [`.env.example`](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/.env.example): Docker Compose and shared service configuration
- [`backend/.env.example`](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/backend/.env.example): backend-only application configuration

Important settings:

- `DATABASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `MODEL_PROVIDER`
- `OLLAMA_BASE_URL`
- `OLLAMA_CHAT_MODEL`
- `OLLAMA_EMBED_MODEL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `BACKEND_URL`
- `FRONTEND_PORT`

For anything beyond a local demo, replace the default `SECRET_KEY`.

## Screenshots

Suggested screenshots for a GitHub portfolio README:

- dashboard with analytics cards
- upload screen with parsed resume and JD data
- generated interview question session
- answer evaluation and history view

Place screenshots under `docs/screenshots/` and reference them here when you capture them.

Placeholder example:

```text
docs/screenshots/dashboard.png
docs/screenshots/generation.png
docs/screenshots/history.png
```

## Developer Notes

Additional project docs:

- [docs/architecture.md](docs/architecture.md)
- [docs/api-overview.md](docs/api-overview.md)
- [docs/developer-guide.md](docs/developer-guide.md)
- [docs/deployment.md](docs/deployment.md)
- [docs/roadmap.md](docs/roadmap.md)

## Roadmap

Completed phases:

- Phase 0: repository foundation
- Phase 1: backend base setup
- Phase 2: Dockerized development environment
- Phase 3: persistence layer and core entities
- Phase 4: ingestion pipeline
- Phase 5: structured parsing
- Phase 6: LLM-powered question generation
- Phase 7: interview session management
- Phase 8: answer submission and evaluation
- Phase 9: frontend application
- Phase 10: authentication and user management
- Phase 11: analytics and insights
- Phase 12: testing and validation
- Phase 13: documentation and developer experience
- Phase 14: deployment readiness

## Resume Value

This project is designed to demonstrate:

- backend API design with FastAPI
- service-oriented Python application structure
- Docker-first local development
- SQLAlchemy modeling and persistence
- auth and user-scoped workflows
- local LLM integration with provider abstraction
- practical analytics and product thinking
- testing and developer-experience discipline
