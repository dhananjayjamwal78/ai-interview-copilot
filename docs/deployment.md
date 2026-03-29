# Deployment Notes

## Goal

This document explains how to move the project from local development to a more deployment-ready setup.

## Current Deployment Posture

The repo now includes:

- safer non-root Docker images for backend and frontend
- explicit dev vs prod config flags
- configurable CORS behavior
- liveness and readiness endpoints
- a production-oriented Compose override

## Key Runtime Endpoints

- `GET /health`: general health summary
- `GET /livez`: liveness check for process health
- `GET /readyz`: readiness check for dependency health

`/readyz` returns `503` when the database is unavailable, which makes it suitable for container orchestrators and load balancers.

## Development Compose

Use the default file for local development:

```bash
docker compose up --build
```

This keeps:

- bind mounts for rapid iteration
- `uvicorn --reload`
- docs enabled

## Production-Style Compose

Use the production override when you want a cleaner deployment profile:

```bash
cp backend/.env.production.example backend/.env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

This changes the stack to:

- disable reload
- disable docs/OpenAPI exposure
- keep restart policies at `always`
- rely on readiness checks for backend startup health

## CORS

CORS is now controlled through:

- `CORS_ALLOW_ORIGINS`
- `CORS_ALLOW_METHODS`
- `CORS_ALLOW_HEADERS`

For production, set `CORS_ALLOW_ORIGINS` to your real frontend origin rather than localhost values.

## Deployment Recommendations

Recommended deployment targets for this project:

- Railway for the FastAPI backend and PostgreSQL database
- Streamlit Community Cloud for the frontend
- Hugging Face Inference Providers for hosted production question generation

## Practical Notes

- Replace the default `SECRET_KEY` before any real deployment.
- Use a managed PostgreSQL instance if you want easier persistence operations.
- Consider putting the backend behind a reverse proxy such as Nginx or Caddy.
- For production, use a hosted model provider instead of local Ollama.
- If you deploy frontend and backend separately, update `BACKEND_URL` and `CORS_ALLOW_ORIGINS` together.
