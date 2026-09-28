from typing import Iterable, Any


class DiscoverySourceRegistry:
    def __init__(self, sources: Iterable[Any]):
        self._sources = {}

        for source in sources:
            name = source.name

            if name in self._sources:
                raise ValueError(
                    "Source de découverte dupliquée."
                )

            self._sources[name] = source

    def get(self, name: str) -> Any:
        if name not in self._sources:
            raise ValueError(
                f"Source de découverte inconnue : {name}"
            )

        return self._sources[name]

    def close(self) -> None:
        for source in self._sources.values():
            close = getattr(source, "close", None)

            if callable(close):
                close()
