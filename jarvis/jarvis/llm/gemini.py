from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import time
from typing import Any

import httpx

from jarvis.llm.base import LLMError, Usage, extract_json
from jarvis.llm.costs import COSTS

logger = logging.getLogger(__name__)

FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


class GeminiLLM:
    name: str

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: str | None = None,
        session_prefix: str = "jarvis",
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise LLMError(
                "GEMINI_API_KEY is not set. Get a free API key from Google AI Studio "
                "(https://aistudio.google.com/apikey) and set it in your environment or .env file."
            )
        self.session_prefix = session_prefix
        self._n = 0
        self.name = f"gemini:{model}"

    async def complete_json(
        self, system: str, messages: list[dict], schema: dict, *, thinking: str = "low"
    ) -> tuple[dict, Usage]:
        user_text = "\n\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        user_text += "\n\nReturn exactly ONE JSON object valid against the schema above. No prose, no code fences."
        image_bytes = next((m.get("image_bytes") for m in messages if m.get("image_bytes")), None)

        # Build model candidate list starting with configured model
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_err: Exception | None = None

        for model_candidate in models_to_try:
            for attempt in range(2):
                self._n += 1
                t0 = time.monotonic()
                try:
                    logger.debug("Attempt %s for model %s (candidate %s)", attempt + 1, model_candidate, model_candidate)
                    reply = await self._call_gemini_api(
                        model=model_candidate,
                        system=system,
                        prompt=user_text,
                        image_bytes=image_bytes,
                    )
                    logger.debug("Gemini API returned reply (truncated): %s", reply[:200].replace('\n', ' ') + "…")
                except Exception as e:
                    last_err = e
                    err_str = str(e)
                    # If model is 503 (high demand) or 429 (rate limit), break inner loop to try fallback model
                    if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        logger.warning("Model %s hit demand/quota limit (%s); trying fallback model...", model_candidate, e)
                        await asyncio.sleep(0.5)
                        break
                    await asyncio.sleep(0.5)
                    continue
                except Exception as e:
                    last_err = e
                    err_str = str(e)
                    # If model is 503 (high demand) or 429 (rate limit), break inner loop to try fallback model
                    if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        logger.warning(f"Model {model_candidate} hit demand/quota limit ({e}); trying fallback model...")
                        await asyncio.sleep(0.5)
                        break
                    await asyncio.sleep(0.5)
                    continue

                latency = (time.monotonic() - t0) * 1000.0
                try:
                    data = extract_json(reply)
                except LLMError as e:
                    last_err = e
                    user_text += "\n\nYour previous reply was not a single valid JSON object. Reply with ONLY the JSON object."
                    continue

                usage = COSTS.usage(model_candidate, user_text, reply, latency)
                return data, usage

        if last_err and ("429" in str(last_err) or "RESOURCE_EXHAUSTED" in str(last_err)):
            raise LLMError(
                "Gemini quota exhausted across tested models. "
                "Wait for the provider reset or configure another Gemini project/API key. "
                f"Provider detail: {last_err}"
            )
        raise LLMError(f"Gemini complete_json failed after retries: {last_err}")

    async def _call_gemini_api(
        self,
        model: str,
        system: str,
        prompt: str,
        image_bytes: bytes | None = None,
    ) -> str:
        if image_bytes:
            return await self._call_gemini_rest(model, system, prompt, image_bytes)

        # 1. Try modern google-genai SDK
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "system_instruction": system,
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                },
            )
            if resp.text:
                return resp.text
        except Exception as sdk_err:
            if "503" in str(sdk_err) or "429" in str(sdk_err):
                raise sdk_err

        # 2. Reliable REST API fallback via httpx (direct Google AI Studio endpoint)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        if system:
            payload["systemInstruction"] = {
                "parts": [{"text": system}]
            }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                url,
                params={"key": self.api_key},
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code != 200:
                raise LLMError(f"Google AI Studio Gemini API error {resp.status_code}: {resp.text}")
            result_json = resp.json()
            try:
                candidate = result_json["candidates"][0]
                part = candidate["content"]["parts"][0]
                return part["text"]
            except (KeyError, IndexError) as err:
                raise LLMError(f"Unexpected response structure from Gemini API: {result_json}") from err

    async def _call_gemini_rest(
        self,
        model: str,
        system: str,
        prompt: str,
        image_bytes: bytes,
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload: dict[str, Any] = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64.b64encode(image_bytes).decode("ascii"),
                        }
                    },
                ]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                url, params={"key": self.api_key}, json=payload,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code != 200:
                raise LLMError(f"Gemini vision API error {resp.status_code}: {resp.text}")
            try:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as err:
                raise LLMError(f"Unexpected Gemini vision response: {resp.text}") from err
