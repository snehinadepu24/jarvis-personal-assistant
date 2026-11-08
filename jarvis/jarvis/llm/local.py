from __future__ import annotations

import json
import time

import httpx

from jarvis.llm.base import LLMError, Usage, extract_json


class LocalLLM:
    """Local LLM adapter for Ollama or llama.cpp OpenAI-compatible server."""

    def __init__(
        self,
        model: str = "llama3:latest",
        base_url: str = "http://localhost:11434/v1",
        name: str = "local",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.name = f"{name}:{model}"
        self._n = 0

    async def complete_json(
        self, system: str, messages: list[dict], schema: dict, *, thinking: str = "low"
    ) -> tuple[dict, Usage]:
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
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                if resp.status_code != 200:
                    raise LLMError(f"Local LLM HTTP error {resp.status_code}: {resp.text}")
                reply = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"Failed to connect to local LLM at {self.base_url}: {e}") from e

        latency = (time.monotonic() - t0) * 1000.0
        data = extract_json(reply)
        usage = Usage(
            model=self.model,
            input_tokens=len(user_text) // 4,
            output_tokens=len(reply) // 4,
            latency_ms=latency,
            usd=0.0,
        )
        return data, usage
