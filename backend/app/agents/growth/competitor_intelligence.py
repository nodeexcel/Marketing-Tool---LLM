"""Competitor Intelligence agent — analyzes a competitor piece and rewrites it.

User pastes a competitor's email / SMS / ad / landing page copy. Claude breaks
down what makes it work and produces N rewritten variations in the user's
brand voice (pulled from workspace context auto-injected by `prepare_context`).
"""

import logging
from typing import Any, Dict, List

from app.agents.base import BaseV4Agent
from app.agents.competitor_intelligence_models import (
    CompetitorAnalysis,
    CompetitorIntelligenceInput,
    CompetitorIntelligenceOutput,
    RewrittenVariation,
)
from app.core.llm import llm_router
from app.utils.json_repair import safe_json_parse

logger = logging.getLogger(__name__)


def _normalize_analysis(data: Dict[str, Any]) -> CompetitorAnalysis:
    raw = data.get("analysis") or {}
    if not isinstance(raw, dict):
        raw = {}

    def _as_list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v) for v in value if v not in (None, "")]
        if isinstance(value, str) and value:
            return [value]
        return []

    return CompetitorAnalysis(
        hook=str(raw.get("hook") or ""),
        pain_points=_as_list(raw.get("pain_points")),
        persuasion_patterns=_as_list(raw.get("persuasion_patterns")),
        primary_cta=str(raw.get("primary_cta") or ""),
        tone_summary=str(raw.get("tone_summary") or ""),
        structural_notes=_as_list(raw.get("structural_notes")),
        strengths=_as_list(raw.get("strengths")),
        weaknesses=_as_list(raw.get("weaknesses")),
    )


def _normalize_variations(data: Dict[str, Any]) -> List[RewrittenVariation]:
    raw = data.get("rewritten_variations") or []
    if not isinstance(raw, list):
        return []
    out: List[RewrittenVariation] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        subject = item.get("subject_line")
        out.append(RewrittenVariation(
            variation_name=str(item.get("variation_name") or "Variation"),
            subject_line=str(subject) if subject not in (None, "") else None,
            content=str(item.get("content") or ""),
            rationale=str(item.get("rationale") or ""),
        ))
    return out


def _build_text_content(
    analysis: CompetitorAnalysis,
    variations: List[RewrittenVariation],
    insights: List[str],
) -> str:
    """Build a Markdown rendering of the full output for the rich-text editor."""
    parts: List[str] = ["# Competitor Intelligence", "", "## Analysis"]
    if analysis.hook:
        parts.append(f"**Hook:** {analysis.hook}")
    if analysis.tone_summary:
        parts.append(f"**Tone:** {analysis.tone_summary}")
    if analysis.primary_cta:
        parts.append(f"**Primary CTA:** {analysis.primary_cta}")
    if analysis.pain_points:
        parts.append("\n**Pain points targeted:**")
        parts.extend(f"- {p}" for p in analysis.pain_points)
    if analysis.persuasion_patterns:
        parts.append("\n**Persuasion patterns:**")
        parts.extend(f"- {p}" for p in analysis.persuasion_patterns)
    if analysis.structural_notes:
        parts.append("\n**Structure:**")
        parts.extend(f"- {p}" for p in analysis.structural_notes)
    if analysis.strengths:
        parts.append("\n**Strengths:**")
        parts.extend(f"- {p}" for p in analysis.strengths)
    if analysis.weaknesses:
        parts.append("\n**Weaknesses:**")
        parts.extend(f"- {p}" for p in analysis.weaknesses)

    if variations:
        parts.append("\n## Rewritten for Your Brand")
        for i, v in enumerate(variations, 1):
            parts.append(f"\n### {i}. {v.variation_name}")
            if v.subject_line:
                parts.append(f"**Subject:** {v.subject_line}")
            parts.append("")
            parts.append(v.content)
            if v.rationale:
                parts.append(f"\n_Why this works: {v.rationale}_")

    if insights:
        parts.append("\n## Key Insights")
        parts.extend(f"- {i}" for i in insights)

    return "\n".join(parts)


class CompetitorIntelligenceAgent(BaseV4Agent):
    agent_id = "competitor_intelligence"
    agent_name = "Competitor Intelligence"
    description = "Analyzes competitor marketing copy and rewrites it in your brand voice."
    category = "growth"

    async def _execute_internal(
        self,
        input_data: CompetitorIntelligenceInput,
        context_str: str,
    ) -> CompetitorIntelligenceOutput:
        # Build the "competitor content" the prompt will reference from up to three
        # sources: pasted text, scraped URL content, and inline image attachments.
        # The api_router auto-scrapes competitor_url into input_data.scraped_content;
        # images are auto-injected into Claude's content blocks via gemini_attachments_ctx.
        sources: list[str] = []
        if input_data.competitor_content and input_data.competitor_content.strip():
            sources.append(
                f"<pasted_text>\n{input_data.competitor_content.strip()}\n</pasted_text>"
            )
        target_url = (input_data.competitor_url or "").strip()
        if target_url and input_data.scraped_content:
            for item in input_data.scraped_content:
                if getattr(item, "url", "") == target_url and item.extracted_text:
                    sources.append(
                        f"<scraped_url url=\"{item.url}\">\n{item.extracted_text[:6000]}\n</scraped_url>"
                    )
                    break
        attached_image_count = len(input_data.kb_documents or []) + (
            1 if hasattr(input_data, "_attachment_count") else 0
        )
        # Attachments themselves are injected by the provider layer (claude.py);
        # we only signal their presence in the prompt so the model knows to inspect them.
        if not sources:
            return CompetitorIntelligenceOutput(
                agent_id=self.agent_id,
                success=False,
                error=(
                    "Provide at least one source: paste competitor text, supply a URL, "
                    "or attach a screenshot."
                ),
                competitor_name=input_data.competitor_name,
                content_type=input_data.content_type,
                text_content="No competitor content was provided.",
            )

        combined_content = "\n\n".join(sources)
        if target_url and not any("scraped_url" in s for s in sources):
            combined_content += f"\n\n<note>URL {target_url} was provided but scraping returned no usable content.</note>"

        prompt_config = await self.get_prompt_config(
            input_data=input_data,
            default_system=(
                "You are a senior conversion copywriter and competitive intelligence "
                "analyst. Return ONLY a JSON object — no markdown, no commentary."
            ),
            default_user="",  # YAML provides the user prompt
            variables={
                "competitor_content": combined_content,
                "content_type": input_data.content_type,
                "competitor_name": input_data.competitor_name or "Unknown",
                "our_angle": input_data.our_angle or "None specified",
                "variation_count": input_data.variation_count,
                "has_image_attachment": "yes" if input_data.kb_documents else "no",
            },
        )

        user_prompt = prompt_config["user"]
        if context_str:
            user_prompt = f"{context_str}\n\n---\n\n{user_prompt}"

        response_text = await llm_router.generate_text(
            prompt=user_prompt,
            system_prompt=prompt_config["system"],
            model_tier="quality",
            response_format={"type": "json_object"},
        )

        try:
            data = safe_json_parse(response_text)
            if not isinstance(data, dict):
                raise ValueError("LLM response is not a JSON object")

            analysis = _normalize_analysis(data)
            variations = _normalize_variations(data)
            insights = data.get("key_insights") or []
            if not isinstance(insights, list):
                insights = []
            insights = [str(i) for i in insights if i]

            text_content = _build_text_content(analysis, variations, insights)

            return CompetitorIntelligenceOutput(
                agent_id=self.agent_id,
                competitor_name=input_data.competitor_name,
                content_type=input_data.content_type,
                analysis=analysis,
                rewritten_variations=variations,
                key_insights=insights,
                text_content=text_content,
                structured_data=data,
            )
        except Exception as exc:
            logger.error("CompetitorIntelligenceAgent parse error: %s", exc)
            return CompetitorIntelligenceOutput(
                agent_id=self.agent_id,
                success=True,
                error=f"Parsing error: {exc}",
                competitor_name=input_data.competitor_name,
                content_type=input_data.content_type,
                text_content=response_text,
                structured_data={"raw_response": response_text},
            )
