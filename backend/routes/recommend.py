from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.schemas.request_models import RecommendationRequest
from backend.schemas.response_models import (
    DataAvailabilityItem,
    RecommendationItem,
    RecommendationResponse,
)
from recommender.recommend_v7 import (
    fetch_db_recommendations,
    find_category_data_gaps,
)

DISPLAY_COLUMNS = ["college_code", "college_name", "branch_name", "city"]


router = APIRouter(tags=["recommendations"])


BUCKET_MAP = {
    "VERY SAFE": "very_safe",
    "SAFE": "safe",
    "MODERATE": "moderate",
    "DREAM": "dream",
}

ADMISSION_CHANCE_BUCKET_MAP = {
    "HIGH CHANCE": "safe",
    "POSSIBLE": "moderate",
    "DIFFICULT": "dream",
}


def clean_text(value):
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def clean_number(value):
    if pd.isna(value):
        return None
    return round(float(value), 2)


def count_historical_years(row):
    return sum(
        clean_number(row[column]) is not None
        for column in [
            "historical_cutoff_2022",
            "historical_cutoff_2023",
            "historical_cutoff_2024",
            "historical_cutoff_2025",
        ]
    )


def build_reason(row, percentile, chance, cap_round):
    cap_text = f"CAP Round {cap_round.replace('CAP', '')}"
    latest_cutoff = float(row["latest_available_cutoff"])
    average_cutoff = float(row["average_cutoff"])
    difference_vs_latest = float(percentile) - latest_cutoff
    difference_vs_average = float(percentile) - average_cutoff

    if chance == "HIGH CHANCE":
        return (
            f"Your percentile is {difference_vs_latest:.2f} points above "
            f"the latest available cutoff. Based on {cap_text} cutoff trends from "
            "2022-2025."
        )

    if chance == "DIFFICULT":
        return (
            f"This branch is currently ambitious based on {cap_text} cutoff trends "
            "from 2022-2025."
        )

    if difference_vs_latest < 0 and difference_vs_average >= 0:
        return (
            "Your percentile is slightly below the latest available cutoff "
            f"but remains above the historical average. Based on {cap_text} cutoff "
            "trends from 2022-2025."
        )

    if chance == "POSSIBLE":
        if difference_vs_latest >= 0 and difference_vs_average < 0:
            return (
                "Your percentile is above the latest available cutoff, but "
                "the historical average is higher. Admission is possible, "
                f"not guaranteed. Based on {cap_text} cutoff trends from 2022-2025."
            )
        return (
            f"You are close to {cap_text} cutoffs from 2022-2025. Admission depends "
            "on this year's competition."
        )

    return (
        f"This branch is currently ambitious based on {cap_text} cutoff trends from "
        "2022-2025."
    )


def admission_chance(row, percentile):
    difference_vs_latest = float(percentile) - float(row["latest_available_cutoff"])
    difference_vs_average = float(percentile) - float(row["average_cutoff"])
    if difference_vs_latest < 0:
        if difference_vs_latest >= -2:
            return "POSSIBLE"
        return "DIFFICULT"

    if difference_vs_average < -2:
        return "POSSIBLE"

    confidence = clean_text(row["confidence_level"])
    confidence = clean_text(confidence)
    if confidence in {"VERY SAFE", "SAFE"}:
        return "HIGH CHANCE"
    if confidence == "MODERATE":
        return "POSSIBLE"
    return "DIFFICULT"


def availability_label(status):
    status = clean_text(status)
    if status == "NO_CATEGORY_HISTORY":
        return "No Past Data Available"
    if status == "LIMITED_DATA":
        return "Limited Past Data"
    return "Past Data Available"


def row_to_item(row, percentile, cap_round):
    cutoff_2022 = clean_number(row["historical_cutoff_2022"])
    cutoff_2023 = clean_number(row["historical_cutoff_2023"])
    cutoff_2024 = clean_number(row["historical_cutoff_2024"])
    cutoff_2025 = clean_number(row["historical_cutoff_2025"])
    chance = admission_chance(row, percentile)
    return RecommendationItem(
        college_code=int(row["college_code"]),
        college_name=clean_text(row["college_name"]),
        branch_name=clean_text(row["branch_name"]),
        city=clean_text(row["city"]),
        historical_cutoff_2022=cutoff_2022,
        historical_cutoff_2023=cutoff_2023,
        historical_cutoff_2024=cutoff_2024,
        historical_cutoff_2025=cutoff_2025,
        cutoff_2022=cutoff_2022,
        cutoff_2023=cutoff_2023,
        cutoff_2024=cutoff_2024,
        cutoff_2025=cutoff_2025,
        average_cutoff=round(float(row["average_cutoff"]), 2),
        latest_available_cutoff=round(float(row["latest_available_cutoff"]), 2),
        student_percentile=round(float(percentile), 2),
        difference=round(float(row["difference"]), 2),
        difference_vs_average=round(float(row["difference_vs_average"]), 2),
        difference_vs_latest=round(float(row["difference_vs_latest"]), 2),
        confidence_level=chance,
        admission_chance=chance,
        reliability_level=clean_text(row["reliability"]),
        college_type=clean_text(row["college_type"]),
        autonomous=clean_text(row["autonomous"]),
        region=clean_text(row["region"]),
        overall_score=round(float(row["overall_score"]), 2),
        data_availability_status=availability_label(row["data_availability_status"]),
        historical_year_count=count_historical_years(row),
        recommendation_score=round(float(row["recommendation_score"]), 4),
        recommendation_reason=build_reason(row, percentile, chance, cap_round),
    )


def row_to_unavailable_item(row):
    return DataAvailabilityItem(
        college_code=int(row["college_code"]),
        college_name=clean_text(row["college_name"]),
        branch_name=clean_text(row["branch_name"]),
        city=clean_text(row["city"]),
        selected_category=clean_text(row["selected_category"]),
        data_availability_status=availability_label(row["data_availability_status"]),
        message=clean_text(row["availability_message"]),
    )


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    try:
        top_recommendations, _ = fetch_db_recommendations(
            request.percentile,
            request.category,
            request.branch,
            request.district,
            request.city,
            request.locality,
            request.cap_round,
            request.gender,
            request.is_pwd,
            request.is_defense,
            request.government_only,
            request.autonomous_only,
            request.minority_allowed,
            request.region,
            request.show_all_matches
        )
        data_gaps = find_category_data_gaps(
            request.category,
            request.branch,
            district=request.district,
            city_name=request.city,
            locality=request.locality,
            cap_round=request.cap_round,
            government_only=request.government_only,
            autonomous_only=request.autonomous_only,
            minority_allowed=request.minority_allowed,
            region=request.region,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    missing_columns = []
    if not top_recommendations.empty:
        missing_columns = [
            column for column in DISPLAY_COLUMNS
            if column not in top_recommendations.columns
        ]
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation output missing columns: {missing_columns}",
        )

    response = {
        "message": top_recommendations.attrs.get("fallback_message") or None,
        "selected_cap_round": request.cap_round,
        "very_safe": [],
        "safe": [],
        "moderate": [],
        "dream": [],
        "unavailable": [],
    }

    for _, row in top_recommendations.iterrows():
        item = row_to_item(row, request.percentile, request.cap_round)
        bucket = ADMISSION_CHANCE_BUCKET_MAP.get(item.admission_chance)
        if bucket:
            response[bucket].append(item)

    unavailable_limit = None if request.show_all_matches else 20
    if not data_gaps.empty:
        gaps = data_gaps if unavailable_limit is None else data_gaps.head(unavailable_limit)
        response["unavailable"] = [
            row_to_unavailable_item(row)
            for _, row in gaps.iterrows()
        ]

    total_rows = sum(
        len(response[key])
        for key in ["very_safe", "safe", "moderate", "dream", "unavailable"]
    )
    if total_rows == 0 and not response["message"]:
        response["message"] = (
            "No colleges were found for this exact combination. We do not "
            "have enough historical seat data for this category and branch. "
            "Try nearby cities or Maharashtra-wide search."
        )

    return response
