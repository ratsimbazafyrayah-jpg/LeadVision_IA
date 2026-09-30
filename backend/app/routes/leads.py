from fastapi import APIRouter, HTTPException

from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.lead_service import (
    create_lead,
    get_leads,
    get_lead,
    update_lead,
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


@router.put("/{lead_id}")
def update_single_lead(lead_id: str, lead: LeadUpdate):

    try:
        updated_lead = update_lead(
            lead_id,
            lead.model_dump(exclude_unset=True),
        )

        if updated_lead is None:
            raise HTTPException(
                status_code=404,
                detail="Lead introuvable"
            )

        return updated_lead

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


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