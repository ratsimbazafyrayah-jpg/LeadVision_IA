from fastapi import APIRouter, HTTPException

from app.schemas.lead import LeadCreate
from app.services.lead_service import (
    create_lead,
    get_leads,
    get_lead,
)
from app.services.lead_qualification_service import qualify_lead


router = APIRouter(
    prefix="/api/leads",
    tags=["Leads"]
)


@router.post("/")
def create_new_lead(lead: LeadCreate):

    try:
        return create_lead(lead.model_dump())

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/")
def list_leads():
    return get_leads()


@router.get("/{lead_id}")
def get_single_lead(lead_id: str):

    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable"
        )

    return lead

@router.get("/{lead_id}/qualification")
def qualify_single_lead(lead_id: str):

    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable"
        )

    qualification = qualify_lead(lead)

    return {
        "lead_id": lead_id,
        "qualification": qualification,
    }