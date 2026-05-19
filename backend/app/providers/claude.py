"""Anthropic Claude client wrapper — text generation + multimodal.

Public surface mirrors `app.providers.gemini` so the swap is invisible to the
79+ agents that import `GeminiProvider`, `generate_text`, or `generate_with_image`.
`gemini.py` re-exports these names for backward compatibility.

Attachments come through `gemini_attachments_ctx` (name kept for compat) as a list
of `{"data": bytes, "filename": str, "mime_type": str}` dicts. Images/PDFs are
sent as native content blocks; other bytes are decoded as UTF-8 text when possible.
"""

import base64
import logging
from typing import Any

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.context_vars import (
    agent_name_ctx,
    campaign_id_ctx,
    gemini_attachments_ctx,
    user_id_ctx,
    workspace_id_ctx,
)
from app.services.analytics import analytics_service

logger = logging.getLogger(__name__)

_client: AsyncAnthropic | None = None

_IMAGE_MIME_PREFIX = "image/"
_PDF_MIME = "application/pdf"
_JSON_INSTRUCTION = (
    "\n\nRespond with valid JSON only. Do not wrap the response in markdown "
    "code fences, do not add commentary, do not add a preamble. Output raw JSON."
)


def _get_client() -> AsyncAnthropic:
    """Get or initialize the Anthropic async client."""
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def _attachment_metadata() -> tuple[int, list[str]]:
    attachments = gemini_attachments_ctx.get() or []
    filenames = [str(a.get("filename") or "unnamed") for a in attachments]
    return len(attachments), filenames


def _attachment_to_block(attachment: dict[str, Any]) -> dict[str, Any] | None:
    """Turn an attachment dict into a Claude content block.

    Returns None if the attachment is unusable (no data, unsupported type that
    isn't valid UTF-8 text).
    """
    data: bytes | None = attachment.get("data")
    if not data:
        return None
    mime_type = attachment.get("mime_type") or "application/octet-stream"
    filename = attachment.get("filename") or "attachment"

    if mime_type.startswith(_IMAGE_MIME_PREFIX):
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": base64.standard_b64encode(data).decode("ascii"),
            },
        }
    if mime_type == _PDF_MIME:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": _PDF_MIME,
                "data": base64.standard_b64encode(data).decode("ascii"),
            },
        }
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning(
            "Skipping attachment %s — unsupported mime %s and not valid UTF-8",
            filename,
            mime_type,
        )
        return None
    return {"type": "text", "text": f"<attachment filename=\"{filename}\">\n{decoded}\n</attachment>"}


def _build_user_content(
    prompt: str,
    extra_image_data: bytes | None = None,
    extra_image_mime: str = "image/png",
) -> list[dict[str, Any]]:
    """Build the user message content blocks: attachments + optional extra image + prompt."""
    blocks: list[dict[str, Any]] = []
    for attachment in gemini_attachments_ctx.get() or []:
        block = _attachment_to_block(attachment)
        if block:
            blocks.append(block)
    if extra_image_data:
        blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": extra_image_mime,
                "data": base64.standard_b64encode(extra_image_data).decode("ascii"),
            },
        })
    blocks.append({"type": "text", "text": prompt})
    return blocks


def _extract_text(response: Any) -> str:
    """Concatenate all text blocks from a Claude messages response."""
    parts: list[str] = []
    for block in response.content or []:
        if getattr(block, "type", None) == "text":
            parts.append(block.text or "")
    return "".join(parts)


class ClaudeProvider:
    """High-level wrapper used by agents. Returns text strings directly.

    Matches the public method shape of the original `GeminiProvider`.
    """

    def _resolve_model(self, model_tier: str | None = None) -> str:
        return settings.model_text

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model_tier: str = "pro",
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        response_mime_type: str | None = "application/json",
        response_format: dict | None = None,
    ) -> str:
        if response_format and response_format.get("type") == "json_object":
            response_mime_type = "application/json"

        result = await generate_text(
            prompt=prompt,
            model=self._resolve_model(model_tier),
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
        )
        return result["text"]


async def generate_text(
    prompt: str,
    model: str | None = None,
    system_instruction: str | None = None,
    temperature: float = 0.7,
    max_output_tokens: int = 8192,
    response_mime_type: str | None = None,
    user_id: str | None = None,
    workspace_id: str | None = None,
    campaign_id: str | None = None,
    agent_name: str | None = None,
) -> dict[str, Any]:
    """Generate text using Claude.

    Returns:
        {"text": "...", "tokens_input": int, "tokens_output": int, "model": str}
    """
    client = _get_client()
    model = model or settings.model_text

    user_id = user_id or user_id_ctx.get() or "system"
    workspace_id = workspace_id or workspace_id_ctx.get()
    campaign_id = campaign_id or campaign_id_ctx.get()
    agent_name = agent_name or agent_name_ctx.get() or "unknown"

    # JSON mode: Claude has no native flag, so we enforce via system prompt.
    effective_system = system_instruction
    if response_mime_type == "application/json":
        effective_system = (effective_system or "") + _JSON_INSTRUCTION

    user_content = _build_user_content(prompt)
    attachment_count, attachment_names = _attachment_metadata()
    attachment_mode = "inline_blocks" if attachment_count else "none"

    logger.info(
        "CLAUDE_CALL_START type=text model=%s agent=%s workspace=%s campaign=%s attachments=%d attachment_names=%s attachment_mode=%s prompt_chars=%d response_mime=%s",
        model, agent_name, workspace_id, campaign_id,
        attachment_count, attachment_names, attachment_mode,
        len(prompt or ""), response_mime_type or "default",
    )
    logger.info("\n" + "=" * 50 + "\n--- FULL SYSTEM PROMPT ---\n" + (effective_system or "None") + "\n" + "=" * 50)
    logger.info("\n" + "=" * 50 + "\n--- FULL USER PROMPT ---\n" + prompt + "\n" + "=" * 50)

    # NB: `temperature` is intentionally omitted. Claude 4.x reasoning models
    # (e.g. opus-4-7) reject it as deprecated; Sonnet/Haiku still accept it but
    # we keep the request shape uniform across models. Phase 5 will revisit
    # per-model sampling controls if needed.
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_output_tokens,
        "messages": [{"role": "user", "content": user_content}],
    }
    if effective_system:
        kwargs["system"] = effective_system

    try:
        response = await client.messages.create(**kwargs)
    except Exception:
        logger.exception(
            "CLAUDE_CALL_ERROR type=text model=%s agent=%s workspace=%s campaign=%s attachments=%d attachment_names=%s",
            model, agent_name, workspace_id, campaign_id, attachment_count, attachment_names,
        )
        raise

    text = _extract_text(response)
    logger.info("\n" + "=" * 50 + "\n--- FULL LLM RESPONSE ---\n" + text + "\n" + "=" * 50)

    tokens_in = response.usage.input_tokens if response.usage else 0
    tokens_out = response.usage.output_tokens if response.usage else 0

    await analytics_service.log_usage(
        user_id=user_id,
        workspace_id=workspace_id,
        campaign_id=campaign_id,
        model_name=model,
        tokens_input=tokens_in,
        tokens_output=tokens_out,
        agent_name=agent_name,
        request_type="text",
        prompt=prompt,
        response=text,
    )

    logger.info(
        "CLAUDE_CALL_DONE type=text model=%s agent=%s workspace=%s campaign=%s attachments=%d tokens_in=%d tokens_out=%d text_chars=%d",
        model, agent_name, workspace_id, campaign_id,
        attachment_count, tokens_in, tokens_out, len(text),
    )
    return {
        "text": text,
        "tokens_input": tokens_in,
        "tokens_output": tokens_out,
        "model": model,
    }


async def generate_with_image(
    prompt: str,
    image_data: bytes | None = None,
    image_mime_type: str = "image/png",
    model: str | None = None,
    system_instruction: str | None = None,
    user_id: str | None = None,
    workspace_id: str | None = None,
    campaign_id: str | None = None,
    agent_name: str | None = None,
) -> dict[str, Any]:
    """Multimodal generation — text + optional image input."""
    client = _get_client()
    model = model or settings.model_text

    user_id = user_id or user_id_ctx.get() or "system"
    workspace_id = workspace_id or workspace_id_ctx.get()
    campaign_id = campaign_id or campaign_id_ctx.get()
    agent_name = agent_name or agent_name_ctx.get() or "unknown"

    user_content = _build_user_content(prompt, extra_image_data=image_data, extra_image_mime=image_mime_type)
    attachment_count, attachment_names = _attachment_metadata()
    attachment_mode = "inline_blocks" if (attachment_count or image_data) else "none"

    logger.info(
        "CLAUDE_CALL_START type=vision model=%s agent=%s workspace=%s campaign=%s attachments=%d attachment_names=%s attachment_mode=%s inline_image=%s prompt_chars=%d",
        model, agent_name, workspace_id, campaign_id,
        attachment_count, attachment_names, attachment_mode, bool(image_data), len(prompt or ""),
    )
    logger.info("\n" + "=" * 50 + "\n--- FULL SYSTEM PROMPT ---\n" + (system_instruction or "None") + "\n" + "=" * 50)
    logger.info("\n" + "=" * 50 + "\n--- FULL USER PROMPT ---\n" + prompt + "\n" + "=" * 50)

    # See note in generate_text() about omitting `temperature`.
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": user_content}],
    }
    if system_instruction:
        kwargs["system"] = system_instruction

    try:
        response = await client.messages.create(**kwargs)
    except Exception:
        logger.exception(
            "CLAUDE_CALL_ERROR type=vision model=%s agent=%s workspace=%s campaign=%s",
            model, agent_name, workspace_id, campaign_id,
        )
        raise

    text = _extract_text(response)
    logger.info("\n" + "=" * 50 + "\n--- FULL LLM RESPONSE ---\n" + text + "\n" + "=" * 50)

    tokens_in = response.usage.input_tokens if response.usage else 0
    tokens_out = response.usage.output_tokens if response.usage else 0

    await analytics_service.log_usage(
        user_id=user_id,
        workspace_id=workspace_id,
        campaign_id=campaign_id,
        model_name=model,
        tokens_input=tokens_in,
        tokens_output=tokens_out,
        agent_name=agent_name,
        request_type="vision",
        prompt=prompt,
        response=text,
    )

    logger.info(
        "CLAUDE_CALL_DONE type=vision model=%s agent=%s workspace=%s campaign=%s tokens_in=%d tokens_out=%d text_chars=%d",
        model, agent_name, workspace_id, campaign_id, tokens_in, tokens_out, len(text),
    )
    return {
        "text": text,
        "tokens_input": tokens_in,
        "tokens_output": tokens_out,
        "model": model,
    }
