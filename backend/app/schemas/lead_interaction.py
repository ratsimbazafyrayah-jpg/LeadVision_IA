from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class LeadInteractionCreate(BaseModel):
    interaction_type: str = Field(..., min_length=2, max_length=100)
    source: str = Field(..., min_length=2, max_length=100)
    occurred_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
