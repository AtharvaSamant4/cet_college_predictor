from typing import List, Optional

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    college_code: int
    college_name: str
    branch_name: str
    city: str
    historical_cutoff_2022: Optional[float] = None
    historical_cutoff_2023: Optional[float] = None
    historical_cutoff_2024: Optional[float] = None
    historical_cutoff_2025: Optional[float] = None
    cutoff_2022: Optional[float] = None
    cutoff_2023: Optional[float] = None
    cutoff_2024: Optional[float] = None
    cutoff_2025: Optional[float] = None
    average_cutoff: float
    latest_available_cutoff: float
    student_percentile: float
    difference: float
    difference_vs_average: float
    difference_vs_latest: float
    confidence_level: str
    admission_chance: str
    reliability_level: str
    college_type: str
    autonomous: str
    region: str
    overall_score: float
    data_availability_status: str
    historical_year_count: int
    recommendation_score: float
    recommendation_reason: str


class DataAvailabilityItem(BaseModel):
    college_code: int
    college_name: str
    branch_name: str
    city: str
    selected_category: str
    data_availability_status: str
    message: str


class RecommendationResponse(BaseModel):
    message: Optional[str] = None
    selected_cap_round: Optional[str] = None
    very_safe: List[RecommendationItem]
    safe: List[RecommendationItem]
    moderate: List[RecommendationItem]
    dream: List[RecommendationItem]
    unavailable: List[DataAvailabilityItem]


class ForecastResponse(BaseModel):
    college_name: str
    branch_name: str
    category: str
    projected_cutoff: float
    reliability: str


class MetadataListResponse(BaseModel):
    values: List[str]


class BranchSearchItem(BaseModel):
    branch_name: str
    families: List[str]


class BranchSearchResponse(BaseModel):
    query: str
    results: List[BranchSearchItem]


class TargetPercentileResponse(BaseModel):
    college_name: str
    branch_name: str
    category: str
    cutoff_2022: Optional[float] = None
    cutoff_2023: Optional[float] = None
    cutoff_2024: Optional[float] = None
    cutoff_2025: Optional[float] = None
    safety_margin: float
    suggested_target_percentile: float


class BranchInfoItem(BaseModel):
    branch_name: str
    description: str
    subjects: str
    skills_required: str
    career_paths: str
    families: List[str]


class BranchInfoResponse(BaseModel):
    results: List[BranchInfoItem]


class CareerMatchItem(BaseModel):
    branch_name: str
    match_score: float
    reasons: List[str]
    what_you_study: str
    who_should_choose: str
    career_paths: str
    average_salary_range: str
    future_scope: str
    difficulty_level: int
    salary_potential: int
    future_growth_score: int


class CareerQuizResponse(BaseModel):
    results: List[CareerMatchItem]
