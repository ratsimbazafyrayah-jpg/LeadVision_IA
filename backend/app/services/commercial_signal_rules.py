from typing import Dict, Any


def classify_interaction(
    interaction: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Classifie une interaction selon des règles commerciales explicites.

    Principe:
    - aucune donnée commerciale n'est inventée ;
    - aucun score commercial n'est calculé ici ;
    - un signal doit disposer d'une preuve identifiable ;
    - les interactions de test sont ignorées.
    """

    interaction_type = interaction.get("type")
    source = interaction.get("source")
    metadata = interaction.get("metadata") or {}

    # ---------------------------------------------------------
    # 1. Données de test
    # ---------------------------------------------------------
    if metadata.get("origin") == "manual_test":
        return {
            "is_signal": False,
            "classification": "test_data",
            "reason": "manual_test",
        }

    # ---------------------------------------------------------
    # 2. Données minimales obligatoires
    # ---------------------------------------------------------
    if not interaction_type or not source:
        return {
            "is_signal": False,
            "classification": "insufficient_data",
            "reason": "missing_type_or_source",
        }

    # ---------------------------------------------------------
    # 3. Formulaire soumis
    # Evidence: form_id ou event_id
    # ---------------------------------------------------------
    if interaction_type == "form_submission":
        if metadata.get("form_id") or metadata.get("event_id"):
            return {
                "is_signal": True,
                "classification": "form_submission",
                "reason": "validated_form_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_form_id_or_event_id",
        }

    # ---------------------------------------------------------
    # 4. Réponse email
    # Evidence: message_id ou thread_id
    # ---------------------------------------------------------
    if interaction_type == "email_reply":
        if metadata.get("message_id") or metadata.get("thread_id"):
            return {
                "is_signal": True,
                "classification": "email_reply",
                "reason": "validated_email_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_message_id_or_thread_id",
        }

    # ---------------------------------------------------------
    # 5. Rendez-vous réservé
    # Evidence: meeting_id ou event_id
    # ---------------------------------------------------------
    if interaction_type == "meeting_booked":
        if metadata.get("meeting_id") or metadata.get("event_id"):
            return {
                "is_signal": True,
                "classification": "meeting_booked",
                "reason": "validated_meeting_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_meeting_id_or_event_id",
        }

    # ---------------------------------------------------------
    # 6. Demande de démonstration
    # Evidence: request_id ou event_id
    # ---------------------------------------------------------
    if interaction_type == "demo_request":
        if metadata.get("request_id") or metadata.get("event_id"):
            return {
                "is_signal": True,
                "classification": "demo_request",
                "reason": "validated_demo_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_request_id_or_event_id",
        }

    # ---------------------------------------------------------
    # 7. Demande de devis
    # Evidence: request_id ou event_id
    # ---------------------------------------------------------
    if interaction_type == "quote_request":
        if metadata.get("request_id") or metadata.get("event_id"):
            return {
                "is_signal": True,
                "classification": "quote_request",
                "reason": "validated_quote_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_request_id_or_event_id",
        }

    # ---------------------------------------------------------
    # 8. Demande de contact
    # Evidence: request_id ou event_id
    # ---------------------------------------------------------
    if interaction_type == "contact_request":
        if metadata.get("request_id") or metadata.get("event_id"):
            return {
                "is_signal": True,
                "classification": "contact_request",
                "reason": "validated_contact_event",
            }

        return {
            "is_signal": False,
            "classification": "insufficient_evidence",
            "reason": "missing_request_id_or_event_id",
        }

    # ---------------------------------------------------------
    # 9. Interaction sans règle commerciale validée
    # ---------------------------------------------------------
    return {
        "is_signal": False,
        "classification": "unclassified",
        "reason": "no_validated_commercial_rule",
    }
