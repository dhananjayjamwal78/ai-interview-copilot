import json
from abc import ABC, abstractmethod
from typing import Any
from urllib import request

from app.core.config import settings


class LLMProviderError(Exception):
    pass


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OllamaLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return settings.OLLAMA_CHAT_MODEL

    def generate(self, prompt: str) -> str:
        endpoint = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = json.dumps(
            {
                "model": settings.OLLAMA_CHAT_MODEL,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        req = request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(
                req,
                timeout=settings.OLLAMA_REQUEST_TIMEOUT_SECONDS,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise LLMProviderError(f"Ollama request failed: {exc}") from exc

        generated = body.get("response", "").strip()
        if not generated:
            raise LLMProviderError("Ollama returned an empty response.")
        return generated


class LLMService:
    def __init__(self) -> None:
        self.provider = self._resolve_provider()

    def _resolve_provider(self) -> BaseLLMProvider:
        if settings.MODEL_PROVIDER == "ollama":
            return OllamaLLMProvider()
        raise LLMProviderError(
            f"Unsupported MODEL_PROVIDER '{settings.MODEL_PROVIDER}'."
        )

    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)


llm_service = LLMService()
