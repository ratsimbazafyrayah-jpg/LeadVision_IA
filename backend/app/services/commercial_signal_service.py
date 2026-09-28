from typing import Dict, Any, List

from app.services.commercial_signal_rules import (
    classify_interaction,
)
from app.schemas.commercial_signal_detail import (
    CommercialSignal,
)


def analyze_commercial_signals(
    interactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyse les interactions réellement enregistrées.

    Tsy mamorona donnée na score commercial.
    Ny signal dia tsy maintsy avy amin'ny règle valide.
    """

    signals = []
    ignored_interactions = []

    for interaction in interactions:
        classification = classify_interaction(interaction)

        if classification["is_signal"]:
            signal = CommercialSignal(
                interaction_id=str(interaction.get("_id")),
                signal_type=classification["classification"],
                source=interaction.get("source"),
                occurred_at=interaction.get("occurred_at"),
                evidence={
                    "source_system": interaction.get("source"),
                    "metadata": interaction.get("metadata") or {},
                },
                validation_reason=classification["reason"],
                confidence=None,
            )

            signals.append(signal.model_dump())

        else:
            ignored_interactions.append({
                "interaction_id": str(interaction.get("_id")),
                "classification": classification["classification"],
                "reason": classification["reason"],
            })

    if signals:
        status = "signals_available"
    else:
        status = "insufficient_signals"

    return {
        "status": status,
        "signal_count": len(signals),
        "signals": signals,
        "ignored_interactions": ignored_interactions,
    }
