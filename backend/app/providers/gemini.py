"""Backward-compat shim. Text generation moved to Anthropic Claude in Phase 2.

The 79+ agents still `from app.providers.gemini import GeminiProvider | generate_text | generate_with_image`;
those names now resolve to the Claude-backed implementations in `app.providers.claude`.

`_get_client` still returns a Google `genai.Client` because image/video/audio
services (Imagen, Veo) haven't been swapped yet — they will move to Flux + Veo3
in later phases.
"""

from google import genai

from app.core.config import settings
from app.providers.claude import (
    ClaudeProvider as GeminiProvider,
    generate_text,
    generate_with_image,
)

__all__ = ["GeminiProvider", "generate_text", "generate_with_image", "_get_client"]

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Return the Google genai client — used by Veo video generation.

    Prefers GOOGLE_API_KEY (what Blake provided for Veo); falls back to
    GEMINI_API_KEY for backward compatibility with older env files.
    """
    global _client
    if _client is None:
        api_key = settings.google_api_key or settings.gemini_api_key
        if not api_key:
            raise RuntimeError(
                "Neither GOOGLE_API_KEY nor GEMINI_API_KEY is set — Veo video "
                "generation needs one of them in .env"
            )
        _client = genai.Client(api_key=api_key)
        print(f"[VEO/GENAI] Client initialized with key prefix: {api_key[:10]}…", flush=True)
    return _client
