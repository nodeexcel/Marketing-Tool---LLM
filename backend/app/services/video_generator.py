"""Video generation service using Google Veo via google-genai SDK."""

import logging
import uuid
import os
import asyncio
import time
from typing import List, Optional, Literal

from google import genai
from google.genai import types
from app.core.config import settings
from app.models.base import GeneratedAsset
from app.providers.gemini import _get_client
from app.providers.gcs import upload_bytes

logger = logging.getLogger(__name__)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "generated", "video")
os.makedirs(ASSETS_DIR, exist_ok=True)


class VideoGeneratorService:
    """Service to generate videos via Google Veo (env-configurable model)."""

    @staticmethod
    async def generate_video(
        prompt: str,
        aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9",
        duration_seconds: int = 8,
        style: Optional[str] = None,
        agent_name: str = "video_agent",
        workspace_id: str = "global",
        campaign_id: str = "default"
    ) -> List[GeneratedAsset]:
        """Generates a video clip using Veo via the google-genai SDK."""
        client = _get_client()

        assets = []
        try:
            enhanced_prompt = prompt
            if style:
                enhanced_prompt = f"{prompt}, {style} style"

            # Visible print so we can confirm which model is being hit at runtime.
            print(
                f"[VEO] model={settings.model_video_gen!r}  aspect={aspect_ratio}  "
                f"duration={duration_seconds}s  agent={agent_name}  "
                f"workspace={workspace_id}  prompt_chars={len(enhanced_prompt)}",
                flush=True,
            )

            # --- LOG FULL REQUEST ---
            logger.info("\n" + "="*50 + "\n--- FULL VIDEO PROMPT ---\n" + enhanced_prompt + "\n" + "="*50)

            import time
            start_time = time.perf_counter()

            # Start video generation (async operation)
            try:
                operation = client.models.generate_videos(
                    model=settings.model_video_gen,
                    prompt=enhanced_prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio=aspect_ratio,
                        number_of_videos=1,
                    ),
                )
            except Exception as submit_err:
                # Surface BFL-style error visibility for Veo too.
                err_text = str(submit_err)
                print(
                    f"[VEO] SUBMIT FAILED model={settings.model_video_gen!r}: {err_text[:500]}",
                    flush=True,
                )
                logger.error("VEO_SUBMIT_ERROR model=%s error=%s", settings.model_video_gen, err_text)
                raise
            # Poll for completion (Veo is an async operation)
            max_wait = 300  # 5 minutes max
            poll_interval = 10  # seconds
            elapsed = 0

            while not operation.done and elapsed < max_wait:
                logger.info(f"[{agent_name}] Video generation in progress... ({elapsed}s elapsed)")
                await asyncio.sleep(poll_interval)
                operation = client.operations.get(operation)
                elapsed += poll_interval

            if not operation.done:
                logger.warning(f"[{agent_name}] Video generation timed out after {max_wait}s")
                print(f"[VEO] TIMEOUT after {max_wait}s — operation not done", flush=True)
                return []

            # Diagnostic: dump everything we can see on the completed operation
            op_error = getattr(operation, "error", None)
            op_response = getattr(operation, "response", None)
            op_result = getattr(operation, "result", None)
            print(
                f"[VEO] operation.done=True after {elapsed}s  "
                f"error={op_error!r}  has_response={op_response is not None}  has_result={op_result is not None}",
                flush=True,
            )
            if op_error:
                err_msg = str(op_error)
                print(f"[VEO] OPERATION ERROR: {err_msg[:600]}", flush=True)
                logger.error("VEO_OPERATION_ERROR agent=%s error=%s", agent_name, err_msg)
                return []

            # The genai SDK has shifted between .response and .result across versions —
            # try both so we're robust to either shape.
            generated_videos = None
            for container_name in ("response", "result"):
                container = getattr(operation, container_name, None)
                if container is None:
                    continue
                vids = getattr(container, "generated_videos", None)
                if vids:
                    generated_videos = vids
                    print(f"[VEO] reading videos from operation.{container_name} (count={len(vids)})", flush=True)
                    break

            if not generated_videos:
                # Last resort: log the structure so we can diagnose
                response_attrs = dir(op_response) if op_response else []
                result_attrs = dir(op_result) if op_result else []
                print(
                    f"[VEO] NO VIDEOS in operation result.  "
                    f"response attrs: {[a for a in response_attrs if not a.startswith('_')][:20]}  "
                    f"result attrs: {[a for a in result_attrs if not a.startswith('_')][:20]}",
                    flush=True,
                )
                logger.warning(
                    "VEO_EMPTY_RESPONSE agent=%s — operation.done but no generated_videos in response or result",
                    agent_name,
                )
                return []

            # Process completed videos
            for vid in generated_videos:
                asset_id = str(uuid.uuid4())
                filename = f"{asset_id}.mp4"

                if not (hasattr(vid, "video") and vid.video):
                    vid_attrs = [a for a in dir(vid) if not a.startswith('_')][:20]
                    print(f"[VEO] generated_video item has no .video attribute. attrs={vid_attrs}", flush=True)
                    logger.warning(f"[{agent_name}] No video data in response item")
                    continue

                video_bytes = None
                if getattr(vid.video, 'video_bytes', None) is not None:
                    video_bytes = vid.video.video_bytes
                elif getattr(vid.video, '_video_bytes', None) is not None:
                    video_bytes = vid.video._video_bytes
                elif hasattr(vid.video, 'dict') and vid.video.dict().get('video_bytes'):
                    video_bytes = vid.video.dict().get('video_bytes')

                if video_bytes:
                    print(f"[VEO] inline bytes received: {len(video_bytes):,} bytes", flush=True)
                    gcs_result = await upload_bytes(
                        data=video_bytes,
                        workspace_uuid=workspace_id,
                        campaign_id=campaign_id,
                        asset_type="video",
                        filename=filename,
                        content_type="video/mp4",
                    )
                    assets.append(GeneratedAsset(
                        id=asset_id,
                        asset_type="video",
                        gcs_url=gcs_result["gcs_url"],
                        gcs_path=gcs_result["gcs_path"],
                        thumbnail_url=gcs_result["gcs_url"],
                        prompt_used=enhanced_prompt,
                        model_used=settings.model_video_gen,
                        mime_type="video/mp4",
                    ))
                    logger.info(f"[{agent_name}] Video saved from inline bytes: {gcs_result['gcs_path']}")
                    continue

                uri = getattr(vid.video, "uri", None)
                if uri:
                    api_key = settings.google_api_key or settings.gemini_api_key
                    print(f"[VEO] downloading from URI: {uri}", flush=True)
                    logger.info(f"[{agent_name}] Inline bytes missing. Downloading video from URI: {uri}")

                    import httpx
                    async with httpx.AsyncClient(follow_redirects=True) as http_client:
                        try:
                            headers = {"x-goog-api-key": api_key}
                            response = await http_client.get(uri, headers=headers)
                            response.raise_for_status()

                            print(f"[VEO] downloaded {len(response.content):,} bytes from URI", flush=True)
                            gcs_result = await upload_bytes(
                                data=response.content,
                                workspace_uuid=workspace_id,
                                campaign_id=campaign_id,
                                asset_type="video",
                                filename=filename,
                                content_type="video/mp4",
                            )
                            assets.append(GeneratedAsset(
                                id=asset_id,
                                asset_type="video",
                                gcs_url=gcs_result["gcs_url"],
                                gcs_path=gcs_result["gcs_path"],
                                thumbnail_url=gcs_result["gcs_url"],
                                prompt_used=enhanced_prompt,
                                model_used=settings.model_video_gen,
                                mime_type="video/mp4",
                            ))
                            logger.info(f"[{agent_name}] Video downloaded and saved: {gcs_result['gcs_path']}")
                        except Exception as download_err:
                            print(f"[VEO] URI download FAILED: {download_err}", flush=True)
                            logger.error(f"[{agent_name}] Failed to download video from {uri}: {download_err}")
                    continue

                # Neither bytes nor URI — dump structure so we can diagnose
                video_attrs = [a for a in dir(vid.video) if not a.startswith('_')][:25]
                print(
                    f"[VEO] video object has no bytes AND no URI. video attrs: {video_attrs}",
                    flush=True,
                )
                logger.warning(f"[{agent_name}] Video object has no bytes and no URI.")
            if assets:
                # --- LOG FULL RESPONSE ---
                asset_urls = "\n".join([f"- {a.gcs_url}" for a in assets])
                logger.info("\n" + "="*50 + "\n--- FULL VIDEO RESPONSE (ASSETS) ---\n" + asset_urls + "\n" + "="*50)

                # Log to analytics
                from app.services.analytics import analytics_service
                from app.core.context_vars import user_id_ctx
                
                latency_ms = (time.perf_counter() - start_time) * 1000
                await analytics_service.log_usage(
                    user_id=user_id_ctx.get() or "system",
                    workspace_id=workspace_id,
                    campaign_id=campaign_id,
                    model_name=settings.model_video_gen,
                    tokens_input=0,
                    tokens_output=5000 * len(assets), # 5000 units per video (placeholder pricing)
                    agent_name=agent_name,
                    request_type="video_gen",
                    prompt=enhanced_prompt,
                    response=asset_urls,
                    latency_ms=latency_ms
                )
            else:
                logger.warning(f"[{agent_name}] No videos returned from Veo")

            return assets

        except Exception as e:
            logger.error(f"[{agent_name}] Video generation failed: {e}", exc_info=True)
            return []
