"""Probe Veo access WITHOUT generating a video (no cost).

Confirms three things on a Gemini API key alone (no GOOGLE_CLOUD_PROJECT needed):
  1. The key authenticates with Google's Generative Language API.
  2. Veo video models are available to this key.
  3. Whichever MODEL_VIDEO_GEN you've set in .env is actually accessible.

If all three pass, the UI 'AI Video Creator' agent will work — and the only
cost is one real generation when you click Generate in the UI ($2-3 per 8s).

Run via: backend\.venv\Scripts\python.exe backend\verify_veo_key.py
"""

import sys

from app.core.config import settings


def main() -> int:
    # Loud, upfront banner so it's impossible to miss which model the .env points at.
    print("=" * 60)
    print(f"  MODEL_VIDEO_GEN currently loaded:  {settings.model_video_gen!r}")
    print("=" * 60)
    print("  (this is the value the BACKEND will use after a FULL restart —")
    print("   uvicorn --reload does NOT pick up .env edits)")
    print()

    print("=== STEP 1: KEY ===")
    key = settings.google_api_key or settings.gemini_api_key
    if not key:
        print("FAIL  no GOOGLE_API_KEY or GEMINI_API_KEY set in .env")
        return 1
    source = "GOOGLE_API_KEY" if settings.google_api_key else "GEMINI_API_KEY"
    print(f"OK    using {source} (prefix: {key[:10]}...)")
    print(f"OK    GOOGLE_CLOUD_PROJECT = {settings.google_cloud_project!r} (empty is fine for Gemini API path)")

    print("\n=== STEP 2: CLIENT INIT ===")
    try:
        from google import genai
        client = genai.Client(api_key=key)
        print(f"OK    genai client initialized: {type(client).__name__}")
    except Exception as exc:
        print(f"FAIL  client init failed: {exc}")
        return 1

    print("\n=== STEP 3: LIST AVAILABLE MODELS (free read-only call) ===")
    try:
        all_models = list(client.models.list())
    except Exception as exc:
        err = str(exc)
        print(f"FAIL  list models failed: {err[:400]}")
        if "permission" in err.lower() or "403" in err:
            print("  Diagnosis: key is invalid or restricted")
        elif "quota" in err.lower() or "429" in err:
            print("  Diagnosis: quota exceeded")
        return 1
    print(f"OK    found {len(all_models)} models on this key")

    print("\n=== STEP 4: FILTER FOR VEO ===")
    veo_models = [m for m in all_models if "veo" in (m.name or "").lower()]
    if not veo_models:
        print("FAIL  no Veo models visible on this key")
        print("  Diagnosis: Veo isn't enabled on this account.")
        print("  Blake needs to enable Veo at https://aistudio.google.com (Veo may require")
        print("  paid billing + region access). Top non-Veo models visible:")
        for m in all_models[:8]:
            print(f"    - {m.name}")
        return 1
    print(f"OK    {len(veo_models)} Veo model(s) available:")
    for m in veo_models:
        # Strip the "models/" prefix for cleaner output
        clean = (m.name or "").replace("models/", "")
        print(f"    - {clean}")

    print("\n=== STEP 5: CHECK CONFIGURED MODEL IS IN THE LIST ===")
    target = settings.model_video_gen
    available_names = [(m.name or "").replace("models/", "") for m in veo_models]
    if target in available_names:
        print(f"OK    MODEL_VIDEO_GEN={target!r} is available")
        print("\nALL CHECKS PASSED — Veo is ready. You can run AI Video Creator in the UI.")
        print("First successful generation will cost ~$2-3 for an 8-second clip.")
        return 0
    print(f"FAIL  MODEL_VIDEO_GEN={target!r} is NOT in the list of Veo models on this key.")
    print(f"  Pick one of the available models above and update .env:")
    if available_names:
        print(f"    MODEL_VIDEO_GEN={available_names[0]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
