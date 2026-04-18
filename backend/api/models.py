"""
Pydantic models for LATTICE API request/response schemas.
"""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class VerticalInfo(BaseModel):
    vertical: str
    relevance_score: int
    is_critical: bool


class RegulationBase(BaseModel):
    title: str
    summary: str | None = None
    type: str
    status: str
    source: str
    published_date: date | None = None
    effective_date: date | None = None
    deadline_date: date | None = None
    complexity_score: int | None = Field(None, ge=1, le=10)
    impact_score: int | None = Field(None, ge=1, le=10)
    citation: str | None = None


class RegulationCreate(RegulationBase):
    regulation_id: str
    affected_entities: list[str] = []
    keywords: list[str] = []
    agency_id: int | None = None


class RegulationResponse(RegulationBase):
    id: int
    regulation_id: str
    affected_entities: list[str] = []
    keywords: list[str] = []
    verticals: list[VerticalInfo] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class RegulationListResponse(BaseModel):
    items: list[RegulationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class VerticalStats(BaseModel):
    vertical: str
    count: int
    critical_count: int


class DeadlineAlert(BaseModel):
    regulation_id: str
    title: str
    deadline_date: date
    days_until: int
    urgency: str
    verticals: list[str]
    impact_score: int | None = None


class SourceStatus(BaseModel):
    name: str
    abbreviation: str
    last_sync: datetime | None = None
    status: str
    regulation_count: int


class DashboardStats(BaseModel):
    total_regulations: int
    by_status: dict[str, int]
    by_vertical: dict[str, int]
    by_agency: dict[str, int]
    deadlines_30_days: int
    deadlines_90_days: int
    sources: list[SourceStatus]
