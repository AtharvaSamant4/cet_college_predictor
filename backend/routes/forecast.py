from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.schemas.request_models import ForecastRequest
from backend.schemas.response_models import ForecastResponse
from config.category_mapping import CATEGORY_MAP
from recommender.recommend_v6 import RELIABILITY_ORDER


ROOT_DIR = Path(__file__).resolve().parents[2]
TREND_PATH = ROOT_DIR / "analysis" / "trend_analysis.csv"
RELIABILITY_PATH = ROOT_DIR / "analysis" / "forecast_reliability.csv"

router = APIRouter(tags=["forecast"])


def ensure_analysis_files():
    if not TREND_PATH.exists():
        from analysis.trend_analysis import build_trend_analysis

        build_trend_analysis()
    if not RELIABILITY_PATH.exists():
        from analysis.forecast_reliability import build_forecast_reliability

        build_forecast_reliability()


def category_values(category):
    category_key = category.strip().upper()
    return CATEGORY_MAP.get(category_key, [category_key])


def conservative_reliability(values):
    labels = [
        str(value).strip().upper()
        for value in values
        if str(value).strip()
    ]
    if not labels:
        return "UNKNOWN"

    worst_rank = max(
        RELIABILITY_ORDER.get(label, RELIABILITY_ORDER["UNKNOWN"])
        for label in labels
    )
    for label, rank in RELIABILITY_ORDER.items():
        if rank == worst_rank:
            return label

    return "UNKNOWN"


def filter_rows(df, request):
    categories = category_values(request.category)
    college_key = request.college.strip().lower()
    branch_key = request.branch.strip().lower()

    return df[
        df["category"].isin(categories)
        & df["college_name"].astype(str).str.lower().eq(college_key)
        & df["branch_name"].astype(str).str.lower().eq(branch_key)
    ].copy()


@router.post("/forecast", response_model=ForecastResponse)
def get_forecast(request: ForecastRequest):
    ensure_analysis_files()

    trend = pd.read_csv(TREND_PATH)
    reliability = pd.read_csv(RELIABILITY_PATH)

    trend_matches = filter_rows(trend, request)
    if trend_matches.empty:
        raise HTTPException(
            status_code=404,
            detail="No forecast found for the given college, branch, and category.",
        )

    reliability_matches = filter_rows(reliability, request)
    best_match = trend_matches.sort_values(
        "projected_2025",
        ascending=False,
    ).iloc[0]

    if reliability_matches.empty:
        reliability_label = "UNKNOWN"
    else:
        reliability_label = conservative_reliability(
            reliability_matches["reliability"]
        )

    return ForecastResponse(
        college_name=str(best_match["college_name"]),
        branch_name=str(best_match["branch_name"]),
        category=request.category.strip().upper(),
        projected_cutoff=round(float(best_match["projected_2025"]), 2),
        reliability=reliability_label,
    )
