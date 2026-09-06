"""
Structured output models for Kisan Dost.

Every tool returns one of these Pydantic models instead of a loose string.
This is what the hackathon brief calls "structured outputs" and it is
what lets the agent (and any future UI) rely on typed fields instead of
parsing free text.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class FarmerProfile(BaseModel):
    """Carried as typed context across a whole session so the farmer
    never has to repeat their district / land size / current crop."""
    name: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    land_size_acres: Optional[float] = None
    current_crop: Optional[str] = None


class CropOption(BaseModel):
    crop: str
    expected_yield_maund_per_acre: float
    expected_profit_pkr_per_acre: int
    water_requirement: str  # "low" | "medium" | "high"
    notes: str


class CropRecommendation(BaseModel):
    district: str
    season: str
    recommended_crops: List[CropOption]
    summary: str


class PestDiagnosis(BaseModel):
    likely_pest_or_disease: str
    confidence: str  # "low" | "medium" | "high"
    treatment: str
    safe_dosage: str
    reapply_after_days: Optional[int] = None
    warning: Optional[str] = None


class FertilizerPlan(BaseModel):
    crop: str
    acres: float
    urea_bags: float
    dap_bags: float
    total_cost_pkr: int
    note: str


class MandiPrice(BaseModel):
    crop: str
    market: str
    price_pkr_per_maund: int
    trend: str  # "rising" | "falling" | "stable"
    advice: str


class IrrigationAdvice(BaseModel):
    district: str
    crop_stage: str
    forecast_summary: str
    irrigation_recommendation: str
    frost_or_heat_warning: Optional[str] = None


class ProfitEstimate(BaseModel):
    crop: str
    acres: float
    total_cost_pkr: int
    expected_revenue_pkr: int
    net_margin_pkr: int
    break_even_yield_maund_per_acre: float


class GovtSupportInfo(BaseModel):
    province: str
    relevant_schemes: List[str]
    how_to_apply: str
