"""Unified LLM router — text via Anthropic Claude, image via Imagen/Flux, video via Veo.

Provides a single entry point for text, image, and video generation.
Text generation delegates to `app.providers.claude.generate_text` so the router
and the agent-level `GeminiProvider` (aliased to `ClaudeProvider`) share one
implementation, with consistent logging, attachment handling, and analytics.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.context_vars import workspace_id_ctx
from app.providers import claude as claude_provider

logger = logging.getLogger(__name__)


class LLMRouter:
    """Unified router for AI text, image, and video generation."""

    def _get_model_for_tier(self, tier: str) -> str:
        return settings.model_text

    # ── Text Generation ─────────────────────────────────────────
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_tier: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 16384,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate text via Anthropic Claude."""
        model = self._get_model_for_tier(model_tier)
        response_mime_type = (
            "application/json"
            if response_format and response_format.get("type") == "json_object"
            else None
        )
        logger.info("Generating text via %s (Tier: %s, max_tokens: %d)", model, model_tier, max_tokens)
        result = await claude_provider.generate_text(
            prompt=prompt,
            model=model,
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type=response_mime_type,
        )
        return result["text"]

    # ── Image Generation ────────────────────────────────────────
    async def generate_image(
        self,
        prompt: str,
        count: int = 1,
        aspect_ratio: str = "1:1",
        style: Optional[str] = None,
        agent_name: str = "visual_agent",
    ) -> List:
        """Generate images via ImageGeneratorService (Imagen / Gemini).

        Returns a list of GeneratedAsset objects.
        """
        from app.services.image_generator import ImageGeneratorService

        logger.info("[%s] LLMRouter.generate_image → delegating to ImageGeneratorService", agent_name)
        return await ImageGeneratorService.generate_images(
            prompt=prompt,
            count=count,
            aspect_ratio=aspect_ratio,
            style=style,
            agent_name=agent_name,
            workspace_id=workspace_id_ctx.get() or "global",
            campaign_id="default" # Campaign ID context var not strictly implemented yet, safe default
        )

    # ── Video Generation ────────────────────────────────────────
    async def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 8,
        style: Optional[str] = None,
        agent_name: str = "video_agent",
    ) -> List:
        """Generate video via VideoGeneratorService (Google Veo).

        Returns a list of GeneratedAsset objects.
        """
        from app.services.video_generator import VideoGeneratorService

        logger.info("[%s] LLMRouter.generate_video → delegating to VideoGeneratorService", agent_name)
        return await VideoGeneratorService.generate_video(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
            style=style,
            agent_name=agent_name,
        )


llm_router = LLMRouter()
