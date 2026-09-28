from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import check_database_connection
from app.routes.leads import router as leads_router
from app.routes.lead_interactions import router as lead_interactions_router
from app.routes.commercial_signals import router as commercial_signals_router
from app.routes.lead_intelligence import router as lead_intelligence_router
from app.routes.discovery import router as discovery_router
from app.services.ai.ai_provider_factory import create_ai_provider
from app.services.discovery.source_factory import build_discovery_sources
from app.services.discovery.source_registry import DiscoverySourceRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_provider = create_ai_provider()

    discovery_sources = build_discovery_sources()
    app.state.discovery_sources = DiscoverySourceRegistry(discovery_sources)

    try:
        yield
    finally:
        http_client = getattr(
            app.state.ai_provider,
            "http_client",
            None,
        )

        if http_client is not None:
            http_client.close()

        discovery_sources = getattr(
            app.state,
            "discovery_sources",
            None,
        )

        if discovery_sources is not None:
            discovery_sources.close()


app = FastAPI(
    title="LeadVision_IA API",
    description="API de prospection intelligente",
    version="1.0.0",
    lifespan=lifespan,
)


# Routes
app.include_router(leads_router)
app.include_router(commercial_signals_router)
app.include_router(lead_interactions_router)
app.include_router(lead_intelligence_router)
app.include_router(discovery_router)


@app.get("/")
def root():
    return {
        "application": "LeadVision_IA",
        "status": "online"
    }


@app.get("/health")
def health():
    mongodb_status = check_database_connection()

    return {
        "api": "ok",
        "mongodb": "connected" if mongodb_status else "disconnected"
    }