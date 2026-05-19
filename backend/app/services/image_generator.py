"""Image generation service — now backed by Black Forest Labs (Flux).

Phase 2c: the public surface (`ImageGeneratorService.generate_images`) is
unchanged so `LLMRouter.generate_image` and every visual agent keep working.
The previous Imagen-via-google-genai implementation has been replaced with
a Flux call followed by an upload through `app.providers.gcs` (which
currently falls back to local-filesystem storage until S3 lands).
"""

import logging
import uuid
from typing import List, Literal, Optional

from app.core.context_vars import user_id_ctx, workspace_id_ctx
from app.models.base import GeneratedAsset
from app.providers import flux as flux_provider
from app.providers.gcs import upload_bytes
from app.services.analytics import analytics_service

logger = logging.getLogger(__name__)


def _get_image_model() -> str:
    from app.core.config import settings
    return settings.model_image_gen


class ImageGeneratorService:
    """Service to generate images via Flux."""

    @staticmethod
    async def generate_images(
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: Literal["1:1", "4:3", "3:4", "16:9", "9:16"] = "1:1",
        count: int = 1,
        style: Optional[str] = None,
        agent_name: str = "visual_agent",
        workspace_id: str = "global",
        campaign_id: str = "default",
    ) -> List[GeneratedAsset]:
        """Generate `count` images (max 4) via Flux and persist them.

        Returns a list of `GeneratedAsset` objects. The `gcs_url` field holds
        whatever the storage layer returns — a local /assets URL today, an S3
        URL after the Phase 2c follow-up.
        """
        image_model = _get_image_model()
        enhanced_prompt = f"{prompt}, {style} style" if style else prompt

        logger.info(
            "[%s] IMAGE_GEN_START model=%s aspect=%s count=%d workspace=%s campaign=%s",
            agent_name, image_model, aspect_ratio, count, workspace_id, campaign_id,
        )
        logger.info("\n" + "=" * 50 + "\n--- FULL IMAGE PROMPT ---\n" + enhanced_prompt + "\n" + "=" * 50)

        # Flux: one job per variation (the BFL API generates one image per call).
        bounded_count = min(max(count, 1), 4)
        try:
            flux_results = await flux_provider.generate_image(
                prompt=enhanced_prompt,
                model=image_model,
                aspect_ratio=aspect_ratio,
                num_images=bounded_count,
            )
        except Exception as exc:
            logger.error("[%s] Flux generation failed: %s", agent_name, exc, exc_info=True)
            return []

        assets: list[GeneratedAsset] = []
        for result in flux_results:
            asset_id = str(uuid.uuid4())
            mime_type = result.get("mime_type") or "image/png"
            ext = "png" if "png" in mime_type else "jpg"
            filename = f"{asset_id}.{ext}"
            try:
                storage_result = await upload_bytes(
                    data=result["image_bytes"],
                    workspace_uuid=workspace_id,
                    campaign_id=campaign_id,
                    asset_type="image",
                    filename=filename,
                    content_type=mime_type,
                )
            except Exception:
                logger.exception("[%s] Failed to persist generated image", agent_name)
                continue

            asset_url = storage_result["gcs_url"]
            asset_path = storage_result["gcs_path"]
            assets.append(GeneratedAsset(
                id=asset_id,
                asset_type="image",
                gcs_url=asset_url,
                gcs_path=asset_path,
                thumbnail_url=asset_url,
                prompt_used=enhanced_prompt,
                model_used=image_model,
                mime_type=mime_type,
            ))
            logger.info("[%s] Image stored: %s", agent_name, asset_path)

        if assets:
            asset_urls = "\n".join(f"- {a.gcs_url}" for a in assets)
            logger.info("\n" + "=" * 50 + "\n--- FULL IMAGE RESPONSE (ASSETS) ---\n" + asset_urls + "\n" + "=" * 50)
            await analytics_service.log_usage(
                user_id=user_id_ctx.get() or "system",
                workspace_id=workspace_id,
                campaign_id=campaign_id,
                model_name=image_model,
                tokens_input=0,
                tokens_output=1000 * len(assets),  # 1000 units per image, same as before
                agent_name=agent_name,
                request_type="image_gen",
                prompt=enhanced_prompt,
                response=asset_urls,
            )
        else:
            logger.warning("[%s] No images returned from Flux", agent_name)

        return assets
