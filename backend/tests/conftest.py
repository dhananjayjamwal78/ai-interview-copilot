import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr("app.main.init_db", lambda: None)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    def _create_user(email="candidate@example.com", password="strongpass123", full_name="Test User"):
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
            },
        )
        assert signup_response.status_code == 201, signup_response.text
        token = signup_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _create_user


@pytest.fixture()
def fake_llm_response(monkeypatch):
    payload = {
        "questions": [
            {
                "prompt": "Explain how you would design a FastAPI service for resume ingestion.",
                "category": "technical",
                "difficulty": "medium",
            },
            {
                "prompt": "Describe a project where you improved system reliability.",
                "category": "project-based",
                "difficulty": "medium",
            },
        ]
    }
    monkeypatch.setattr(
        "app.services.question_generation_service.llm_service.generate",
        lambda prompt: json.dumps(payload),
    )
    return payload
