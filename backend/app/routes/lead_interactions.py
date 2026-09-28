from fastapi import APIRouter, HTTPException, Request
from app.schemas.lead_interaction import LeadInteractionCreate
from app.services.lead_interaction_service import (
    create_lead_interaction,
    get_lead_interactions,
)
from app.services.lead_service import get_lead


router = APIRouter(
    prefix="/api/leads",
    tags=["Lead Interactions"]
)


@router.post("/{lead_id}/interactions")
def create_interaction(
    lead_id: str,
    interaction: LeadInteractionCreate,
):
    """
    Ajoute une interaction réelle à un lead existant.
    """

    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable"
        )

    try:
        return create_lead_interaction(
            lead_id=lead_id,
            interaction_type=interaction.interaction_type,
            source=interaction.source,
            occurred_at=interaction.occurred_at,
            metadata=interaction.metadata,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{lead_id}/interactions")
def list_interactions(lead_id: str):
    """
    Retourne les interactions réelles d'un lead.
    """

    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable"
        )

    try:
        return get_lead_interactions(lead_id)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
