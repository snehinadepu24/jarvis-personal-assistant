from __future__ import annotations

A11Y_FLAG = "--force-renderer-accessibility"


async def launch(headless: bool = False):
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir="",  # dedicated profile only; never attach to the user's main profile
        headless=headless,
        args=[A11Y_FLAG],
    )
    return pw, browser


async def act(page, role: str, name: str, verb: str = "click", text: str | None = None) -> dict:
    locator = page.get_by_role(role, name=name)
    if verb == "click":
        await locator.click()
        return {"ok": True, "detail": f"clicked {role} {name!r}"}
    if verb == "fill":
        await locator.fill(text or "")
        return {"ok": True, "detail": f"filled {role} {name!r}"}
    if verb == "text":
        found = await page.get_by_text(text or "").count()
        return {"ok": found > 0, "detail": f"{found} text matches for {text!r}"}
    return {"ok": False, "detail": f"unknown verb {verb}"}
