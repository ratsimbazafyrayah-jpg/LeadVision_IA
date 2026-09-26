from fastapi import FastAPI

from app.database.mongodb import check_database_connection
from app.routes.leads import router as leads_router
from app.routes.lead_interactions import router as lead_interactions_router
from app.routes.commercial_signals import router as commercial_signals_router

app = FastAPI(
    title="LeadVision_IA API",
    description="API de prospection intelligente",
    version="1.0.0"
)


# Routes
app.include_router(leads_router)
app.include_router(commercial_signals_router)

app.include_router(lead_interactions_router)


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