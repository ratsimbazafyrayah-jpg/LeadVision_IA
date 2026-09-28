from fastapi import APIRouter, HTTPException, Request

from app.schemas.discovery import DiscoverySearchRequest, DiscoveryImportRequest
from app.services.discovery.search_service import search_prospects
from app.services.discovery.discovery_service import import_prospects


router = APIRouter(
    prefix="/api/discovery",
    tags=["Discovery"],
)


@router.post("/search")
def discovery_search(
    payload: DiscoverySearchRequest,
    request: Request,
):
    try:
        source = request.app.state.discovery_sources.get(payload.source)

        return search_prospects(
            request=payload,
            source=source,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail="La source de découverte est indisponible.",
        ) from error


@router.post("/import")
def discovery_import(payload: DiscoveryImportRequest):
    try:
        return import_prospects(
            prospects=payload.prospects,
            source=payload.source,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
