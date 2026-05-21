import json
import re
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.base import BaseAgentInput, BaseAgentOutput, GeneratedAsset

# --- CATEGORY 4: SOCIAL MEDIA (Instagram + Facebook only) ---

class SocialPost(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: str
    caption: str
    image_prompts: List[str] = []
    video_prompts: List[str] = []
    hashtags: List[str] = []
    posting_time_suggestion: str = "Morning"
    post_index: int = 0
    assets: List[GeneratedAsset] = []

# 4.1 Instagram
class InstagramAgentInput(BaseAgentInput):
    agent_id: Literal["instagram_post", "instagram_story", "instagram_reel", "instagram_carousel", "instagram_bio"]
    topic: str
    visual_theme: Optional[str] = None
    tone_override: Optional[str] = None
    keywords: List[str] = []
    format: Optional[str] = None
    hook_style: Optional[str] = None
    slide_count: Optional[int] = None
    frame_count: Optional[int] = None
    sticker_cta: Optional[str] = None
    story_sequence: Optional[str] = None
    shot_list: Optional[List[str]] = None
    audio_reference: Optional[str] = None
    duration_seconds: Optional[int] = None
    slide_goal: Optional[str] = None
    final_slide_cta: Optional[str] = None

    @field_validator("shot_list", mode="before")
    @classmethod
    def normalize_shot_list(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []

            # Support JSON-list text coming from custom clients.
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass

            # Support comma/newline/bullet-separated textarea input.
            tokens = [
                part.strip(" \t\r\n-*•")
                for part in re.split(r"[,\n;]+", raw)
            ]
            return [token for token in tokens if token]
        return value


class InstagramAgentOutput(BaseAgentOutput):
    post: Optional[SocialPost] = None
    posts: List[SocialPost] = []
    alternate_captions: List[str] = []

# 4.2 Facebook
class FacebookAgentInput(BaseAgentInput):
    agent_id: Literal["facebook_post", "facebook_ad_copy"]
    topic: str
    goal: str = "engagement"                # "engagement", "traffic", "leads"
    tone_override: Optional[str] = None
    include_link: bool = False
    audience_segment: Optional[str] = None
    campaign_stage: Optional[str] = None


class FacebookAgentOutput(BaseAgentOutput):
    post: Optional[SocialPost] = None
    posts: List[SocialPost] = []
