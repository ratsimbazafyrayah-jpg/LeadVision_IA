from datetime import datetime
from typing import Optional, Dict, Any

from bson import ObjectId

from app.database.mongodb import db
from app.models.lead_interaction import (
    build_lead_interaction_document,
)


interactions_collection = db["lead_interactions"]


def create_lead_interaction(
    lead_id: str,
    interaction_type: str,
    source: str,
    occurred_at: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Mamorona interaction ho an'ny lead iray.

    Ny interaction dia tsy mamorona score.
    Ny données tena voaray ihany no tehirizina.
    """

    if not ObjectId.is_valid(lead_id):
        raise ValueError("lead_id invalide")

    document = build_lead_interaction_document(
        lead_id=lead_id,
        interaction_type=interaction_type,
        source=source,
        occurred_at=occurred_at,
        metadata=metadata,
    )

    result = interactions_collection.insert_one(document)

    document["_id"] = str(result.inserted_id)

    return document


def get_lead_interactions(lead_id: str):
    """
    Maka ny interactions rehetra an'ny lead iray.
    """

    if not ObjectId.is_valid(lead_id):
        raise ValueError("lead_id invalide")

    interactions = []

    cursor = interactions_collection.find(
        {"lead_id": lead_id}
    ).sort("occurred_at", -1)

    for interaction in cursor:
        interaction["_id"] = str(interaction["_id"])
        interactions.append(interaction)

    return interactions
