from __future__ import annotations

import os
from typing import Any

import httpx


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.last_model = self.model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def respond(self, prompt: str) -> str:
        if not self.api_key:
            raise GeminiServiceError("Gemini is not configured on the backend.")

        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            },
        }
        models = [self.model]
        if self.model != "gemini-2.5-flash":
            models.append("gemini-2.5-flash")

        last_error: GeminiServiceError | None = None
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        url,
                        params={"key": self.api_key},
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
            except httpx.HTTPError as error:
                last_error = GeminiServiceError("Gemini request could not reach the API.")
                if model == models[-1]:
                    raise last_error from error
                continue
            if response.status_code != 200:
                last_error = GeminiServiceError(
                    f"Gemini API returned HTTP {response.status_code}: {response.text[:300]}"
                )
                if response.status_code not in (429, 500, 502, 503, 504) or model == models[-1]:
                    raise last_error
                continue

            try:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError, TypeError, ValueError) as error:
                last_error = GeminiServiceError("Gemini returned an unexpected response.")
                if model == models[-1]:
                    raise last_error from error
                continue
            if text:
                self.last_model = model
                return text
            last_error = GeminiServiceError("Gemini returned an empty response.")
            if model == models[-1]:
                raise last_error

        raise last_error or GeminiServiceError("Gemini request failed.")
