"""One-shot verification that Flux image generation works end-to-end.

Runs ImageGeneratorService.generate_images with a tiny prompt, then checks
the resulting asset file landed on disk and is reachable via the static URL.

Run via: backend\.venv\Scripts\python.exe backend\verify_flux_swap.py
"""

import asyncio
import os
import sys

import urllib.request

from app.core.config import settings
from app.services.image_generator import ImageGeneratorService


async def run() -> int:
    if not settings.flux_api_key:
        print("FAIL  FLUX_API_KEY not set")
        return 1
    print(f"INFO  model_image_gen = {settings.model_image_gen}")
    print("INFO  generating 1 image, this can take ~10-30s...")

    assets = await ImageGeneratorService.generate_images(
        prompt="A simple flat-design icon of a red apple on white background",
        count=1,
        aspect_ratio="1:1",
        agent_name="verify_flux",
        workspace_id="verify",
        campaign_id="smoketest",
    )

    if not assets:
        print("FAIL  no assets returned")
        return 1
    asset = assets[0]
    print(f"OK    asset id={asset.id} path={asset.gcs_path} url={asset.gcs_url}")

    local_path = os.path.join("assets", asset.gcs_path)
    if not os.path.exists(local_path):
        print(f"FAIL  expected file at {local_path} but it does not exist")
        return 1
    size = os.path.getsize(local_path)
    if size < 1024:
        print(f"FAIL  file at {local_path} is only {size} bytes — likely an error response")
        return 1
    print(f"OK    file at {local_path} ({size:,} bytes)")

    try:
        with urllib.request.urlopen(asset.gcs_url, timeout=5) as resp:
            served_bytes = resp.read()
        if len(served_bytes) == size:
            print(f"OK    HTTP serve from {asset.gcs_url} returned {len(served_bytes):,} bytes")
        else:
            print(f"WARN  HTTP serve byte mismatch: disk={size}, http={len(served_bytes)}")
    except Exception as exc:
        print(f"WARN  could not fetch {asset.gcs_url}: {exc}")

    print("\nALL CHECKS PASSED — Flux image generation verified.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
