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
    """Return the Gemini client — used by Imagen/Veo/audio services."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client
