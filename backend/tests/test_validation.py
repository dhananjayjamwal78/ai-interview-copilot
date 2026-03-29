def test_resume_text_rejects_whitespace_only_content(client, auth_headers):
    headers = auth_headers()

    response = client.post(
        "/ingestion/resumes/text",
        headers=headers,
        json={
            "title": "   ",
            "original_filename": "resume.txt",
            "resume_text": "   ",
        },
    )

    assert response.status_code == 422


def test_answer_submission_rejects_blank_text(client, auth_headers, fake_llm_response):
    headers = auth_headers()

    resume_response = client.post(
        "/ingestion/resumes/text",
        headers=headers,
        json={
            "title": "Backend Resume",
            "original_filename": "resume.txt",
            "resume_text": "Python FastAPI Docker PostgreSQL engineer.",
        },
    )
    resume_id = resume_response.json()["id"]

    generation_response = client.post(
        "/generation/questions",
        headers=headers,
        json={
            "resume_id": resume_id,
            "categories": ["technical"],
            "difficulty": "medium",
            "question_count": 1,
        },
    )
    session_id = generation_response.json()["interview_session_id"]

    session_detail_response = client.get(f"/sessions/{session_id}", headers=headers)
    question_id = session_detail_response.json()["questions"][0]["id"]

    response = client.post(
        "/answers",
        headers=headers,
        json={
            "question_id": question_id,
            "response_text": "   ",
        },
    )

    assert response.status_code == 422
