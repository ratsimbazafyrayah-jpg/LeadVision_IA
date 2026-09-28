from typing import Dict, Any, List

from app.services.lead_qualification_service import qualify_lead
from app.services.lead_scoring_service import calculate_lead_score
from app.services.commercial_signal_service import analyze_commercial_signals
from app.services.commercial_score_service import calculate_commercial_score


def build_evidence_registry(
    signals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Construit un registre d'evidences à partir des signaux commerciaux
    déjà validés.

    Tsy mamorona donnée métier vaovao.
    Ny evidence dia référence technique amin'ny signal existant.
    """

    registry = []

    for signal in signals:
        interaction_id = signal.get("interaction_id")
        signal_type = signal.get("signal_type")
        source = signal.get("source")
        validation_reason = signal.get("validation_reason")

        if not interaction_id:
            continue

        if not signal_type or not source or not validation_reason:
            continue

        registry.append({
            "evidence_id": f"commercial-signal:{interaction_id}",
            "evidence_type": "commercial_signal",
            "source": source,
            "reference_id": interaction_id,
            "description": validation_reason,
        })

    return registry


def build_lead_intelligence(
    lead: Dict[str, Any],
    interactions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Agrège les informations existantes d'un lead.

    Cette fonction ne crée aucun nouveau score.
    Elle réutilise uniquement les services métier existants :
    - qualification
    - data quality
    - commercial signals
    - commercial score
    """

    qualification = qualify_lead(lead)

    data_quality = calculate_lead_score(lead)

    commercial_signals = analyze_commercial_signals(
        interactions
    )

    signals = commercial_signals.get("signals", [])

    commercial_score = calculate_commercial_score(
        signals
    )

    evidence_registry = build_evidence_registry(signals)

    return {
        "lead": lead,
        "qualification": qualification,
        "data_quality": data_quality,
        "commercial_signals": commercial_signals,
        "commercial_score": commercial_score,
        "evidence_registry": evidence_registry,
    }
