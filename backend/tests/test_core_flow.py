def test_end_to_end_authenticated_interview_flow(client, auth_headers, fake_llm_response):
    headers = auth_headers()

    resume_response = client.post(
        "/ingestion/resumes/text",
        headers=headers,
        json={
            "title": "Backend Resume",
            "original_filename": "resume.txt",
            "resume_text": (
                "Backend engineer with 4 years of Python, FastAPI, PostgreSQL, Docker, and AWS experience."
            ),
        },
    )
    assert resume_response.status_code == 201, resume_response.text
    resume_id = resume_response.json()["id"]

    job_description_response = client.post(
        "/ingestion/job-descriptions",
        headers=headers,
        json={
            "role_title": "Backend Engineer",
            "company_name": "Acme",
            "raw_text": (
                "Required: Python, FastAPI, PostgreSQL. Responsibilities: build APIs and improve reliability."
            ),
        },
    )
    assert job_description_response.status_code == 201, job_description_response.text
    job_description_id = job_description_response.json()["id"]

    generation_response = client.post(
        "/generation/questions",
        headers=headers,
        json={
            "resume_id": resume_id,
            "job_description_id": job_description_id,
            "categories": ["technical", "project-based"],
            "difficulty": "medium",
            "question_count": 2,
            "session_title": "Backend Practice",
        },
    )
    assert generation_response.status_code == 201, generation_response.text
    generation_payload = generation_response.json()
    assert generation_payload["generated_count"] == 2
    assert generation_payload["source_mode"] == "resume_and_jd"
    session_id = generation_payload["interview_session_id"]

    session_detail_response = client.get(f"/sessions/{session_id}", headers=headers)
    assert session_detail_response.status_code == 200
    session_detail = session_detail_response.json()
    assert len(session_detail["questions"]) == 2
    question_id = session_detail["questions"][0]["id"]

    answer_response = client.post(
        "/answers",
        headers=headers,
        json={
            "question_id": question_id,
            "response_text": (
                "I would build a FastAPI ingestion service with validation, parsing, database persistence, and clear error handling."
            ),
        },
    )
    assert answer_response.status_code == 201, answer_response.text
    assert answer_response.json()["evaluation"]["score"] is not None

    analytics_response = client.get("/analytics/summary", headers=headers)
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    assert analytics["questions_attempted"] == 1
    assert analytics["answers_submitted"] == 1
    assert analytics["average_score"] > 0
    assert analytics["category_performance"][0]["questions_attempted"] >= 1


def test_user_cannot_generate_questions_from_another_users_resume(
    client,
    auth_headers,
    fake_llm_response,
):
    owner_headers = auth_headers(email="owner@example.com", full_name="Owner User")
    intruder_headers = auth_headers(email="intruder@example.com", full_name="Intruder User")

    resume_response = client.post(
        "/ingestion/resumes/text",
        headers=owner_headers,
        json={
            "title": "Owner Resume",
            "original_filename": "resume.txt",
            "resume_text": "Python FastAPI PostgreSQL backend engineer.",
        },
    )
    assert resume_response.status_code == 201
    resume_id = resume_response.json()["id"]

    generation_response = client.post(
        "/generation/questions",
        headers=intruder_headers,
        json={
            "resume_id": resume_id,
            "categories": ["technical"],
            "difficulty": "medium",
            "question_count": 1,
        },
    )

    assert generation_response.status_code == 400
    assert "authenticated user" in generation_response.json()["detail"]
