from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CommercialScoreResponse(BaseModel):
    commercial_score: Optional[float] = None
    status: str
    confidence: Optional[float] = None
    signals_used: List[str]
    evidence: List[Dict[str, Any]]
    calculation: Optional[Dict[str, Any]] = None
