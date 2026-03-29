import json
from abc import ABC, abstractmethod
from typing import Any
from urllib import error, request

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


class HuggingFaceLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def model_name(self) -> str:
        return settings.HF_CHAT_MODEL

    def generate(self, prompt: str) -> str:
        if not settings.HF_API_TOKEN:
            raise LLMProviderError("HF_API_TOKEN is required when MODEL_PROVIDER=huggingface.")

        payload = json.dumps(
            {
                "model": settings.HF_CHAT_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": 1200,
            }
        ).encode("utf-8")
        req = request.Request(
            settings.HF_BASE_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            },
            method="POST",
        )
        try:
            with request.urlopen(
                req,
                timeout=settings.HF_REQUEST_TIMEOUT_SECONDS,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            raise LLMProviderError(f"Hugging Face request failed: {detail}") from exc
        except Exception as exc:
            raise LLMProviderError(f"Hugging Face request failed: {exc}") from exc

        choices = body.get("choices") or []
        if not choices:
            raise LLMProviderError("Hugging Face returned no choices.")
        message = choices[0].get("message") or {}
        generated = str(message.get("content") or "").strip()
        if not generated:
            raise LLMProviderError("Hugging Face returned an empty response.")
        return generated


class LLMService:
    def __init__(self) -> None:
        self.provider = self._resolve_provider()

    def _resolve_provider(self) -> BaseLLMProvider:
        if settings.MODEL_PROVIDER == "ollama":
            return OllamaLLMProvider()
        if settings.MODEL_PROVIDER == "huggingface":
            return HuggingFaceLLMProvider()
        raise LLMProviderError(
            f"Unsupported MODEL_PROVIDER '{settings.MODEL_PROVIDER}'."
        )

    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)


llm_service = LLMService()
