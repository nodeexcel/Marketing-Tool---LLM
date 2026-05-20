"""Pydantic I/O for the Competitor Intelligence agent.

The user pastes a competitor's email / SMS / ad / landing-page copy; the agent
breaks down what makes it work and rewrites it for the user's brand using the
workspace context (brand voice, audience, etc.) that gets auto-injected.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.models.base import BaseAgentInput, BaseAgentOutput


ContentType = Literal[
    "email",
    "sms",
    "ad",
    "landing_page",
    "social_post",
    "blog",
    "other",
]


class CompetitorIntelligenceInput(BaseAgentInput):
    """User-provided competitor content to analyze and rewrite.

    At least one of `competitor_content`, `competitor_url`, or an attached image
    must be supplied — the agent will combine whichever sources are present.
    """

    competitor_content: Optional[str] = Field(
        None,
        description="Pasted text of the competitor's email, SMS, ad, etc. (optional if URL or image is provided).",
    )
    competitor_url: Optional[str] = Field(
        None,
        description="URL to scrape for the competitor's landing page, blog post, ad copy, etc.",
    )
    content_type: ContentType = Field(
        "email", description="What kind of content the user pasted/uploaded/linked."
    )
    competitor_name: Optional[str] = Field(
        None, description="Optional — competitor brand name for stronger analysis."
    )
    our_angle: Optional[str] = Field(
        None,
        description=(
            "Optional — angle the user wants to emphasize when rewriting "
            "(e.g. 'lead with our 30-day guarantee')."
        ),
    )
    variation_count: int = Field(
        3, ge=1, le=5, description="How many rewritten versions to produce."
    )


class CompetitorAnalysis(BaseModel):
    """Structured breakdown of what makes the competitor piece work."""

    hook: str = ""                 # The opening line / attention grab
    pain_points: List[str] = []    # Pain points the piece targets
    persuasion_patterns: List[str] = []  # FOMO, social proof, urgency, etc.
    primary_cta: str = ""          # The call-to-action language
    tone_summary: str = ""         # Brief tone description (e.g. "urgent and informal")
    structural_notes: List[str] = []  # How the piece is laid out
    strengths: List[str] = []      # What's working
    weaknesses: List[str] = []     # What could be improved


class RewrittenVariation(BaseModel):
    """A single rewritten variation aligned to the user's brand."""

    variation_name: str = ""       # e.g. "Punchy", "Story-driven", "Direct"
    subject_line: Optional[str] = None  # For email
    content: str = ""              # The full rewritten copy
    rationale: str = ""            # Why this version works for our brand


class CompetitorIntelligenceOutput(BaseAgentOutput):
    """Analysis + rewritten variations of the competitor piece."""

    competitor_name: Optional[str] = None
    content_type: ContentType = "email"
    analysis: CompetitorAnalysis = Field(default_factory=CompetitorAnalysis)
    rewritten_variations: List[RewrittenVariation] = []
    key_insights: List[str] = []   # Bullet takeaways across the whole analysis
