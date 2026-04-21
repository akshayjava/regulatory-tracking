"""
Pydantic models for LATTICE API request/response schemas.
"""
from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class VerticalInfo(BaseModel):
    vertical: str
    relevance_score: int
    is_critical: bool


class RegulationBase(BaseModel):
    title: str
    summary: Optional[str] = None
    type: str
    status: str
    source: str
    published_date: Optional[date] = None
    effective_date: Optional[date] = None
    deadline_date: Optional[date] = None
    complexity_score: Optional[int] = Field(None, ge=1, le=10)
    impact_score: Optional[int] = Field(None, ge=1, le=10)
    citation: Optional[str] = None


class RegulationCreate(RegulationBase):
    regulation_id: str
    affected_entities: List[str] = []
    keywords: List[str] = []
    agency_id: Optional[int] = None


class RegulationResponse(RegulationBase):
    id: int
    regulation_id: str
    affected_entities: List[str] = []
    keywords: List[str] = []
    verticals: List[VerticalInfo] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RegulationListResponse(BaseModel):
    items: List[RegulationResponse]
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
    verticals: List[str]
    impact_score: Optional[int] = None


class SourceStatus(BaseModel):
    name: str
    abbreviation: str
    last_sync: Optional[datetime] = None
    status: str
    regulation_count: int


class DashboardStats(BaseModel):
    total_regulations: int
    by_status: Dict[str, int]
    by_vertical: Dict[str, int]
    by_agency: Dict[str, int]
    deadlines_30_days: int
    deadlines_90_days: int
    sources: List[SourceStatus]
