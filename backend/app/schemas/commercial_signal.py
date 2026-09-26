from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class CommercialSignalResponse(BaseModel):
    status: str
    signal_count: int
    signals: List[Dict[str, Any]]
    ignored_interactions: List[Dict[str, Any]]
    commercial_score: Optional[float] = None
