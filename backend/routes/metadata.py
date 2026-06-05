from pathlib import Path

import pandas as pd
from fastapi import APIRouter

from backend.schemas.response_models import MetadataListResponse
from config.category_mapping import DISPLAY_CATEGORIES
from config.user_branch_families import DISPLAY_BRANCH_FAMILIES


ROOT_DIR = Path(__file__).resolve().parents[2]
METADATA_PATH = ROOT_DIR / "data" / "college_metadata.csv"

COMMON_LOCATION_ALIASES = [
    "All Maharashtra",
    "Navi Mumbai",
    "Pimpri",
    "PCMC",
]

router = APIRouter(tags=["metadata"])


def clean_values(values):
    cleaned = []
    for value in values:
        text = str(value).strip()
        if text and text.lower() != "nan":
            cleaned.append(text)
    return sorted(set(cleaned))


def infer_locations_from_names(names):
    known_locations = [
        "Ahmednagar",
        "Akola",
        "Amravati",
        "Aurangabad",
        "Baramati",
        "Beed",
        "Bhandara",
        "Buldhana",
        "Chandrapur",
        "Dhule",
        "Gondia",
        "Ichalkaranji",
        "Jalgaon",
        "Jalna",
        "Karad",
        "Kolhapur",
        "Latur",
        "Mumbai",
        "Navi Mumbai",
        "Nagpur",
        "Nanded",
        "Nandurbar",
        "Nashik",
        "Osmanabad",
        "Palghar",
        "Panvel",
        "Parbhani",
        "Pimpri",
        "Pune",
        "Raigad",
        "Ratnagiri",
        "Sambhajinagar",
        "Sangli",
        "Satara",
        "Shegaon",
        "Sindhudurg",
        "Solapur",
        "Thane",
        "Ulhasnagar",
        "Vasai",
        "Virar",
        "Wardha",
        "Washim",
        "Yavatmal",
    ]
    found = set()
    for name in names:
        lower_name = str(name).lower()
        for location in known_locations:
            if location.lower() in lower_name:
                found.add(location)
    return found


@router.get("/categories", response_model=MetadataListResponse)
def get_categories():
    return MetadataListResponse(values=list(DISPLAY_CATEGORIES))


@router.get("/branches", response_model=MetadataListResponse)
def get_branches():
    return MetadataListResponse(values=list(DISPLAY_BRANCH_FAMILIES))


@router.get("/locations", response_model=MetadataListResponse)
def get_locations():
    metadata = pd.read_csv(METADATA_PATH, keep_default_na=False)
    locations = set(clean_values(metadata["city"]))
    locations.update(infer_locations_from_names(metadata["college_name"]))
    locations.update(COMMON_LOCATION_ALIASES)
    return MetadataListResponse(
        values=["All Maharashtra"] + sorted(location for location in locations if location != "All Maharashtra")
    )
