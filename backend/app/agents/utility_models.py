from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.models.base import BaseAgentInput, BaseAgentOutput, GeneratedAsset

# --- CATEGORY: ADAPTATION & UTILITIES ---

class UtilityInput(BaseAgentInput):
    agent_id: Literal["custom_workflow"]
    source_content: str
    target_formats: List[str]             # ["blog -> twitter", "video -> email"]

class UtilityOutput(BaseAgentOutput):
    converted_content: Dict[str, str]
