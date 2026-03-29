from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Interview Copilot Backend"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Free and open-source AI interview preparation backend"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = Field(default=8000, ge=1, le=65535)
    RUN_RELOAD: bool = False
    ENABLE_DOCS: bool = True
    ENABLE_REDOC: bool = False
    ENABLE_OPENAPI: bool = True
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@db:5432/ai_interview_copilot"
    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = Field(default=5 * 1024 * 1024, ge=1024)
    MODEL_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_REQUEST_TIMEOUT_SECONDS: int = Field(default=180, ge=30, le=1800)
    CORS_ALLOW_ORIGINS: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = Field(default="GET,POST,PUT,DELETE,OPTIONS")
    CORS_ALLOW_HEADERS: str = Field(default="*")
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=5)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @staticmethod
    def _split_csv(raw_value: str) -> list[str]:
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return self._split_csv(self.CORS_ALLOW_ORIGINS)

    @property
    def cors_allow_methods_list(self) -> list[str]:
        return self._split_csv(self.CORS_ALLOW_METHODS)

    @property
    def cors_allow_headers_list(self) -> list[str]:
        return self._split_csv(self.CORS_ALLOW_HEADERS)


settings = Settings()
