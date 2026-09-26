from fastapi import APIRouter, HTTPException

from app.schemas.commercial_signal import CommercialSignalResponse
from app.services.commercial_signal_service import (
    analyze_commercial_signals,
)
from app.services.lead_interaction_service import (
    get_lead_interactions,
)
from app.services.lead_service import get_lead


router = APIRouter(
    prefix="/api/leads",
    tags=["Commercial Signals"],
)


@router.get(
    "/{lead_id}/commercial-signals",
    response_model=CommercialSignalResponse,
)
def get_commercial_signals(lead_id: str):
    """
    Retourne les signaux commerciaux détectables
    à partir des interactions réellement enregistrées.
    """

    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable",
        )

    try:
        interactions = get_lead_interactions(lead_id)

        return analyze_commercial_signals(interactions)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
