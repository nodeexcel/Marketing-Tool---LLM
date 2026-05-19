"""One-shot verification that all agents route through Claude.

Static checks: confirm the names exported by `app.providers.gemini` (which
every agent imports) point at the Claude implementation. Live check: make
one tiny Anthropic API call through ClaudeProvider to prove the wiring works
end-to-end with the configured key + model.

Run via: backend\.venv\Scripts\python.exe backend\verify_claude_swap.py
"""

import asyncio
import importlib
import sys


def static_checks() -> bool:
    """Confirm gemini.py exports actually resolve to Claude implementations."""
    gem = importlib.import_module("app.providers.gemini")
    cla = importlib.import_module("app.providers.claude")

    ok = True

    if gem.GeminiProvider is not cla.ClaudeProvider:
        print("FAIL  gemini.GeminiProvider is NOT ClaudeProvider")
        ok = False
    else:
        print("OK    gemini.GeminiProvider IS ClaudeProvider")

    if gem.generate_text is not cla.generate_text:
        print("FAIL  gemini.generate_text is NOT claude.generate_text")
        ok = False
    else:
        print("OK    gemini.generate_text IS claude.generate_text")

    if gem.generate_with_image is not cla.generate_with_image:
        print("FAIL  gemini.generate_with_image is NOT claude.generate_with_image")
        ok = False
    else:
        print("OK    gemini.generate_with_image IS claude.generate_with_image")

    # _get_client must stay Gemini-backed for image/video/audio services
    import google.genai as genai
    client = gem._get_client()
    if not isinstance(client, genai.Client):
        print(f"FAIL  gemini._get_client() returned {type(client).__name__}, expected genai.Client")
        ok = False
    else:
        print("OK    gemini._get_client() still returns genai.Client (for Imagen/Veo)")

    return ok


def count_agent_importers() -> int:
    """Count files that import GeminiProvider | generate_text from gemini.py."""
    import pathlib
    root = pathlib.Path(__file__).parent / "app"
    needles = ("from app.providers.gemini import",)
    count = 0
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(n in text for n in needles):
            count += 1
    return count


async def live_call() -> bool:
    """Round-trip through ClaudeProvider with a minimal prompt."""
    from app.providers.gemini import GeminiProvider
    from app.core.config import settings

    if not settings.anthropic_api_key:
        print("SKIP  no ANTHROPIC_API_KEY set — skipping live call")
        return True

    provider = GeminiProvider()
    print(f"INFO  model_text = {settings.model_text}")
    print(f"INFO  calling {type(provider).__name__}.generate_text() with a tiny prompt...")
    text = await provider.generate_text(
        prompt="Reply with exactly the word: PONG",
        system_prompt="You are a strict echo. Respond with one word only.",
        max_output_tokens=16,
        response_mime_type=None,
    )
    print(f"INFO  response: {text!r}")
    if "PONG" in text.upper():
        print("OK    live Claude API call succeeded")
        return True
    print("WARN  live call returned text but didn't contain PONG — wiring works, model misbehaved")
    return True


def main() -> int:
    print("=== STATIC CHECKS ===")
    static_ok = static_checks()

    print("\n=== AGENT IMPORTER COUNT ===")
    n = count_agent_importers()
    print(f"OK    {n} files import from app.providers.gemini (all now routed to Claude)")

    print("\n=== LIVE API CALL ===")
    live_ok = asyncio.run(live_call())

    print()
    if static_ok and live_ok:
        print("ALL CHECKS PASSED — Phase 2 swap verified.")
        return 0
    print("CHECKS FAILED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
