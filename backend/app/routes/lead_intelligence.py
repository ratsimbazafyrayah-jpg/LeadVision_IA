from fastapi import APIRouter, HTTPException, Request
from app.schemas.ai_analysis import AIAnalysisResponse
from app.schemas.ai_analysis_input import AIAnalysisInput
from app.services.ai.ai_analysis_service import AIAnalysisService
from app.services.lead_service import get_lead
from app.services.lead_interaction_service import get_lead_interactions
from app.services.lead_intelligence_service import build_lead_intelligence


router = APIRouter(
    prefix="/api/leads",
    tags=["Lead Intelligence"],
)


@router.get("/{lead_id}/intelligence")
def get_lead_intelligence(lead_id: str):
    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable",
        )

    try:
        interactions = get_lead_interactions(lead_id)

        return build_lead_intelligence(
            lead=lead,
            interactions=interactions,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.get("/{lead_id}/ai-analysis")
def get_lead_ai_analysis(
    lead_id: str,
    request: Request,
):
    lead = get_lead(lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead introuvable",
        )

    try:
        interactions = get_lead_interactions(lead_id)

        intelligence = build_lead_intelligence(
            lead=lead,
            interactions=interactions,
        )

        data = AIAnalysisInput(**intelligence)

        provider = request.app.state.ai_provider

        service = AIAnalysisService(
            provider=provider
        )

        try:
            result = service.analyze(data)
            return result

        except RuntimeError as error:
            raise HTTPException(
                status_code=503,
                detail=str(error),
            )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )