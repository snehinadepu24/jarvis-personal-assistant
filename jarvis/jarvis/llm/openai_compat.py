from __future__ import annotations

import json
import os
import time

import httpx

from jarvis.llm.base import LLMError, Usage, extract_json
from jarvis.llm.costs import COSTS


class OpenAICompatLLM:
    provider = "openai"

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None, base_url: str = "https://api.openai.com/v1"):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.name = f"openai:{model}"
        self._n = 0

    async def complete_json(self, system: str, messages: list[dict], schema: dict, *, thinking: str = "low") -> tuple[dict, Usage]:
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY is not set")

        user_text = "\n\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        user_text += "\n\nReturn exactly ONE JSON object valid against the schema above. No prose, no code fences."

        self._n += 1
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        t0 = time.monotonic()
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code != 200:
                raise LLMError(f"OpenAI API error {resp.status_code}: {resp.text}")
            reply = resp.json()["choices"][0]["message"]["content"]

        latency = (time.monotonic() - t0) * 1000.0
        return extract_json(reply), COSTS.usage(self.model, user_text, reply, latency)


class AnthropicLLM:
    provider = "anthropic"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.name = f"anthropic:{model}"
        self._n = 0

    async def complete_json(self, system: str, messages: list[dict], schema: dict, *, thinking: str = "low") -> tuple[dict, Usage]:
        if not self.api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")

        user_text = "\n\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        user_text += "\n\nReturn exactly ONE JSON object valid against the schema above. No prose, no code fences."

        self._n += 1
        payload = {
            "model": self.model,
            "system": system,
            "max_tokens": 2048,
            "messages": [
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.2,
        }

        t0 = time.monotonic()
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code != 200:
                raise LLMError(f"Anthropic API error {resp.status_code}: {resp.text}")
            reply = resp.json()["content"][0]["text"]

        latency = (time.monotonic() - t0) * 1000.0
        return extract_json(reply), COSTS.usage(self.model, user_text, reply, latency)
