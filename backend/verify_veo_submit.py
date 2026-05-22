"""End-to-end Veo verification — submit, poll, download, save MP4.

Mirrors verify_flux_swap.py but for Veo video generation. Runs a real
generation against either the configured MODEL_VIDEO_GEN or an explicit model
passed as a CLI argument. Polls until the operation completes (or times out)
and saves the resulting MP4 to backend/assets/generated/video/.

Cost: ~$2-3 per SUCCESSFUL generation. ~$0 if Veo 503s or rejects upfront
(failed submits don't bill on the Gemini API path).

Usage:
  # Use whatever MODEL_VIDEO_GEN is in .env
  backend\\.venv\\Scripts\\python.exe backend\\verify_veo_submit.py

  # Override with a specific model
  backend\\.venv\\Scripts\\python.exe backend\\verify_veo_submit.py veo-3.0-fast-generate-001
  backend\\.venv\\Scripts\\python.exe backend\\verify_veo_submit.py veo-3.1-lite-generate-preview
  backend\\.venv\\Scripts\\python.exe backend\\verify_veo_submit.py veo-2.0-generate-001
"""

import asyncio
import os
import sys
import time
import uuid

from app.core.config import settings


TEST_PROMPT = "A single red apple on a wooden kitchen table, soft natural window light, 5 seconds, photorealistic."

POLL_INTERVAL_SECONDS = 10
MAX_WAIT_SECONDS = 300  # 5 minutes


async def run(model: str) -> int:
    print("=" * 60)
    print(f"  Testing Veo model: {model!r}")
    print("=" * 60)
    print(f"  Prompt: {TEST_PROMPT[:80]}...")
    print(f"  Aspect: 16:9   Max wait: {MAX_WAIT_SECONDS}s   Poll: every {POLL_INTERVAL_SECONDS}s")
    print()

    key = settings.google_api_key or settings.gemini_api_key
    if not key:
        print("FAIL  no GOOGLE_API_KEY or GEMINI_API_KEY set in .env")
        return 1
    print(f"OK    using key prefix: {key[:10]}...")

    from google import genai
    from google.genai import types

    try:
        client = genai.Client(api_key=key)
        print(f"OK    client initialized")
    except Exception as exc:
        print(f"FAIL  client init: {exc}")
        return 1

    # ── STEP 1: SUBMIT ──
    print("\n=== STEP 1: SUBMIT ===")
    start = time.perf_counter()
    try:
        operation = client.models.generate_videos(
            model=model,
            prompt=TEST_PROMPT,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
            ),
        )
        submit_elapsed = time.perf_counter() - start
        op_name = getattr(operation, "name", "(no name)")
        print(f"OK    submit accepted in {submit_elapsed:.1f}s — operation: {op_name}")
        print(f"      operation.done = {operation.done}")
    except Exception as exc:
        submit_elapsed = time.perf_counter() - start
        err = str(exc)
        print(f"FAIL  submit rejected after {submit_elapsed:.1f}s")
        print(f"      error: {err[:600]}")
        diagnose_submit_error(err)
        return 2

    # ── STEP 2: POLL ──
    print(f"\n=== STEP 2: POLL (every {POLL_INTERVAL_SECONDS}s, max {MAX_WAIT_SECONDS}s) ===")
    elapsed = 0
    while not operation.done and elapsed < MAX_WAIT_SECONDS:
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
        try:
            operation = client.operations.get(operation)
        except Exception as poll_err:
            print(f"FAIL  poll error after {elapsed}s: {poll_err}")
            return 3
        elapsed += POLL_INTERVAL_SECONDS
        print(f"      ...{elapsed}s elapsed, done={operation.done}")

    if not operation.done:
        print(f"FAIL  timed out after {MAX_WAIT_SECONDS}s without completion")
        return 4
    print(f"OK    operation completed after ~{elapsed}s")

    # ── STEP 3: INSPECT RESULT ──
    print("\n=== STEP 3: RESULT INSPECTION ===")
    op_error = getattr(operation, "error", None)
    op_response = getattr(operation, "response", None)
    op_result = getattr(operation, "result", None)
    print(f"      operation.error    = {op_error!r}")
    print(f"      operation.response = {'present' if op_response else 'None'}")
    print(f"      operation.result   = {'present' if op_result else 'None'}")

    if op_error:
        print(f"FAIL  operation finished with error: {str(op_error)[:600]}")
        return 5

    generated_videos = None
    for container_name in ("response", "result"):
        container = getattr(operation, container_name, None)
        if container is None:
            continue
        vids = getattr(container, "generated_videos", None)
        if vids:
            generated_videos = vids
            print(f"OK    found {len(vids)} video(s) in operation.{container_name}")
            break

    if not generated_videos:
        print(f"FAIL  no generated_videos in either operation.response or operation.result")
        if op_response:
            print(f"      response attrs: {[a for a in dir(op_response) if not a.startswith('_')][:20]}")
        if op_result:
            print(f"      result attrs:   {[a for a in dir(op_result) if not a.startswith('_')][:20]}")
        return 6

    # ── STEP 4: DOWNLOAD + SAVE ──
    print("\n=== STEP 4: DOWNLOAD + SAVE ===")
    video_dir = os.path.join(os.path.dirname(__file__), "assets", "generated", "video")
    os.makedirs(video_dir, exist_ok=True)
    filename = f"verify_{uuid.uuid4().hex[:8]}.mp4"
    filepath = os.path.join(video_dir, filename)

    vid = generated_videos[0]
    if not (hasattr(vid, "video") and vid.video):
        print(f"FAIL  generated_video[0] has no .video attribute")
        print(f"      attrs: {[a for a in dir(vid) if not a.startswith('_')][:20]}")
        return 7

    # Try inline bytes first
    video_bytes = (
        getattr(vid.video, "video_bytes", None)
        or getattr(vid.video, "_video_bytes", None)
    )
    if video_bytes:
        print(f"OK    inline bytes: {len(video_bytes):,} bytes")
        with open(filepath, "wb") as f:
            f.write(video_bytes)
        print(f"OK    saved to {filepath}")
        return 0

    # Fallback to URI download
    uri = getattr(vid.video, "uri", None)
    if uri:
        print(f"OK    URI returned: {uri}")
        import httpx
        async with httpx.AsyncClient(follow_redirects=True) as http:
            try:
                resp = await http.get(uri, headers={"x-goog-api-key": key}, timeout=120)
                resp.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                print(f"OK    downloaded {len(resp.content):,} bytes")
                print(f"OK    saved to {filepath}")
                return 0
            except Exception as dl_err:
                print(f"FAIL  URI download: {dl_err}")
                return 8

    print(f"FAIL  video object has neither bytes nor URI")
    print(f"      video attrs: {[a for a in dir(vid.video) if not a.startswith('_')][:20]}")
    return 9


def diagnose_submit_error(err: str) -> None:
    """Hint at what's wrong based on the error string."""
    low = err.lower()
    if "503" in err or "unavailable" in low:
        if "deadline" in low:
            print()
            print("  Diagnosis: 503 'Deadline expired' — Google's API gateway timed out")
            print("  waiting for Veo backend to accept the job. Either:")
            print("    - Google's Veo is overloaded (try again in 30-60 min), OR")
            print("    - Account billing isn't fully active for video generation")
        else:
            print()
            print("  Diagnosis: 503 service unavailable — Veo backend is overloaded.")
            print("  Try a different model or retry in 30-60 minutes.")
    elif "403" in err or "permission_denied" in low:
        print()
        print("  Diagnosis: 403 permission denied — key doesn't have Veo access on")
        print("  this model tier. Blake needs to enable Veo in Google AI Studio.")
    elif "404" in err or "not_found" in low:
        print()
        print("  Diagnosis: 404 model not found — the slug doesn't exist on the API.")
        print("  Verify the model name against the verify_veo_key.py output.")
    elif "429" in err or "exhausted" in low:
        print()
        print("  Diagnosis: 429 quota exhausted — daily/monthly Veo limit hit.")
    elif "billing" in low:
        print()
        print("  Diagnosis: billing required — Blake needs paid Google Cloud billing")
        print("  enabled on the project that owns this API key.")


def main() -> int:
    # CLI arg overrides the .env model. Otherwise use what's in settings.
    cli_model = sys.argv[1] if len(sys.argv) > 1 else None
    model = cli_model or settings.model_video_gen

    if cli_model:
        print(f"(CLI override) using model: {cli_model}")
        print(f"(.env MODEL_VIDEO_GEN is currently: {settings.model_video_gen})")
    else:
        print(f"Using MODEL_VIDEO_GEN from .env: {model}")
    print(f"To test a different model: python verify_veo_submit.py <model-slug>\n")

    return asyncio.run(run(model))


if __name__ == "__main__":
    sys.exit(main())
