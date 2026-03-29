# Architecture Notes

## Goal

AI Interview Copilot is designed as a modular full-stack application that can grow from a local development setup into a more production-like architecture without major restructuring.

## Core Components

- `frontend/`: Streamlit UI for candidate workflows, interview sessions, and analytics views
- `backend/app/api/`: API surface for health, interviews, uploads, scoring, and AI workflows
- `backend/app/services/`: business logic and orchestration layer
- `backend/app/schemas/`: request and response contracts
- `backend/app/db/`: database engine, session management, and migrations wiring
- `backend/app/models/`: SQLAlchemy ORM models
- `backend/app/prompts/`: prompt templates for LLM-powered tasks
- `ollama`: local inference runtime for free open-source language and embedding models
- `backend/app/utils/`: reusable utilities such as parsers and text helpers

## Runtime Topology

- `frontend` talks to `backend` over HTTP
- `backend` persists data in PostgreSQL
- `backend` calls Ollama for local inference
- Docker Compose orchestrates the local development stack

## Request Flow

Typical product flow:

1. User authenticates through the frontend.
2. Frontend sends bearer-authenticated requests to FastAPI.
3. FastAPI routes validate payloads with Pydantic schemas.
4. Service-layer code orchestrates persistence, parsing, generation, or evaluation.
5. SQLAlchemy models persist workflow state in PostgreSQL.
6. Ollama is used only where LLM-backed question generation is needed.

## Design Priorities

- Keep each phase runnable
- Prefer explicit schemas and clear service boundaries
- Separate transport, business logic, and persistence
- Keep the structure friendly to future auth, background jobs, and analytics
- Default to free and open-source components for local development

## Current Architectural Tradeoffs

- Streamlit keeps the frontend simple and demo-friendly, though a richer SPA could replace it later.
- Table creation currently happens on startup for simplicity; Alembic is already in the repo for future migration hardening.
- Parsing and evaluation are deterministic-first so the platform remains testable and cost-free.
