# API Overview

## Purpose

This document provides a quick developer-facing map of the current backend API surface.

Base URL in local development:

- `http://localhost:8000`

Interactive docs:

- `http://localhost:8000/docs`

## Public Endpoints

### Root

- `GET /`
- Returns service metadata and quick navigation pointers.

### Health

- `GET /health`
- Returns backend status, version, environment, and database availability.

### Authentication

- `POST /auth/signup`
- `POST /auth/login`

These endpoints return a bearer token that should be sent as:

```text
Authorization: Bearer <token>
```

## Authenticated Endpoints

### User

- `GET /auth/me`
- Returns the currently authenticated user.

### Ingestion

- `POST /ingestion/resumes/text`
- `POST /ingestion/resumes/upload`
- `POST /ingestion/job-descriptions`

Purpose:

- store raw resume or JD content
- trigger deterministic parsing
- persist parsed metadata

### Parsing

- `POST /parsing/resumes/{resume_id}`
- `POST /parsing/job-descriptions/{job_description_id}`

Purpose:

- rerun structured parsing when needed

### Question Generation

- `POST /generation/questions`

Supports:

- resume-only generation
- JD-only generation
- combined resume + JD generation
- generation into a new or existing session

### Interview Sessions

- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`

Purpose:

- create session containers
- review prior sessions
- fetch a full session with questions, answers, and evaluations

### Answers

- `POST /answers`

Purpose:

- submit a candidate answer
- trigger evaluation
- persist answer + evaluation output

### Analytics

- `GET /analytics/summary`

Returns:

- questions attempted
- answers submitted
- average score
- category-wise performance
- weak-area recommendations

## Main Domain Entities

- `User`
- `Resume`
- `JobDescription`
- `InterviewSession`
- `Question`
- `Answer`
- `Evaluation`

These live in [backend/app/models](/Users/dhananjay/ai-interview-copilot/ai-interview-copilot/backend/app/models).

## Notes

- Most product workflows are user-scoped and require authentication.
- The backend currently uses deterministic parsing and scoring plus a local LLM for question generation.
- The OpenAPI schema in `/docs` is the most precise live contract for request and response shapes.
