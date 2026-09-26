from datetime import datetime, timezone
from typing import Optional, Dict, Any


def build_lead_interaction_document(
    lead_id: str,
    interaction_type: str,
    source: str,
    occurred_at: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Mamorona interaction commerciale mifototra amin'ny
    donnée tena misy.

    Tsy mamorona score na valeur commerciale automatique.
    """

    now = datetime.now(timezone.utc)

    return {
        "lead_id": lead_id,
        "type": interaction_type,
        "source": source,
        "occurred_at": occurred_at or now,
        "metadata": metadata or {},
        "created_at": now,
    }
