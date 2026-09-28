from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable


class DiscoverySource(ABC):
    """
    Contrat commun pour toutes les sources de découverte.

    Une source doit uniquement collecter des données disponibles
    depuis sa source réelle. Elle ne doit pas inventer de données.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def discover(self, query: str) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError
