"""Black Forest Labs (Flux) image generation provider.

Async client for https://api.bfl.ai. Submits a generation job, polls until
ready, then downloads the resulting PNG bytes.

`ImageGeneratorService` is the only caller; it expects a list of
`{"image_bytes": bytes, "mime_type": str, "prompt": str}` dicts so the
storage layer (currently local filesystem, S3 later) can persist the bytes.
"""

import asyncio
import logging
from typing import Any, Literal

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BFL_API_BASE = "https://api.bfl.ai/v1"

# Flux outputs are sized in pixels, not aspect labels. These pairs are the
# dimensions BFL recommends per ratio (megapixel ~= 1, divisible by 32).
_ASPECT_TO_DIMENSIONS: dict[str, tuple[int, int]] = {
    "1:1": (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
    "4:3": (1152, 896),
    "3:4": (896, 1152),
}

# How long to wait for a single job before giving up.
_POLL_INTERVAL_SECONDS = 1.5
_POLL_TIMEOUT_SECONDS = 90

AspectRatio = Literal["1:1", "4:3", "3:4", "16:9", "9:16"]


def _dimensions(aspect_ratio: str) -> tuple[int, int]:
    return _ASPECT_TO_DIMENSIONS.get(aspect_ratio, _ASPECT_TO_DIMENSIONS["1:1"])


async def _submit_and_poll(
    http: httpx.AsyncClient,
    model: str,
    payload: dict[str, Any],
    headers: dict[str, str],
) -> str:
    """Submit a Flux job and poll until the image URL is ready."""
    submit_resp = await http.post(f"{BFL_API_BASE}/{model}", headers=headers, json=payload)
    if submit_resp.status_code >= 400:
        # Surface BFL's actual error body so wrong model names / bad params are visible.
        body_preview = submit_resp.text[:500] if submit_resp.text else "<empty>"
        print(f"[FLUX] HTTP {submit_resp.status_code} from {model}: {body_preview}", flush=True)
        logger.error("FLUX_HTTP_ERROR model=%s status=%d body=%s", model, submit_resp.status_code, body_preview)
        submit_resp.raise_for_status()
    submit_data = submit_resp.json()
    job_id = submit_data.get("id")
    polling_url = submit_data.get("polling_url") or f"{BFL_API_BASE}/get_result?id={job_id}"
    if not job_id:
        raise RuntimeError(f"Flux submission returned no job id: {submit_data}")

    deadline = asyncio.get_event_loop().time() + _POLL_TIMEOUT_SECONDS
    while True:
        if asyncio.get_event_loop().time() > deadline:
            raise TimeoutError(f"Flux job {job_id} did not complete within {_POLL_TIMEOUT_SECONDS}s")
        await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        poll_resp = await http.get(polling_url, headers=headers)
        poll_resp.raise_for_status()
        poll_data = poll_resp.json()
        status = poll_data.get("status")
        if status == "Ready":
            sample_url = (poll_data.get("result") or {}).get("sample")
            if not sample_url:
                raise RuntimeError(f"Flux job {job_id} reported Ready but no sample URL: {poll_data}")
            return sample_url
        if status in ("Failed", "Error", "Content Moderated", "Request Moderated"):
            raise RuntimeError(f"Flux job {job_id} failed with status: {status}")
        # Otherwise still "Pending" / "Task not found yet" — keep polling.


def _uses_aspect_ratio_param(model: str) -> bool:
    """Some BFL endpoints expect `aspect_ratio` (string) instead of `width`/`height`.

    True for flux-pro-1.1-ultra and (likely) all flux-2-* models, which control
    their own output dimensions internally and don't accept explicit pixel sizes.
    """
    m = model.lower()
    return "ultra" in m or m.startswith("flux-2") or "-2-" in m or m.startswith("flux-pro-2")


async def generate_image(
    prompt: str,
    model: str | None = None,
    aspect_ratio: AspectRatio = "1:1",
    style: str | None = None,
    num_images: int = 1,
) -> list[dict[str, Any]]:
    """Generate `num_images` images from a text prompt.

    Returns a list of {"image_bytes": bytes, "mime_type": "image/png", "prompt": str}.
    """
    if not settings.flux_api_key:
        raise RuntimeError("FLUX_API_KEY is not set in the environment")

    model = model or settings.model_image_gen
    full_prompt = f"{prompt}, {style} style" if style else prompt

    # Build a model-appropriate payload — ultra and flux-2 models take aspect_ratio
    # directly; older flux-1 endpoints take explicit width/height.
    payload: dict[str, Any] = {
        "prompt": full_prompt,
        "output_format": "png",
        "prompt_upsampling": True,
        "safety_tolerance": 2,
    }
    width: int | None = None
    height: int | None = None
    if _uses_aspect_ratio_param(model):
        payload["aspect_ratio"] = aspect_ratio
    else:
        width, height = _dimensions(aspect_ratio)
        payload["width"] = width
        payload["height"] = height

    endpoint = f"{BFL_API_BASE}/{model}"
    # Visible print so the user can confirm which model is being hit at runtime.
    print(
        f"[FLUX] model={model!r}  endpoint={endpoint}  "
        f"aspect={aspect_ratio}  "
        f"dimensions={'auto-by-model' if width is None else f'{width}x{height}'}  "
        f"num_images={num_images}  prompt_chars={len(full_prompt)}",
        flush=True,
    )

    headers = {
        "x-key": settings.flux_api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    logger.info(
        "FLUX_CALL_START model=%s endpoint=%s aspect=%s dimensions=%s num_images=%d prompt_chars=%d payload_keys=%s",
        model, endpoint, aspect_ratio,
        "auto" if width is None else f"{width}x{height}",
        num_images, len(full_prompt), list(payload.keys()),
    )

    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=30) as http:
        for i in range(num_images):
            try:
                sample_url = await _submit_and_poll(http, model, payload, headers)
                img_resp = await http.get(sample_url, timeout=60)
                img_resp.raise_for_status()
                results.append({
                    "image_bytes": img_resp.content,
                    "mime_type": "image/png",
                    "prompt": full_prompt,
                })
                logger.info("FLUX_CALL_DONE model=%s variation=%d bytes=%d", model, i + 1, len(img_resp.content))
            except Exception as exc:
                logger.exception("FLUX_CALL_ERROR model=%s variation=%d: %s", model, i + 1, exc)
                # Keep going — return whatever variations succeed.
                continue

    return results


async def edit_image(
    image_data: bytes,
    edit_prompt: str,
    model: str | None = None,
) -> dict[str, Any] | None:
    """Edit an existing image using Flux Kontext.

    Returns {"image_bytes": bytes, "mime_type": str, "prompt": str} or None.
    """
    if not settings.flux_api_key:
        raise RuntimeError("FLUX_API_KEY is not set in the environment")

    import base64

    model = model or "flux-kontext-pro"
    payload = {
        "prompt": edit_prompt,
        "input_image": base64.standard_b64encode(image_data).decode("ascii"),
        "output_format": "png",
        "safety_tolerance": 2,
    }
    headers = {
        "x-key": settings.flux_api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    logger.info("FLUX_EDIT_START model=%s input_bytes=%d prompt_chars=%d", model, len(image_data), len(edit_prompt))
    async with httpx.AsyncClient(timeout=30) as http:
        try:
            sample_url = await _submit_and_poll(http, model, payload, headers)
            img_resp = await http.get(sample_url, timeout=60)
            img_resp.raise_for_status()
            logger.info("FLUX_EDIT_DONE model=%s bytes=%d", model, len(img_resp.content))
            return {
                "image_bytes": img_resp.content,
                "mime_type": "image/png",
                "prompt": edit_prompt,
            }
        except Exception:
            logger.exception("FLUX_EDIT_ERROR model=%s", model)
            return None
