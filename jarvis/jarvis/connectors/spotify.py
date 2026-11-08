from __future__ import annotations

import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx

AUTH = "https://accounts.spotify.com/authorize"
TOKEN = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"


def pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def auth_url(client_id: str, redirect_uri: str, verifier: str, scope: str = "user-read-playback-state user-modify-playback-state") -> str:
    v, challenge = verifier, None
    challenge = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    q = urlencode({
        "client_id": client_id, "response_type": "code", "redirect_uri": redirect_uri,
        "code_challenge_method": "S256", "code_challenge": challenge, "scope": scope,
    })
    return f"{AUTH}?{q}"


async def exchange_code(client_id: str, redirect_uri: str, verifier: str, code: str) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.post(TOKEN, data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
            "client_id": client_id, "code_verifier": verifier,
        })
        r.raise_for_status()
        return r.json()


async def play(token: str, uri: str) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.put(f"{API}/me/player/play", headers={"Authorization": f"Bearer {token}"}, json={"uris": [uri]})
        return {"ok": r.status_code in (200, 204), "status": r.status_code}


async def search(token: str, q: str, kind: str = "track") -> list[dict]:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{API}/search", headers={"Authorization": f"Bearer {token}"}, params={"q": q, "type": kind})
        r.raise_for_status()
        return r.json().get(f"{kind}s", {}).get("items", [])
