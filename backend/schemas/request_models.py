from typing import Dict, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    percentile: float = Field(..., ge=0, le=100)
    category: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1)
    district: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    cap_round: str = Field(..., pattern="^CAP[1-4]$")
    gender: str = Field("Male", pattern="^(Male|Female)$")
    is_pwd: bool = False
    is_defense: bool = False
    government_only: bool = False
    autonomous_only: bool = False
    minority_allowed: bool = True
    region: Optional[str] = None
    show_all_matches: bool = False


class ForecastRequest(BaseModel):
    college: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)


class TargetPercentileRequest(BaseModel):
    college: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    safety_margin: float = Field(2.0, ge=0, le=10)


class CareerQuizRequest(BaseModel):
    answers: Dict[str, int]

