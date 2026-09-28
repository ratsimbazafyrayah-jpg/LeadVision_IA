from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DiscoverySearchRequest(BaseModel):
    country: str = Field(..., min_length=2, max_length=100)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    region: Optional[str] = Field(None, min_length=2, max_length=100)
    sector: Optional[str] = Field(None, min_length=2, max_length=150)
    source: str = Field(..., min_length=2, max_length=100)
    query: str = Field(..., min_length=2, max_length=200)

    @field_validator("country", "source", "query")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("La valeur ne peut pas être vide.")

        return value

    @field_validator("city", "region", "sector")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("La valeur ne peut pas être vide.")

        return value


class DiscoveryImportRequest(BaseModel):
    source: str = Field(..., min_length=2, max_length=100)
    prospects: list[dict] = Field(..., min_length=1)

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("La source ne peut pas être vide.")

        return value
