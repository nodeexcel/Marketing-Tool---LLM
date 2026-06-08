from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel
from app.models.base import BaseAgentInput, BaseAgentOutput

# Import specific agent models as we define them
# For now, we define the structure of the registry

class AgentMetadata(BaseModel):
    agent_id: str
    name: str
    description: str
    category: str
    icon: str  # Lucide icon name or similar
    input_model: Type[BaseAgentInput]
    output_model: Type[BaseAgentOutput]
    is_implemented: bool = False

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}

    def register(self, metadata: AgentMetadata):
        self._agents[metadata.agent_id] = metadata

    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        return self._agents.get(agent_id)

    def list_agents(self, category: Optional[str] = None) -> List[AgentMetadata]:
        if category:
            return [a for a in self._agents.values() if a.category == category]
        return list(self._agents.values())

    def get_categories(self) -> List[str]:
        return list(set(a.category for a in self._agents.values()))

# Global Singleton
registry = AgentRegistry()

# Forward reference to avoid circular imports during registration
def populate_registry():
    from app.agents.brand.models import (
        BrandIdentityInput, BrandIdentityOutput,
        BrandNamingInput, BrandNamingOutput,
        TaglineInput, TaglineOutput,
        TargetAudienceInput, TargetAudienceOutput,
        BrandVoiceInput, BrandVoiceOutput,
        BrandGuardianInput, BrandGuardianOutput
    )
    from app.agents.visual_strategy_models import (
        CreativeDirectionInput, CreativeDirectionOutput,
        CampaignConceptInput, CampaignConceptOutput,
        ContentCalendarInput, ContentCalendarOutput,
        HeroImageInput, HeroImageOutput,
        ProductPhotoshootInput, ProductPhotoshootOutput,
        AdCreativeInput, AdCreativeOutput,
        ImageEditorInput, ImageEditorOutput,
        MockupInput, MockupOutput,
        InfographicInput, InfographicOutput,
    )
    from app.agents.social_models import (
        InstagramAgentInput, InstagramAgentOutput,
        FacebookAgentInput, FacebookAgentOutput,
    )
    from app.agents.video_models import (
        VideoScriptInput, VideoScriptOutput,
        VideoGenInput, VideoGenOutput,
    )
    from app.agents.content_models import (
        ContentInput, ContentOutput,
        AdCopyInput, AdCopyOutput,
        SEOInput, SEOOutput,
    )
    from app.agents.utility_models import (
        UtilityInput, UtilityOutput,
    )

    # 🏷️ CATEGORY 1: BRAND IDENTITY (6)
    registry.register(AgentMetadata(
        agent_id="brand_identity", name="Brand Identity Builder",
        description="Creates complete brand identity — colors, fonts, mood, visual style, values.",
        category="brand", icon="Fingerprint", input_model=BrandIdentityInput, output_model=BrandIdentityOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="brand_naming", name="Brand Naming Agent",
        description="Generates creative brand name options with rationale and domain suggestions.",
        category="brand", icon="Type", input_model=BrandNamingInput, output_model=BrandNamingOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="tagline_slogan", name="Tagline & Slogan Agent",
        description="Creates memorable taglines and slogans ranked by tone and memorability.",
        category="brand", icon="Quote", input_model=TaglineInput, output_model=TaglineOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="target_audience", name="Target Audience Analyzer",
        description="Defines detailed buyer personas with psychographics and channel preferences.",
        category="brand", icon="Users", input_model=TargetAudienceInput, output_model=TargetAudienceOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="brand_voice", name="Brand Voice Analyzer",
        description="Analyzes content to extract brand tone, rules, and personality.",
        category="brand", icon="Mic", input_model=BrandVoiceInput, output_model=BrandVoiceOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="brand_guardian", name="Brand Guardian",
        description="Validates content against brand standards and guidelines.",
        category="brand", icon="ShieldCheck", input_model=BrandGuardianInput, output_model=BrandGuardianOutput, is_implemented=True
    ))

    # 🎨 CATEGORY 2: CREATIVE STRATEGY (3)
    registry.register(AgentMetadata(
        agent_id="creative_direction", name="Creative Direction Agent",
        description="Sets visual and mood direction for campaigns.",
        category="strategy", icon="Compass", input_model=CreativeDirectionInput, output_model=CreativeDirectionOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="campaign_concept", name="Campaign Concept Agent",
        description="Generates high-level themes and messaging for marketing campaigns.",
        category="strategy", icon="Lightbulb", input_model=CampaignConceptInput, output_model=CampaignConceptOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="content_calendar", name="Content Calendar Planner",
        description="Plans a strategic content schedule across multiple channels.",
        category="strategy", icon="Calendar", input_model=ContentCalendarInput, output_model=ContentCalendarOutput, is_implemented=True
    ))

    # 🖼️ CATEGORY 3: VISUAL DESIGN (6)
    registry.register(AgentMetadata(
        agent_id="hero_image", name="Image Generator",
        description="Creates high-impact banner and hero images.",
        category="visual", icon="Image", input_model=HeroImageInput, output_model=HeroImageOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="product_photoshoot", name="Product Photoshoot",
        description="Places products in professional studio or lifestyle scenes.",
        category="visual", icon="Camera", input_model=ProductPhotoshootInput, output_model=ProductPhotoshootOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="ad_creative", name="Ad Creative Designer",
        description="Designs platform-ready visual ads with headlines.",
        category="visual", icon="Sparkles", input_model=AdCreativeInput, output_model=AdCreativeOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="image_editor", name="Image Editor (AI)",
        description="Applies sophisticated AI edits to existing images.",
        category="visual", icon="Edit", input_model=ImageEditorInput, output_model=ImageEditorOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="mockup_generator", name="Mockup Generator",
        description="Renders designs onto real-world product mockups.",
        category="visual", icon="Box", input_model=MockupInput, output_model=MockupOutput, is_implemented=True
    ))
    registry.register(AgentMetadata(
        agent_id="infographic", name="Infographic Generator",
        description="Transforms data and concepts into visual infographics.",
        category="visual", icon="BarChart", input_model=InfographicInput, output_model=InfographicOutput, is_implemented=True
    ))

    # 📱 CATEGORY 4: SOCIAL MEDIA (5) — Instagram + Facebook only
    for aid in ["instagram_post", "instagram_story", "instagram_reel"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=f"IG {aid.split('_')[1].title()}", description=f"Optimized Instagram {aid.split('_')[1]} content.",
            category="social", icon="Instagram", input_model=InstagramAgentInput, output_model=InstagramAgentOutput, is_implemented=True
        ))
    for aid in ["facebook_post", "facebook_ad_copy"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=f"FB {aid.split('_')[1].title()}", description=f"Engagement-focused Facebook {aid.split('_')[1]}.",
            category="social", icon="Facebook", input_model=FacebookAgentInput, output_model=FacebookAgentOutput, is_implemented=True
        ))

    # 🎬 CATEGORY 5: VIDEO & MOTION (4)
    for aid in ["video_ad_script", "youtube_script", "ai_video_gen", "thumbnail_idea"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=aid.replace('_', ' ').title(), description=f"Platform-optimized {aid.replace('_', ' ')}.",
            category="video", icon="Video", input_model=VideoScriptInput, output_model=VideoScriptOutput, is_implemented=True
        ))

    # 📝 CATEGORY 6: CONTENT & COPY (6)
    for aid in ["blog_post", "email_campaign", "newsletter", "landing_page", "product_description", "faq_generator"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=aid.replace('_', ' ').title(), description=f"Expert {aid.replace('_', ' ')} writing.",
            category="content", icon="Pen", input_model=ContentInput, output_model=ContentOutput, is_implemented=True
        ))

    # 💰 CATEGORY 7: ADVERTISING COPY (4)
    for aid in ["meta_ads", "google_search_ads", "google_display_ads", "youtube_ads"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=aid.replace('_', ' ').title(), description=f"High-ROI {aid.replace('_', ' ')}.",
            category="ads", icon="DollarSign", input_model=AdCopyInput, output_model=AdCopyOutput, is_implemented=True
        ))

    # 🔍 CATEGORY 8: SEO & AEO (4)
    for aid in ["keyword_researcher", "on_page_seo", "technical_seo", "aeo_optimizer"]:
        registry.register(AgentMetadata(
            agent_id=aid, name=aid.replace('_', ' ').title(), description=f"Ranking-focused {aid.replace('_', ' ')}.",
            category="seo", icon="Search", input_model=SEOInput, output_model=SEOOutput, is_implemented=True
        ))

    # 🛠️ CATEGORY 9: ADAPTATION & UTILITIES (1)
    registry.register(AgentMetadata(
        agent_id="custom_workflow", name="Content Adaptor",
        description="Repurposes content for different platforms and formats.",
        category="utility", icon="Repeat", input_model=UtilityInput, output_model=UtilityOutput, is_implemented=True
    ))

    # 🕵️ CATEGORY 10: INTELLIGENCE (2 — Phase 3)
    from app.agents.competitor_intelligence_models import (
        CompetitorIntelligenceInput, CompetitorIntelligenceOutput,
    )
    registry.register(AgentMetadata(
        agent_id="competitor_intelligence",
        name="Competitor Intelligence",
        description="Analyzes competitor marketing copy and rewrites it in your brand voice.",
        category="growth",
        icon="Telescope",
        input_model=CompetitorIntelligenceInput,
        output_model=CompetitorIntelligenceOutput,
        is_implemented=True,
    ))

    from app.agents.trend_scanner_models import (
        TrendScannerInput, TrendScannerOutput,
    )
    registry.register(AgentMetadata(
        agent_id="trend_scanner",
        name="Trend Scanner",
        description="Scans a niche across multiple URLs and surfaces what's working, what's saturated, and where the gaps are.",
        category="growth",
        icon="Radar",
        input_model=TrendScannerInput,
        output_model=TrendScannerOutput,
        is_implemented=True,
    ))

# Auto-populate on import
populate_registry()
