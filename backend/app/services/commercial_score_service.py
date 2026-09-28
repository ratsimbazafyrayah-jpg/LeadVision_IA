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
    Mesure l'intensité observable des signaux commerciaux validés.

    L'Intent V1 combine:
    - volume des signaux: 40 %
    - diversité des types de signaux: 30 %
    - récurrence temporelle: 30 %

    Le score ne représente pas une probabilité d'achat.
    """

    if not signals:
        return 0.0

    signal_count = len(signals)

    # Volume avec rendement décroissant.
    volume = 100.0 * signal_count / (signal_count + 1.0)

    # Les types disponibles sont ceux définis par les règles
    # commerciales de LeadVision_IA.
    allowed_signal_types = {
        "form_submission",
        "email_reply",
        "meeting_booked",
        "demo_request",
        "quote_request",
        "contact_request",
    }

    signal_types = {
        signal.get("signal_type")
        for signal in signals
        if signal.get("signal_type") in allowed_signal_types
    }

    diversity = (
        100.0 * len(signal_types) / len(allowed_signal_types)
        if signal_types
        else 0.0
    )

    # Récurrence observée sur une fenêtre de 90 jours.
    # Les dates sont normalisées en UTC et les dates civiles
    # distinctes représentent les jours d'activité observée.
    active_days = set()

    for signal in signals:
        occurred_at = signal.get("occurred_at")

        if not isinstance(occurred_at, datetime):
            continue

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        age_days = (
            datetime.now(timezone.utc) - occurred_at
        ).total_seconds() / 86400

        if 0 <= age_days <= 90:
            active_days.add(occurred_at.date())

    if len(active_days) <= 1:
        recurrence = 0.0
    else:
        recurrence = min(
            100.0,
            100.0 * (len(active_days) - 1) / 89.0,
        )

    intent = (
        (volume * 0.40)
        + (diversity * 0.30)
        + (recurrence * 0.30)
    )

    return round(
        max(0.0, min(100.0, intent)),
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

    La diversité est calculée à partir de la répartition réelle
    des signaux entre les différentes sources.

    Méthode :
    Diversity = (1 - HHI) * 100

    où HHI = somme des carrés des parts de chaque source.

    Une seule source dominante produit une diversité de 0.
    Une répartition plus équilibrée entre plusieurs sources
    produit une diversité plus élevée.
    """
    sources = [
        signal.get("source")
        for signal in signals
        if signal.get("source")
    ]

    if not sources:
        return 0.0

    total = len(sources)

    source_counts = {}

    for source in sources:
        source_counts[source] = source_counts.get(source, 0) + 1

    hhi = sum(
        (count / total) ** 2
        for count in source_counts.values()
    )

    diversity = (1.0 - hhi) * 100.0

    return round(
        max(0.0, min(100.0, diversity)),
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
        "confidence": None,
        "signals_used": [
            signal.get("interaction_id")
            for signal in valid_signals
        ],
        "evidence": evidence_list,
        "calculation": calculation,
    }
