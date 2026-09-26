from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class CommercialSignal(BaseModel):
    interaction_id: str
    signal_type: str
    source: str
    occurred_at: datetime
    evidence: Dict[str, Any]
    validation_reason: str
    confidence: Optional[float] = None
