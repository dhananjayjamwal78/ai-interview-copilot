import os
import sys
from typing import Any, Optional
from pathlib import Path

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from utils.api_client import APIClient, APIClientError


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
BACKEND_BROWSER_URL = os.getenv("BACKEND_BROWSER_URL", "http://127.0.0.1:8000").rstrip("/")
client = APIClient(BACKEND_URL)

st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="IC",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --bg: #111216;
            --panel: rgba(24, 27, 34, 0.82);
            --panel-strong: rgba(18, 21, 27, 0.96);
            --panel-soft: rgba(255, 255, 255, 0.04);
            --line: rgba(255, 255, 255, 0.08);
            --text: #f5f1ea;
            --muted: #b8b3aa;
            --accent: #ff6b57;
            --accent-soft: rgba(255, 107, 87, 0.14);
            --accent-2: #e8c98d;
            --success: #5ed4a8;
            --warning: #f4bb67;
        }

        html, body, [class*="css"]  {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255,107,87,0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(232,201,141,0.12), transparent 26%),
                linear-gradient(180deg, #0d0f13 0%, #111216 52%, #15171c 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(18, 21, 27, 0.98) 0%, rgba(16, 18, 24, 0.96) 100%);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }

        [data-testid="stHeader"] {
            background: rgba(17, 18, 22, 0.55);
            backdrop-filter: blur(12px);
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.02em;
            color: var(--text);
        }

        .hero-shell {
            background:
                linear-gradient(135deg, rgba(255,107,87,0.16), rgba(232,201,141,0.08)),
                rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 1.6rem 1.7rem;
            box-shadow: 0 24px 80px rgba(0,0,0,0.24);
            margin-bottom: 1rem;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.38rem 0.8rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            background: var(--accent-soft);
            color: #ffd2c9;
            border: 1px solid rgba(255,107,87,0.2);
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 3.4rem;
            line-height: 0.96;
            font-weight: 800;
            margin-bottom: 0.9rem;
            max-width: 8.5em;
        }

        .hero-copy {
            max-width: 48rem;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .surface-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 18px 60px rgba(0,0,0,0.18);
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .section-copy {
            color: var(--muted);
            font-size: 0.96rem;
            margin-bottom: 0.9rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1rem 0.95rem;
            min-height: 126px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2rem;
            line-height: 1;
            font-weight: 700;
            color: var(--text);
        }

        .metric-note {
            color: var(--muted);
            margin-top: 0.45rem;
            font-size: 0.88rem;
        }

        .status-strip {
            background: rgba(94,212,168,0.12);
            border: 1px solid rgba(94,212,168,0.24);
            color: #d5fff0;
            padding: 0.9rem 1rem;
            border-radius: 18px;
            margin: 0.9rem 0 1rem;
            font-weight: 600;
        }

        .context-pill-row {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin: 0.8rem 0 1.2rem;
        }

        .context-pill {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.85rem 1rem;
            min-width: 180px;
        }

        .context-pill strong {
            display: block;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-bottom: 0.3rem;
        }

        .question-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1rem 1.05rem;
            margin-bottom: 0.9rem;
        }

        .question-meta {
            color: var(--accent-2);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.55rem;
        }

        .question-text {
            font-size: 1.05rem;
            line-height: 1.6;
            color: var(--text);
            margin-bottom: 0.55rem;
        }

        .subtle-banner {
            background: rgba(232,201,141,0.08);
            border: 1px solid rgba(232,201,141,0.18);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            color: #f2e1bb;
            margin-bottom: 1rem;
        }

        .weak-card {
            background: rgba(255,255,255,0.025);
            border: 1px solid var(--line);
            border-left: 3px solid var(--accent);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
        }

        .mini-heading {
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-bottom: 0.4rem;
        }

        .rail-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .quick-action {
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.03);
            border-radius: 22px;
            padding: 0.95rem 1rem;
            min-height: 138px;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        .stTextInput input,
        .stTextArea textarea {
            background: rgba(255,255,255,0.03) !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {
            border-radius: 999px !important;
            border: none !important;
            background: linear-gradient(135deg, #ff6b57 0%, #ff8a6b 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 0.65rem 1.1rem !important;
            box-shadow: 0 12px 30px rgba(255,107,87,0.25);
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.03);
            border-radius: 999px;
            padding: 0.55rem 0.95rem;
            border: 1px solid var(--line);
        }

        .stDataFrame, div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--line);
        }

        [data-testid="stMetric"] {
            background: transparent;
        }

        .footer-note {
            color: var(--muted);
            font-size: 0.88rem;
            margin-top: 1rem;
        }

        .auth-shell {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 1rem;
            align-items: stretch;
            margin-top: 1rem;
        }

        .auth-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 1.4rem;
            box-shadow: 0 18px 60px rgba(0,0,0,0.18);
        }

        .auth-feature {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }

        .auth-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            line-height: 1.05;
            margin-bottom: 0.7rem;
        }

        .auth-copy {
            color: var(--muted);
            line-height: 1.7;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    defaults = {
        "auth_token": "",
        "current_user": None,
        "analytics_summary": None,
        "session_library": [],
        "resume_preview": None,
        "jd_preview": None,
        "nav_page": "Dashboard",
        "workspace_focus": "",
        "active_resume_id": "",
        "active_job_description_id": "",
        "active_session_id": "",
        "last_generation": None,
        "last_answer": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state["auth_token"]:
        client.set_token(st.session_state["auth_token"])
        if st.session_state["current_user"] is None:
            try:
                st.session_state["current_user"] = client.me()
            except APIClientError:
                logout()


def set_auth(auth_payload: dict[str, Any]):
    st.session_state["auth_token"] = auth_payload["access_token"]
    st.session_state["current_user"] = {
        "user_id": auth_payload["user_id"],
        "email": auth_payload["email"],
        "full_name": auth_payload["full_name"],
    }
    client.set_token(auth_payload["access_token"])


def logout():
    st.session_state["auth_token"] = ""
    st.session_state["current_user"] = None
    st.session_state["analytics_summary"] = None
    st.session_state["session_library"] = []
    st.session_state["resume_preview"] = None
    st.session_state["jd_preview"] = None
    st.session_state["nav_page"] = "Dashboard"
    st.session_state["workspace_focus"] = ""
    st.session_state["active_resume_id"] = ""
    st.session_state["active_job_description_id"] = ""
    st.session_state["active_session_id"] = ""
    st.session_state["last_generation"] = None
    st.session_state["last_answer"] = None
    client.set_token(None)


def show_api_error(exc: Exception):
    st.error(str(exc))


def require_auth() -> bool:
    if not st.session_state["auth_token"]:
        st.info("Sign in from the home screen to continue into your interview workspace.")
        return False
    return True


def short_id(value: str, fallback: str = "Not set") -> str:
    if not value:
        return fallback
    return value[:8]


def load_session_library() -> list[dict[str, Any]]:
    if not st.session_state["current_user"]:
        return []
    try:
        sessions = client.list_sessions()
    except APIClientError as exc:
        show_api_error(exc)
        return st.session_state.get("session_library", [])
    st.session_state["session_library"] = sessions
    return sessions


def get_session_number(session_id: str) -> Optional[int]:
    if not session_id:
        return None
    sessions = st.session_state.get("session_library") or load_session_library()
    chronological = sorted(sessions, key=lambda item: item["created_at"])
    for index, session in enumerate(chronological, start=1):
        if session["id"] == session_id:
            return index
    return None


def format_session_label(session_id: str) -> str:
    session_number = get_session_number(session_id)
    if session_number is not None:
        return f"Session {session_number}"
    return f"Session {short_id(session_id)}"


def build_answer_guide(question: dict[str, Any]) -> str:
    category = (question.get("category") or "").lower()
    if category == "technical":
        return "Ideal answer: define the concept, explain how it works, mention one tradeoff, and give one concrete example."
    if category == "project-based":
        return "Ideal answer: describe the goal, your role, the main decision, the tools used, and one measurable result."
    if category == "behavioral":
        return "Ideal answer: use STAR in short form: situation, task, action, and result."
    return "Ideal answer: explain why you fit the role, what you can contribute, and one short example."


def jump_to_page(page: str, focus: str = "") -> None:
    st.session_state["nav_page"] = page
    if focus:
        st.session_state["workspace_focus"] = focus
    st.rerun()


def get_generation_hint(question: dict[str, Any]) -> Optional[dict[str, str]]:
    last_generation = st.session_state.get("last_generation") or {}
    generated_questions = last_generation.get("questions") or []
    for generated in generated_questions:
        if generated.get("prompt") == question.get("prompt"):
            return {
                "suggested_answer": generated.get("suggested_answer", "").strip(),
                "answer_example": generated.get("answer_example", "").strip(),
            }
    return None


def render_hero():
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-kicker">AI Interview Copilot</div>
            <div class="hero-title">AI Interview Copilot</div>
            <div class="hero-copy">
                A professional interview preparation workspace for turning your resume, target role, and practice answers into tailored sessions and structured feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card_html(label: str, value: Any, note: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


def render_section_heading(title: str, copy: str):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def render_context_pills():
    last_generation = st.session_state["last_generation"]
    generated_count = last_generation["generated_count"] if last_generation else 0
    st.markdown(
        f"""
        <div class="context-pill-row">
            <div class="context-pill"><strong>Resume</strong>{short_id(st.session_state["active_resume_id"])}</div>
            <div class="context-pill"><strong>Job Description</strong>{short_id(st.session_state["active_job_description_id"])}</div>
            <div class="context-pill"><strong>Session</strong>{short_id(st.session_state["active_session_id"])}</div>
            <div class="context-pill"><strong>Generated</strong>{generated_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_control_sidebar(page_options: list[str]) -> str:
    current_user = st.session_state["current_user"]
    if not current_user:
        return "Auth"

    with st.sidebar:
        st.markdown("## Control Deck")
        st.caption("Use this panel for navigation and workspace context.")
        st.markdown('<div class="rail-card">', unsafe_allow_html=True)
        st.markdown("### Account")
        st.success(f"Signed in as {current_user['full_name']}")
        st.caption(current_user["email"])
        if st.button("Log Out", use_container_width=True):
            logout()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="rail-card">', unsafe_allow_html=True)
        st.markdown("### Workspace")
        st.caption("Open the linked records directly from here.")
        if st.session_state["active_resume_id"]:
            if st.button(
                f"Open Resume · {short_id(st.session_state['active_resume_id'])}",
                use_container_width=True,
                key="open_resume_link",
            ):
                jump_to_page("Documents", "resume")
        if st.session_state["active_job_description_id"]:
            if st.button(
                f"Open Job Description · {short_id(st.session_state['active_job_description_id'])}",
                use_container_width=True,
                key="open_jd_link",
            ):
                jump_to_page("Documents", "job_description")
        if st.session_state["active_session_id"]:
            if st.button(
                f"Open {format_session_label(st.session_state['active_session_id'])}",
                use_container_width=True,
                key="open_session_link",
            ):
                jump_to_page("History", "session")
        st.markdown("</div>", unsafe_allow_html=True)
        current_page = st.session_state.get("nav_page", "Dashboard")
        if current_page not in page_options:
            current_page = "Dashboard"
        selected_page = st.radio(
            "Navigate",
            page_options,
            label_visibility="visible",
            index=page_options.index(current_page),
        )
        st.session_state["nav_page"] = selected_page
        return selected_page


def sync_linked_context() -> None:
    focus = st.session_state.get("workspace_focus")
    resume_id = st.session_state.get("active_resume_id")
    resume_preview = st.session_state.get("resume_preview")
    if focus == "resume" and resume_id and (
        not resume_preview or resume_preview.get("id") != resume_id
    ):
        try:
            st.session_state["resume_preview"] = client.get_resume(resume_id)
        except APIClientError as exc:
            show_api_error(exc)

    job_description_id = st.session_state.get("active_job_description_id")
    jd_preview = st.session_state.get("jd_preview")
    if focus == "job_description" and job_description_id and (
        not jd_preview or jd_preview.get("id") != job_description_id
    ):
        try:
            st.session_state["jd_preview"] = client.get_job_description(job_description_id)
        except APIClientError as exc:
            show_api_error(exc)


def render_auth_landing():
    render_hero()
    auth_left, auth_right = st.columns([1.08, 0.92], gap="large")

    with auth_left:
        st.markdown(
            """
            <div class="auth-panel">
                <div class="auth-title">Professional interview preparation, organized around your workflow.</div>
                <div class="auth-copy">
                    Build a guided practice flow from your resume, optionally add a target role description, generate tailored interview questions, and review your progress in one place.
                </div>
                <div class="auth-feature">
                    <div class="mini-heading">Step 1</div>
                    <strong>Add your resume first.</strong>
                    <div class="footer-note">This is the core input for personalized interview preparation.</div>
                </div>
                <div class="auth-feature">
                    <div class="mini-heading">Step 2</div>
                    <strong>Add a job description only if you want tighter role-specific practice.</strong>
                    <div class="footer-note">Resume-only practice is fully supported and often the fastest way to start.</div>
                </div>
                <div class="auth-feature">
                    <div class="mini-heading">Step 3</div>
                    <strong>Generate, answer, and review.</strong>
                    <div class="footer-note">Each session stays linked to your account so progress can build over time.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with auth_right:
        st.markdown('<div class="auth-panel">', unsafe_allow_html=True)
        auth_tab = st.radio("Access", ["Login", "Sign Up"], horizontal=True)
        if auth_tab == "Login":
            st.markdown("### Log In")
            st.caption("Continue into your saved interview workspace.")
            with st.form("login_form_home"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                if not email.strip() or not password:
                    st.warning("Enter both email and password.")
                else:
                    try:
                        response = client.login(
                            {"email": email.strip().lower(), "password": password}
                        )
                        set_auth(response)
                        st.rerun()
                    except APIClientError as exc:
                        show_api_error(exc)
        else:
            st.markdown("### Create Account")
            st.caption("Start a personal workspace for interview preparation.")
            with st.form("signup_form_home"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not full_name.strip() or not email.strip() or not password:
                    st.warning("Full name, email, and password are required.")
                else:
                    try:
                        response = client.signup(
                            {
                                "full_name": full_name.strip(),
                                "email": email.strip().lower(),
                                "password": password,
                            }
                        )
                        set_auth(response)
                        st.rerun()
                    except APIClientError as exc:
                        show_api_error(exc)
        st.markdown("</div>", unsafe_allow_html=True)

def render_dashboard():
    render_hero()
    render_section_heading(
        "Overview",
        "A clean snapshot of your interview progress. Use the dedicated pages in the control deck for uploads, generation, answering, and history.",
    )

    if not st.session_state["current_user"]:
        return

    try:
        analytics = client.get_analytics_summary()
        st.session_state["analytics_summary"] = analytics
    except APIClientError as exc:
        show_api_error(exc)
        analytics = None

    if analytics is None:
        return

    st.markdown('<div class="surface-card">', unsafe_allow_html=True)
    render_section_heading(
        "Performance snapshot",
        "These metrics summarize how you are doing across completed interview attempts, not just a single session.",
    )

    performance_cols = st.columns(4, gap="medium")
    performance_cols[0].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Questions Attempted</div>
            <div class="metric-value">{analytics['questions_attempted']}</div>
            <div class="metric-note">Across all saved interview sessions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    performance_cols[1].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value">{analytics['average_score']}</div>
            <div class="metric-note">Your current overall answer quality signal.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    performance_cols[2].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Completed Sessions</div>
            <div class="metric-value">{analytics['completed_sessions']}</div>
            <div class="metric-note">Finished interview rounds in your history.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    performance_cols[3].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Answers Submitted</div>
            <div class="metric-value">{analytics['answers_submitted']}</div>
            <div class="metric-note">Total answers reviewed by the evaluator.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.25, 0.95], gap="large")

    with left:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Category performance",
            "Track how different question types are trending so you can practice the right areas next.",
        )
        if analytics["category_performance"]:
            st.dataframe(
                analytics["category_performance"],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Answer a few generated questions to unlock category-level insights.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Weak areas",
            "These recommendations are derived from your category scores and answer-quality dimensions.",
        )
        if analytics["weak_areas"]:
            selected_weak_area = st.selectbox(
                "Choose a weak area",
                options=analytics["weak_areas"],
                format_func=lambda item: (
                    f"{item['area']} · {item['average_score']}"
                ),
            )
            st.markdown(
                f"""
                <div class="weak-card">
                    <div class="mini-heading">{selected_weak_area['metric']}</div>
                    <strong>{selected_weak_area['area']}</strong><br/>
                    Average score: {selected_weak_area['average_score']}<br/><br/>
                    {selected_weak_area['recommendation']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.success("No obvious weak areas yet. Keep building data through more interview runs.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_ingestion():
    if not require_auth():
        return

    sync_linked_context()
    render_section_heading(
        "Context intake",
        "Start with your resume. If you want role-specific tailoring, you can optionally add a job description before moving to question generation.",
    )
    focus = st.session_state.get("workspace_focus")
    if focus == "resume":
        st.markdown(
            '<div class="subtle-banner">Showing your linked resume and its parsed signals below.</div>',
            unsafe_allow_html=True,
        )
    elif focus == "job_description":
        st.markdown(
            '<div class="subtle-banner">Showing your linked job description and its parsed signals below.</div>',
            unsafe_allow_html=True,
        )
    use_job_description = st.toggle(
        "I want to add a job description for tighter role-specific questions",
        value=bool(st.session_state["active_job_description_id"]) or focus == "job_description",
    )
    tabs = st.tabs(["Resume", "Job Description (Optional)" if use_job_description else "Resume Only Flow"])

    with tabs[0]:
        left, right = st.columns([0.95, 1.05], gap="large")
        with left:
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            st.markdown("### Resume intake")
            st.caption("Choose between quick text input and file upload.")
            resume_mode = st.radio("Resume Input Type", ["Text", "File Upload"], horizontal=True)
            if resume_mode == "Text":
                with st.form("resume_text_form"):
                    title = st.text_input("Resume Title", value="Primary Resume")
                    original_filename = st.text_input("Original Filename", value="resume.txt")
                    resume_text = st.text_area("Resume Text", height=280)
                    submitted = st.form_submit_button("Save Resume Text")
                if submitted:
                    try:
                        result = client.create_resume_text(
                            {
                                "title": title,
                                "original_filename": original_filename,
                                "resume_text": resume_text,
                            }
                        )
                        st.session_state["active_resume_id"] = result["id"]
                        st.success("Resume text ingested successfully.")
                        st.session_state["resume_preview"] = result
                        st.session_state["workspace_focus"] = "resume"
                        if not use_job_description:
                            jump_to_page("Documents", "resume")
                    except APIClientError as exc:
                        show_api_error(exc)
            else:
                with st.form("resume_upload_form"):
                    title = st.text_input("Resume Title", value="Uploaded Resume")
                    resume_file = st.file_uploader("Upload Resume File", type=["pdf", "txt", "md"])
                    submitted = st.form_submit_button("Upload Resume")
                if submitted:
                    if resume_file is None:
                        st.warning("Please choose a resume file.")
                    else:
                        try:
                            result = client.create_resume_upload(
                                data={"title": title},
                                files={
                                    "file": (
                                        resume_file.name,
                                        resume_file.getvalue(),
                                        resume_file.type or "application/octet-stream",
                                    )
                                },
                            )
                            st.session_state["active_resume_id"] = result["id"]
                            st.success("Resume uploaded successfully.")
                            st.session_state["resume_preview"] = result
                            st.session_state["workspace_focus"] = "resume"
                            if not use_job_description:
                                jump_to_page("Documents", "resume")
                        except APIClientError as exc:
                            show_api_error(exc)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            render_section_heading(
                "Linked resume",
                "Review the saved resume text and the parsed signals that feed your interview rounds.",
            )
            preview = st.session_state.get("resume_preview")
            if preview:
                st.markdown(f"**Resume ID**  `{preview['id']}`")
                st.markdown(f"**Title**  {preview['title']}")
                st.markdown(f"**Filename**  {preview['original_filename']}")
                with st.expander("View saved resume", expanded=True):
                    st.text_area(
                        "Resume content",
                        value=preview.get("extracted_text", ""),
                        height=280,
                        disabled=True,
                    )
                st.markdown("**Parsed signals**")
                st.json(preview["parsed_data"])
            else:
                st.info("Save a resume to preview the parsed structure here.")
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        if not use_job_description:
            st.markdown(
                '<div class="subtle-banner">You can skip the job description and continue with resume-only practice. When you are ready, move to the Generate section.</div>',
                unsafe_allow_html=True,
            )
            return
        left, right = st.columns([0.95, 1.05], gap="large")
        with left:
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            st.markdown("### Job brief intake")
            with st.form("job_description_form"):
                role_title = st.text_input("Role Title")
                company_name = st.text_input("Company Name")
                source_url = st.text_input("Source URL")
                raw_text = st.text_area("Job Description Text", height=310)
                submitted = st.form_submit_button("Save Job Description")
            if submitted:
                try:
                    result = client.create_job_description(
                        {
                            "role_title": role_title,
                            "company_name": company_name or None,
                            "source_url": source_url or None,
                            "raw_text": raw_text,
                        }
                    )
                    st.session_state["active_job_description_id"] = result["id"]
                    st.success("Job description ingested successfully.")
                    st.session_state["jd_preview"] = result
                    st.session_state["workspace_focus"] = "job_description"
                    jump_to_page("Documents", "job_description")
                except APIClientError as exc:
                    show_api_error(exc)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            render_section_heading(
                "Linked job description",
                "Review the saved job brief and the parsed requirements that shape the generated round.",
            )
            preview = st.session_state.get("jd_preview")
            if preview:
                st.markdown(f"**Job Description ID**  `{preview['id']}`")
                st.markdown(f"**Role**  {preview['role_title']}")
                if preview.get("company_name"):
                    st.markdown(f"**Company**  {preview['company_name']}")
                with st.expander("View saved job description", expanded=True):
                    st.text_area(
                        "Job description content",
                        value=preview.get("raw_text", ""),
                        height=280,
                        disabled=True,
                    )
                st.markdown("**Parsed signals**")
                st.json(preview["parsed_data"])
            else:
                st.info("Save a job description to preview the parsed structure here.")
            st.markdown("</div>", unsafe_allow_html=True)


def render_documents():
    if not require_auth():
        return

    sync_linked_context()
    render_section_heading(
        "Documents",
        "Review the linked resume and job description in a cleaner document-style view.",
    )

    focus = st.session_state.get("workspace_focus")
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Resume",
            "See the uploaded document when available, or the saved resume text if this record was entered directly.",
        )
        resume_preview = st.session_state.get("resume_preview")
        if resume_preview:
            st.markdown(f"**Title**  {resume_preview['title']}")
            st.markdown(f"**Filename**  {resume_preview['original_filename']}")
            if focus == "resume":
                st.success("This is the currently linked resume.")

            if resume_preview.get("file_path"):
                preview_url = (
                    f"{BACKEND_BROWSER_URL}/ingestion/resumes/{resume_preview['id']}/file"
                    f"?preview_token={st.session_state['auth_token']}"
                )
                is_pdf = resume_preview["original_filename"].lower().endswith(".pdf")
                if is_pdf:
                    resume_action_cols = st.columns([0.52, 0.48], gap="small")
                    with resume_action_cols[0]:
                        st.markdown(
                            f"""
                            <a href="{preview_url}" target="_blank" style="
                                display:block;
                                text-align:center;
                                padding:0.85rem 1.1rem;
                                border-radius:999px;
                                background:linear-gradient(135deg, #ff6b57 0%, #ff8a6b 100%);
                                color:white;
                                text-decoration:none;
                                font-weight:700;
                                margin-bottom:1rem;
                            ">Open Resume PDF</a>
                            """,
                            unsafe_allow_html=True,
                        )
                    with resume_action_cols[1]:
                        if st.button("Go to Generate", use_container_width=True, key="documents_to_generate"):
                            jump_to_page("Generate", "resume")
                    st.caption("The PDF will open in a separate browser tab for full-size preview.")
                else:
                    st.info("This uploaded file is not a PDF, so the saved extracted text is shown below.")
                    st.text_area(
                        "Document preview",
                        value=resume_preview.get("extracted_text", ""),
                        height=320,
                        disabled=True,
                    )
            else:
                st.text_area(
                    "Saved resume",
                    value=resume_preview.get("extracted_text", ""),
                    height=320,
                    disabled=True,
                )
        else:
            st.info("No resume is linked yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Job description",
            "This remains optional. If you linked one, you can review the saved brief here.",
        )
        jd_preview = st.session_state.get("jd_preview")
        if jd_preview:
            st.markdown(f"**Role**  {jd_preview['role_title']}")
            if jd_preview.get("company_name"):
                st.markdown(f"**Company**  {jd_preview['company_name']}")
            if focus == "job_description":
                st.success("This is the currently linked job description.")
            st.text_area(
                "Saved job description",
                value=jd_preview.get("raw_text", ""),
                height=320,
                disabled=True,
            )
        else:
            st.info("No job description is linked yet.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_generation():
    if not require_auth():
        return

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Question generator",
            "Generate a professional interview round from your uploaded context. A job description is optional, and resume-only practice works well too.",
        )
        with st.form("generation_form"):
            resume_id = st.text_input("Resume ID", value=st.session_state["active_resume_id"])
            job_description_id = st.text_input(
                "Job Description ID",
                value=st.session_state["active_job_description_id"],
            )
            session_id = st.text_input(
                "Existing Session ID (Optional)",
                value=st.session_state["active_session_id"],
            )
            session_title = st.text_input("Session Title", value="Interview Practice Session")
            categories = st.multiselect(
                "Question Categories",
                ["technical", "project-based", "behavioral", "hr/general"],
                default=["technical", "project-based", "behavioral", "hr/general"],
            )
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
            question_count = st.slider("Question Count", min_value=1, max_value=12, value=3)
            submitted = st.form_submit_button("Generate Questions", use_container_width=True)
        if submitted:
            try:
                result = client.generate_questions(
                    {
                        "resume_id": resume_id or None,
                        "job_description_id": job_description_id or None,
                        "interview_session_id": session_id or None,
                        "categories": categories,
                        "difficulty": difficulty,
                        "question_count": question_count,
                        "session_title": session_title or None,
                    }
                )
                st.session_state["active_session_id"] = result["interview_session_id"]
                st.session_state["last_generation"] = result
                st.success("Questions generated successfully. Moving you to the answer workspace.")
                jump_to_page("Answer", "session")
            except APIClientError as exc:
                show_api_error(exc)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Generated round",
            "Your latest question set appears here. Move into the answer view when you are ready to respond.",
        )
        result = st.session_state["last_generation"]
        if result:
            session_label = format_session_label(result["interview_session_id"])
            st.markdown(
                f"""
                <div class="subtle-banner">
                    <strong>{session_label}</strong> |
                    Provider <strong>{result['provider']}</strong> |
                    Model <strong>{result['model']}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for index, question in enumerate(result["questions"], start=1):
                st.markdown(
                    f"""
                    <div class="question-card">
                        <div class="question-meta">Question {index} · {question['category']} · {question['difficulty']}</div>
                        <div class="question-text">{question['prompt']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Generate a question set to preview the round here.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_answering():
    if not require_auth():
        return

    render_section_heading(
        "Answer workspace",
        "Load a session, work through each question, and get feedback directly in the flow.",
    )
    top_cols = st.columns([1.1, 0.35], gap="medium")
    active_session_id = top_cols[0].text_input(
        "Session ID to Work On",
        value=st.session_state["active_session_id"],
    )
    if top_cols[1].button("Load Session", use_container_width=True):
        st.session_state["active_session_id"] = active_session_id

    if not st.session_state["active_session_id"]:
        st.info("Generate or select a session first.")
        return

    try:
        session = client.get_session(st.session_state["active_session_id"])
    except APIClientError as exc:
        show_api_error(exc)
        return

    session_label = format_session_label(session["id"])
    st.markdown('<div class="surface-card">', unsafe_allow_html=True)
    st.markdown(f"### {session_label}")
    st.caption(session["title"])
    st.caption(f"Target role: {session.get('target_role') or 'Not set'}")
    st.markdown("</div>", unsafe_allow_html=True)

    for question in session["questions"]:
        generation_hint = get_generation_hint(question)
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="question-meta">
                Question {question.get('display_order') or 1} · {question.get('category') or 'uncategorized'} · {question.get('difficulty') or 'unspecified'}
            </div>
            <div class="question-text">{question['prompt']}</div>
            """,
            unsafe_allow_html=True,
        )

        existing_answers = question.get("answers", [])
        if existing_answers:
            latest = existing_answers[-1]
            st.success("Answer already submitted for this question.")
            st.write(latest["response_text"])
            if generation_hint and generation_hint.get("suggested_answer"):
                st.info(f"Suggested answer: {generation_hint['suggested_answer']}")
                if generation_hint.get("answer_example"):
                    st.caption(f"Example: {generation_hint['answer_example']}")
            else:
                st.caption(build_answer_guide(question))
            if latest.get("evaluations"):
                evaluation = latest["evaluations"][-1]
                feedback_cols = st.columns(4)
                feedback_cols[0].metric("Score", evaluation.get("score"))
                feedback_cols[1].metric("Correctness", evaluation.get("correctness_score"))
                feedback_cols[2].metric("Clarity", evaluation.get("clarity_score"))
                feedback_cols[3].metric("Completeness", evaluation.get("completeness_score"))
                if evaluation.get("rubric_feedback"):
                    st.caption(evaluation["rubric_feedback"])
                if evaluation.get("improvement_suggestions"):
                    st.info(evaluation["improvement_suggestions"])
        else:
            with st.form(f"answer_form_{question['id']}"):
                response_text = st.text_area(
                    "Your Answer",
                    height=160,
                    key=f"answer_text_{question['id']}",
                )
                submit_answer = st.form_submit_button("Submit Answer", use_container_width=True)
            if submit_answer:
                try:
                    result = client.submit_answer(
                        {
                            "question_id": question["id"],
                            "response_text": response_text,
                        }
                    )
                    st.session_state["last_answer"] = result
                    st.success("Answer submitted and evaluated.")
                    st.rerun()
                except APIClientError as exc:
                    show_api_error(exc)
        st.markdown("</div>", unsafe_allow_html=True)


def render_history():
    if not require_auth():
        return

    left, right = st.columns([0.85, 1.15], gap="large")

    with left:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            "Session library",
            "Review past interview runs and reopen them when you want to continue or compare progress.",
        )
        sessions = load_session_library()

        if not sessions:
            st.info("No sessions found yet.")
        else:
            chronological = sorted(sessions, key=lambda item: item["created_at"])
            numbered_sessions = {
                session["id"]: index
                for index, session in enumerate(chronological, start=1)
            }
            selected = st.selectbox(
                "Choose a Session",
                options=sessions,
                format_func=lambda session: (
                    f"Session {numbered_sessions.get(session['id'], '?')} | {session['title']} | {session['status']}"
                ),
            )
            if selected:
                st.session_state["active_session_id"] = selected["id"]
                st.session_state["workspace_focus"] = "session"
        st.markdown("</div>", unsafe_allow_html=True)

        analytics = st.session_state.get("analytics_summary")
        if analytics:
            st.markdown('<div class="surface-card" style="margin-top: 1rem;">', unsafe_allow_html=True)
            render_section_heading(
                "Progress snapshot",
                "A compact summary of your current trajectory across all stored interview practice.",
            )
            st.write(
                f"You have attempted `{analytics['questions_attempted']}` questions with an average score of `{analytics['average_score']}`."
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if not st.session_state["active_session_id"]:
            st.info("Select a session to open the detailed review.")
            return
        try:
            detail = client.get_session(st.session_state["active_session_id"])
        except APIClientError as exc:
            show_api_error(exc)
            return

        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        render_section_heading(
            format_session_label(detail["id"]),
            "Detailed review of prompts, submitted answers, and evaluation feedback.",
        )
        st.caption(detail["title"])
        st.write(f"Target role: `{detail.get('target_role') or 'Not set'}`")
        st.write(f"Target skills: `{', '.join(detail.get('target_skills', [])) or 'None'}`")
        st.write(f"Question categories: `{', '.join(detail.get('question_categories', [])) or 'None'}`")
        st.markdown("</div>", unsafe_allow_html=True)

        for question in detail["questions"]:
            with st.expander(f"Question {question.get('display_order') or 1}: {question['prompt']}"):
                st.caption(
                    f"{question.get('category') or 'uncategorized'} | {question.get('difficulty') or 'unspecified'}"
                )
                if not question["answers"]:
                    st.info("No answers submitted yet.")
                for answer in question["answers"]:
                    st.write(answer["response_text"])
                    for evaluation in answer["evaluations"]:
                        score_cols = st.columns(4)
                        score_cols[0].metric("Score", evaluation.get("score"))
                        score_cols[1].metric("Correctness", evaluation.get("correctness_score"))
                        score_cols[2].metric("Clarity", evaluation.get("clarity_score"))
                        score_cols[3].metric("Completeness", evaluation.get("completeness_score"))
                        if evaluation.get("semantic_similarity_score") is not None:
                            st.write(f"Similarity: {evaluation.get('semantic_similarity_score')}")
                        if evaluation.get("rubric_feedback"):
                            st.caption(evaluation["rubric_feedback"])
                        if evaluation.get("improvement_suggestions"):
                            st.info(evaluation["improvement_suggestions"])


inject_styles()
init_state()

page_options = ["Dashboard", "Upload", "Documents", "Generate", "Answer", "History"]
page = render_control_sidebar(page_options)

if page == "Auth":
    render_auth_landing()
elif page == "Dashboard":
    render_dashboard()
elif page == "Upload":
    render_ingestion()
elif page == "Documents":
    render_documents()
elif page == "Generate":
    render_generation()
elif page == "Answer":
    render_answering()
else:
    render_history()
