import json
from abc import ABC, abstractmethod
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

    def _chat_completion_request(
        self,
        *,
        endpoint: str,
        api_key: str,
        model: str,
        prompt: str,
        timeout_seconds: int,
        extra_headers: dict[str, str] | None = None,
    ) -> str:
        payload = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if extra_headers:
            headers.update(extra_headers)
        req = request.Request(
            endpoint,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            raise LLMProviderError(
                f"{self.provider_name.title()} request failed: {detail}"
            ) from exc
        except Exception as exc:
            raise LLMProviderError(
                f"{self.provider_name.title()} request failed: {exc}"
            ) from exc

        choices = body.get("choices") or []
        if not choices:
            raise LLMProviderError(f"{self.provider_name.title()} returned no choices.")
        message = choices[0].get("message") or {}
        generated = str(message.get("content") or "").strip()
        if not generated:
            raise LLMProviderError(
                f"{self.provider_name.title()} returned an empty response."
            )
        return generated


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
        return self._chat_completion_request(
            endpoint=settings.HF_BASE_URL,
            api_key=settings.HF_API_TOKEN,
            model=settings.HF_CHAT_MODEL,
            prompt=prompt,
            timeout_seconds=settings.HF_REQUEST_TIMEOUT_SECONDS,
        )


class OpenRouterLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model_name(self) -> str:
        return settings.OPENROUTER_MODEL

    def generate(self, prompt: str) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise LLMProviderError(
                "OPENROUTER_API_KEY is required when MODEL_PROVIDER=openrouter."
            )

        extra_headers: dict[str, str] = {}
        if settings.OPENROUTER_SITE_URL:
            extra_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            extra_headers["X-Title"] = settings.OPENROUTER_APP_NAME

        return self._chat_completion_request(
            endpoint=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            model=settings.OPENROUTER_MODEL,
            prompt=prompt,
            timeout_seconds=settings.OPENROUTER_REQUEST_TIMEOUT_SECONDS,
            extra_headers=extra_headers,
        )


class LLMService:
    def __init__(self) -> None:
        self.provider = self._resolve_provider()

    def _resolve_provider(self) -> BaseLLMProvider:
        if settings.MODEL_PROVIDER == "ollama":
            return OllamaLLMProvider()
        if settings.MODEL_PROVIDER == "huggingface":
            return HuggingFaceLLMProvider()
        if settings.MODEL_PROVIDER == "openrouter":
            return OpenRouterLLMProvider()
        raise LLMProviderError(
            f"Unsupported MODEL_PROVIDER '{settings.MODEL_PROVIDER}'."
        )

    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)


llm_service = LLMService()
