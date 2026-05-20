"""Pydantic I/O for the Trend Scanner agent.

The user provides a niche/topic and a list of URLs (industry blogs, competitor
newsletters, Reddit threads, trending content pages). The shared
`urls_to_scrape` field on `BaseAgentInput` is the source of URLs; the scraper
service hydrates them before the agent runs. Claude then identifies recurring
themes, hooks, formats, gaps, and recommendations across the scraped corpus.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.models.base import BaseAgentInput, BaseAgentOutput


TimeHorizon = Literal["last_week", "last_month", "last_quarter", "evergreen"]
ScanDepth = Literal["quick", "standard", "deep"]


class TrendScannerInput(BaseAgentInput):
    """User-provided niche context. URLs come from `urls_to_scrape` (shared)."""

    niche: str = Field(
        ..., description="The space being scanned (e.g. 'children's organic snacks', 'B2B SaaS onboarding')."
    )
    our_brand_focus: Optional[str] = Field(
        None,
        description="Optional — the user's brand angle or positioning, so recommendations stay on-brand.",
    )
    time_horizon: TimeHorizon = Field(
        "last_month",
        description="How recent the trends should be. Evergreen = patterns that aren't time-sensitive.",
    )
    scan_depth: ScanDepth = Field(
        "standard",
        description="Quick (top 3 of each), Standard (top 5), Deep (top 8 with detailed evidence).",
    )


class TrendingTheme(BaseModel):
    theme: str = ""
    why_now: str = ""             # Why this is trending right now
    evidence_count: int = 0        # How many sources show this pattern
    example_hooks: List[str] = []  # Sample opening lines/headlines


class RecurringHook(BaseModel):
    hook_pattern: str = ""         # The pattern description (e.g. "Counterintuitive claim → personal story")
    examples: List[str] = []       # Concrete instances from the scraped content
    when_to_use: str = ""          # When this pattern is most effective


class ContentFormat(BaseModel):
    format_name: str = ""          # e.g. "Listicle with comparison table"
    why_trending: str = ""
    examples: List[str] = []


class GapOpportunity(BaseModel):
    opportunity: str = ""
    why_underserved: str = ""
    angle_for_user: str = ""       # How the user's brand could uniquely fill this


class TrendScannerOutput(BaseAgentOutput):
    niche: str = ""
    time_horizon: TimeHorizon = "last_month"
    sources_analyzed: int = 0
    summary: str = ""                              # 2-3 sentence executive summary
    trending_themes: List[TrendingTheme] = []
    recurring_hooks: List[RecurringHook] = []
    content_formats: List[ContentFormat] = []
    saturated_angles: List[str] = []               # Things that are oversaturated; avoid
    gaps_and_opportunities: List[GapOpportunity] = []
    recommended_actions: List[str] = []            # Concrete next moves for the user
    key_insights: List[str] = []                   # Bullet takeaways
