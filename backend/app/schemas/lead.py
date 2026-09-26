from typing import Optional, Dict
from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    sector: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    sector: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
