from datetime import datetime, timezone
from typing import Dict, Any, List


# Poids méthodologiques du Commercial Score.
# Ces poids sont une première méthodologie de travail,
# et ne constituent pas une validation statistique.
INTENT_WEIGHT = 0.40
RECENCY_WEIGHT = 0.25
DIVERSITY_WEIGHT = 0.20
EVIDENCE_WEIGHT = 0.15


def _calculate_intent(signals: List[Dict[str, Any]]) -> float:
    """
    Mesure l'intensité observable de l'intention commerciale
    à partir du nombre de signaux commerciaux validés.

    Aucun point fixe n'est attribué à un type de signal.
    La mesure est normalisée sur le nombre de signaux observés.
    """
    if not signals:
        return 0.0

    signal_count = len(signals)

    # Saturation progressive : plus il existe de signaux valides,
    # plus l'intention observée augmente, sans dépasser 100.
    return round(
        min(100.0, signal_count * 25.0),
        2,
    )


def _calculate_recency(signals: List[Dict[str, Any]]) -> float:
    """
    Mesure la récence du signal commercial le plus récent.

    100 = signal observé maintenant.
    0 = signal datant d'au moins 90 jours.

    Si la date est absente ou invalide, le signal n'est pas utilisé
    pour le calcul de récence.
    """
    dated_signals = []

    for signal in signals:
        occurred_at = signal.get("occurred_at")

        if not isinstance(occurred_at, datetime):
            continue

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        dated_signals.append(occurred_at)

    if not dated_signals:
        return 0.0

    latest_signal = max(dated_signals)
    now = datetime.now(timezone.utc)

    age_days = max(
        0.0,
        (now - latest_signal).total_seconds() / 86400,
    )

    recency = max(
        0.0,
        100.0 * (1.0 - (age_days / 90.0)),
    )

    return round(recency, 2)


def _calculate_diversity(signals: List[Dict[str, Any]]) -> float:
    """
    Mesure la diversité des sources commerciales observées.

    Une seule source = 1 source observée.
    Plusieurs sources indépendantes augmentent la diversité.

    Maximum méthodologique actuel : 5 sources distinctes.
    """
    sources = {
        signal.get("source")
        for signal in signals
        if signal.get("source")
    }

    if not sources:
        return 0.0

    return round(
        min(100.0, (len(sources) / 5.0) * 100.0),
        2,
    )


def _calculate_evidence(signals: List[Dict[str, Any]]) -> float:
    """
    Mesure la présence de preuves traçables pour les signaux.

    Un signal est considéré comme correctement documenté
    lorsqu'il possède:
    - interaction_id
    - validation_reason
    - source
    """
    if not signals:
        return 0.0

    documented = 0

    for signal in signals:
        if (
            signal.get("interaction_id")
            and signal.get("validation_reason")
            and signal.get("source")
        ):
            documented += 1

    return round(
        (documented / len(signals)) * 100.0,
        2,
    )


def calculate_commercial_score(
    signals: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calcule le Commercial Score 0-100 uniquement à partir
    de signaux commerciaux déjà validés.

    Le score mesure la force des signaux commerciaux observés.
    Il ne représente PAS une probabilité d'achat.
    """

    valid_signals = [
        signal
        for signal in signals
        if (
            signal.get("signal_type")
            and signal.get("interaction_id")
            and signal.get("validation_reason")
        )
    ]

    if not valid_signals:
        return {
            "commercial_score": None,
            "status": "insufficient_signals",
            "confidence": None,
            "signals_used": [],
            "evidence": [],
            "calculation": None,
        }

    intent = _calculate_intent(valid_signals)
    recency = _calculate_recency(valid_signals)
    diversity = _calculate_diversity(valid_signals)
    evidence = _calculate_evidence(valid_signals)

    commercial_score = round(
        (intent * INTENT_WEIGHT)
        + (recency * RECENCY_WEIGHT)
        + (diversity * DIVERSITY_WEIGHT)
        + (evidence * EVIDENCE_WEIGHT),
        2,
    )

    commercial_score = max(
        0.0,
        min(100.0, commercial_score),
    )

    calculation = {
        "method": "intent_recency_diversity_evidence",
        "scale": "0-100",
        "interpretation": (
            "force_des_signaux_commerciaux_observes"
        ),
        "weights": {
            "intent": INTENT_WEIGHT,
            "recency": RECENCY_WEIGHT,
            "diversity": DIVERSITY_WEIGHT,
            "evidence": EVIDENCE_WEIGHT,
        },
        "dimensions": {
            "intent": intent,
            "recency": recency,
            "diversity": diversity,
            "evidence": evidence,
        },
        "formula": (
            "intent*0.40 + recency*0.25 + "
            "diversity*0.20 + evidence*0.15"
        ),
    }

    evidence_list = [
        {
            "interaction_id": signal.get("interaction_id"),
            "signal_type": signal.get("signal_type"),
            "source": signal.get("source"),
            "validation_reason": signal.get("validation_reason"),
            "occurred_at": signal.get("occurred_at"),
        }
        for signal in valid_signals
    ]

    return {
        "commercial_score": commercial_score,
        "status": "score_available",
        "confidence": evidence,
        "signals_used": [
            signal.get("interaction_id")
            for signal in valid_signals
        ],
        "evidence": evidence_list,
        "calculation": calculation,
    }
