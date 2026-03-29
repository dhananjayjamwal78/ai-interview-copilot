import os

import requests


class APIClientError(Exception):
    pass


class APIClient:
    def __init__(self, base_url=None):
        self.base_url = (base_url or os.getenv("BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.token = None
        self.timeout_seconds = int(os.getenv("API_TIMEOUT_SECONDS", "180"))

    def set_token(self, token):
        self.token = token

    def _headers(self, extra_headers=None):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", None)
        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout_seconds,
                headers=self._headers(headers),
                **kwargs,
            )
        except requests.RequestException as exc:
            raise APIClientError(str(exc)) from exc
        if not response.ok:
            detail = None
            try:
                detail = response.json().get("detail")
            except Exception:
                detail = response.text
            raise APIClientError(detail or f"Request failed with status {response.status_code}")
        if response.content:
            return response.json()
        return None

    def _binary_request(self, path):
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(
                url,
                timeout=self.timeout_seconds,
                headers=self._headers(),
            )
        except requests.RequestException as exc:
            raise APIClientError(str(exc)) from exc
        if not response.ok:
            detail = response.text or f"Request failed with status {response.status_code}"
            raise APIClientError(detail)
        return {
            "content": response.content,
            "content_type": response.headers.get("content-type", "application/octet-stream"),
            "filename": response.headers.get("content-disposition", ""),
        }

    def get_health(self):
        return self._request("GET", "/health")

    def get_analytics_summary(self):
        return self._request("GET", "/analytics/summary")

    def signup(self, payload):
        return self._request("POST", "/auth/signup", json=payload)

    def login(self, payload):
        return self._request("POST", "/auth/login", json=payload)

    def me(self):
        return self._request("GET", "/auth/me")

    def create_resume_text(self, payload):
        return self._request("POST", "/ingestion/resumes/text", json=payload)

    def create_resume_upload(self, data, files):
        return self._request("POST", "/ingestion/resumes/upload", data=data, files=files)

    def get_resume(self, resume_id):
        return self._request("GET", f"/ingestion/resumes/{resume_id}")

    def download_resume_file(self, resume_id):
        return self._binary_request(f"/ingestion/resumes/{resume_id}/file")

    def create_job_description(self, payload):
        return self._request("POST", "/ingestion/job-descriptions", json=payload)

    def get_job_description(self, job_description_id):
        return self._request("GET", f"/ingestion/job-descriptions/{job_description_id}")

    def generate_questions(self, payload):
        return self._request("POST", "/generation/questions", json=payload)

    def submit_answer(self, payload):
        return self._request("POST", "/answers", json=payload)

    def list_sessions(self):
        return self._request("GET", "/sessions")

    def get_session(self, session_id):
        return self._request("GET", f"/sessions/{session_id}")

    def create_session(self, payload):
        return self._request("POST", "/sessions", json=payload)
