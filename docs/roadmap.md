# Phase Roadmap

## Completed

### Phase 0

- Clean repository structure
- Base docs, `.env.example`, `.gitignore`, and license

### Phase 1

- FastAPI backend skeleton
- Root and health endpoints
- Config and router structure

### Phase 2

- Docker Compose setup
- PostgreSQL container
- Backend container and service networking

### Phase 3

- SQLAlchemy setup and session management
- Core ORM entities
- Database initialization flow

### Phase 4

- Resume and JD ingestion APIs
- File handling and text extraction
- Raw content persistence

### Phase 5

- Deterministic parsing for skills, roles, domains, and experience
- Parsed metadata persistence

### Phase 6

- Free local LLM-powered question generation via Ollama
- Prompt management
- Provider abstraction

### Phase 7

- Interview session lifecycle APIs
- Session metadata and question persistence

### Phase 8

- Answer submission
- Deterministic evaluation and feedback
- Evaluation persistence

### Phase 9

- Streamlit frontend workflow
- Upload, generate, answer, history, and review screens

### Phase 10

- Signup/login flow
- Password hashing
- Auth-protected routes and user-scoped data

### Phase 11

- Analytics summary APIs
- Weak-area and category-performance reporting

### Phase 12

- Backend test setup
- Core flow and validation coverage
- Startup smoke checks

### Phase 13

- GitHub-ready README
- Developer docs
- Improved environment templates

## Good Next Steps

- Replace startup table creation with full Alembic migration flow
- Add richer evaluation signals using embeddings or local scoring models
- Expand frontend UX beyond Streamlit if a more product-like client is desired
- Add exportable interview reports and session comparison views
