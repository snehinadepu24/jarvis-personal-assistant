from __future__ import annotations

from typing import Any, Callable


class VoiceInteractionAgent:
    """Specialist Agent: Communicates with user via voice/chat, asks clarifications, and confirms nonces."""

    def __init__(self, voice_ask_fn: Callable | None = None, speaker_fn: Callable | None = None):
        self.ask_fn = voice_ask_fn
        self.speak_fn = speaker_fn

    async def ask_user(self, question: str) -> str:
        if self.ask_fn:
            return await self.ask_fn(question)
        return "stop"

    async def request_nonce_confirmation(self, action_desc: str, nonce: str) -> bool:
        prompt = f"Confirmation required: {action_desc}. Please confirm with code {nonce}."
        if self.speak_fn:
            self.speak_fn(prompt)
        reply = await self.ask_user(f"{prompt} (Say 'confirm {nonce}' or 'cancel')")
        return nonce.lower() in reply.lower() or "confirm" in reply.lower() or "yes" in reply.lower()

