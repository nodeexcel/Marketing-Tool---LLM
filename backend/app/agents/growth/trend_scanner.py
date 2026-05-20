"""Trend Scanner agent — finds patterns across a corpus of niche content.

The user supplies a niche + URLs (via the shared `urls_to_scrape` field). The
api_router scrapes them; this agent feeds the scraped corpus to Claude to
identify trending themes, recurring hooks, dominant content formats, and gaps.
"""

import logging
from typing import Any, Dict, List

from app.agents.base import BaseV4Agent
from app.agents.trend_scanner_models import (
    ContentFormat,
    GapOpportunity,
    RecurringHook,
    TrendingTheme,
    TrendScannerInput,
    TrendScannerOutput,
)
from app.core.llm import llm_router
from app.utils.json_repair import safe_json_parse

logger = logging.getLogger(__name__)


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value if v not in (None, "")]
    if isinstance(value, str) and value:
        return [value]
    return []


def _normalize_themes(data: Dict[str, Any]) -> List[TrendingTheme]:
    raw = data.get("trending_themes") or []
    if not isinstance(raw, list):
        return []
    out: List[TrendingTheme] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(TrendingTheme(
            theme=str(item.get("theme") or ""),
            why_now=str(item.get("why_now") or ""),
            evidence_count=int(item.get("evidence_count") or 0),
            example_hooks=_as_list(item.get("example_hooks")),
        ))
    return out


def _normalize_hooks(data: Dict[str, Any]) -> List[RecurringHook]:
    raw = data.get("recurring_hooks") or []
    if not isinstance(raw, list):
        return []
    out: List[RecurringHook] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(RecurringHook(
            hook_pattern=str(item.get("hook_pattern") or ""),
            examples=_as_list(item.get("examples")),
            when_to_use=str(item.get("when_to_use") or ""),
        ))
    return out


def _normalize_formats(data: Dict[str, Any]) -> List[ContentFormat]:
    raw = data.get("content_formats") or []
    if not isinstance(raw, list):
        return []
    out: List[ContentFormat] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(ContentFormat(
            format_name=str(item.get("format_name") or ""),
            why_trending=str(item.get("why_trending") or ""),
            examples=_as_list(item.get("examples")),
        ))
    return out


def _normalize_gaps(data: Dict[str, Any]) -> List[GapOpportunity]:
    raw = data.get("gaps_and_opportunities") or []
    if not isinstance(raw, list):
        return []
    out: List[GapOpportunity] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(GapOpportunity(
            opportunity=str(item.get("opportunity") or ""),
            why_underserved=str(item.get("why_underserved") or ""),
            angle_for_user=str(item.get("angle_for_user") or ""),
        ))
    return out


def _build_text_content(out: TrendScannerOutput) -> str:
    """Render the structured output as Markdown for the rich-text editor."""
    parts: List[str] = [f"# Trend Scan — {out.niche}"]
    if out.summary:
        parts.append("")
        parts.append(out.summary)
    if out.sources_analyzed:
        parts.append(f"\n_{out.sources_analyzed} sources analyzed · {out.time_horizon.replace('_', ' ')}_")

    if out.trending_themes:
        parts.append("\n## Trending Themes")
        for t in out.trending_themes:
            parts.append(f"\n### {t.theme}")
            if t.why_now:
                parts.append(t.why_now)
            if t.example_hooks:
                parts.append("\n**Example hooks:**")
                parts.extend(f"- {h}" for h in t.example_hooks)

    if out.recurring_hooks:
        parts.append("\n## Recurring Hooks")
        for h in out.recurring_hooks:
            parts.append(f"\n### {h.hook_pattern}")
            if h.examples:
                parts.extend(f"- {e}" for e in h.examples)
            if h.when_to_use:
                parts.append(f"\n_When to use: {h.when_to_use}_")

    if out.content_formats:
        parts.append("\n## Content Formats")
        for f in out.content_formats:
            parts.append(f"\n**{f.format_name}** — {f.why_trending}")
            if f.examples:
                parts.extend(f"- {e}" for e in f.examples)

    if out.saturated_angles:
        parts.append("\n## Saturated Angles (avoid)")
        parts.extend(f"- {a}" for a in out.saturated_angles)

    if out.gaps_and_opportunities:
        parts.append("\n## Gaps & Opportunities")
        for g in out.gaps_and_opportunities:
            parts.append(f"\n**{g.opportunity}**")
            if g.why_underserved:
                parts.append(g.why_underserved)
            if g.angle_for_user:
                parts.append(f"\n_Your angle: {g.angle_for_user}_")

    if out.recommended_actions:
        parts.append("\n## Recommended Actions")
        parts.extend(f"- {a}" for a in out.recommended_actions)

    if out.key_insights:
        parts.append("\n## Key Insights")
        parts.extend(f"- {i}" for i in out.key_insights)

    return "\n".join(parts)


class TrendScannerAgent(BaseV4Agent):
    agent_id = "trend_scanner"
    agent_name = "Trend Scanner"
    description = "Scans a niche across multiple URLs and surfaces what's working, what's saturated, and where the gaps are."
    category = "growth"

    async def _execute_internal(
        self,
        input_data: TrendScannerInput,
        context_str: str,
    ) -> TrendScannerOutput:
        # Compose source corpus from the scraped URLs. The api_router scrapes
        # `urls_to_scrape` before this method runs; the results land on
        # input_data.scraped_content.
        scraped = input_data.scraped_content or []
        if not scraped:
            return TrendScannerOutput(
                agent_id=self.agent_id,
                success=False,
                error=(
                    "Trend Scanner needs at least one URL to scan. Add URLs in "
                    "the 'URLs to Scrape' panel on the left."
                ),
                niche=input_data.niche,
                time_horizon=input_data.time_horizon,
                text_content="No source URLs were provided.",
            )

        corpus_blocks: List[str] = []
        for i, item in enumerate(scraped, 1):
            url = getattr(item, "url", "") or "unknown"
            title = getattr(item, "title", "") or ""
            text = (getattr(item, "extracted_text", "") or "")[:6000]
            if not text.strip():
                continue
            corpus_blocks.append(
                f"<source index=\"{i}\" url=\"{url}\" title=\"{title}\">\n{text}\n</source>"
            )

        if not corpus_blocks:
            return TrendScannerOutput(
                agent_id=self.agent_id,
                success=False,
                error="All provided URLs returned empty content.",
                niche=input_data.niche,
                time_horizon=input_data.time_horizon,
                text_content="Scraping returned no usable text from the provided URLs.",
            )

        corpus = "\n\n".join(corpus_blocks)

        prompt_config = await self.get_prompt_config(
            input_data=input_data,
            default_system=(
                "You are a senior content strategist and trend analyst. "
                "Return ONLY a JSON object — no markdown, no commentary."
            ),
            default_user="",
            variables={
                "niche": input_data.niche,
                "our_brand_focus": input_data.our_brand_focus or "None specified",
                "time_horizon": input_data.time_horizon,
                "scan_depth": input_data.scan_depth,
            },
        )

        user_prompt = prompt_config["user"]
        # Append the actual corpus after the YAML-provided instructions so the
        # template doesn't have to know about variable scraped content.
        user_prompt = f"{user_prompt}\n\n<corpus>\n{corpus}\n</corpus>"
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

            themes = _normalize_themes(data)
            hooks = _normalize_hooks(data)
            formats = _normalize_formats(data)
            gaps = _normalize_gaps(data)
            saturated = _as_list(data.get("saturated_angles"))
            actions = _as_list(data.get("recommended_actions"))
            insights = _as_list(data.get("key_insights"))
            summary = str(data.get("summary") or "")
            sources_analyzed = int(data.get("sources_analyzed") or len(corpus_blocks))

            output = TrendScannerOutput(
                agent_id=self.agent_id,
                niche=input_data.niche,
                time_horizon=input_data.time_horizon,
                sources_analyzed=sources_analyzed,
                summary=summary,
                trending_themes=themes,
                recurring_hooks=hooks,
                content_formats=formats,
                saturated_angles=saturated,
                gaps_and_opportunities=gaps,
                recommended_actions=actions,
                key_insights=insights,
                structured_data=data,
            )
            output.text_content = _build_text_content(output)
            return output
        except Exception as exc:
            logger.error("TrendScannerAgent parse error: %s", exc)
            return TrendScannerOutput(
                agent_id=self.agent_id,
                success=True,
                error=f"Parsing error: {exc}",
                niche=input_data.niche,
                time_horizon=input_data.time_horizon,
                text_content=response_text,
                structured_data={"raw_response": response_text},
            )
