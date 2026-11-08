from __future__ import annotations

import os

SCOPES = ["Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite", "Chat.ReadWrite"]
GRAPH = "https://graph.microsoft.com/v1.0"


def _msal_app(client_id: str):
    import msal

    return msal.PublicClientApplication(
        client_id, authority="https://login.microsoftonline.com/common"
    )


def token(client_id: str) -> str:
    app = _msal_app(client_id)
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if not result:
        result = app.acquire_token_interactive(SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"MSAL auth failed: {result.get('error_description', result)}")
    return result["access_token"]


async def create_draft(client_id: str, to: str, subject: str, body: str) -> str:
    import httpx

    async with httpx.AsyncClient(base_url=GRAPH) as c:
        r = await c.post(
            "/me/messages",
            headers={"Authorization": f"Bearer {token(client_id)}"},
            json={
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
        )
        r.raise_for_status()
        return r.json()["id"]


async def send_draft(client_id: str, draft_id: str) -> None:
    import httpx

    async with httpx.AsyncClient(base_url=GRAPH) as c:
        r = await c.post(f"/me/messages/{draft_id}/send", headers={"Authorization": f"Bearer {token(client_id)}"})
        r.raise_for_status()


CLIENT_ID = os.environ.get("JARVIS_GRAPH_CLIENT_ID", "")
