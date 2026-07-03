from pathlib import Path

import pandas as pd
from fastapi import APIRouter

from backend.schemas.response_models import MetadataListResponse
from config.category_mapping import DISPLAY_CATEGORIES
from config.user_branch_families import DISPLAY_BRANCH_FAMILIES, USER_BRANCH_FAMILIES


from backend.database import engine
from sqlalchemy import text

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


@router.get("/grouped-branches")
def get_grouped_branches():
    return USER_BRANCH_FAMILIES


from config.university_mapping import DISTRICT_TO_UNIVERSITY

@router.get("/home-districts", response_model=MetadataListResponse)
def get_home_districts():
    districts = sorted(list(DISTRICT_TO_UNIVERSITY.keys()))
    return MetadataListResponse(values=districts)


@router.get("/districts", response_model=MetadataListResponse)
def get_districts():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT DISTINCT name FROM districts ORDER BY name"))
        districts = [row[0] for row in res]
    return MetadataListResponse(values=districts)


@router.get("/cities", response_model=MetadataListResponse)
def get_cities(district: str = None):
    query = "SELECT DISTINCT name FROM cities"
    params = {}
    if district:
        query += " WHERE district_id IN (SELECT id FROM districts WHERE name = :district)"
        params["district"] = district
    query += " ORDER BY name"
    
    with engine.connect() as conn:
        res = conn.execute(text(query), params)
        cities = [row[0] for row in res]
    return MetadataListResponse(values=cities)


@router.get("/localities", response_model=MetadataListResponse)
def get_localities(city: str = None):
    query = "SELECT DISTINCT name FROM localities"
    params = {}
    if city:
        query += " WHERE city_id IN (SELECT id FROM cities WHERE name = :city)"
        params["city"] = city
    query += " ORDER BY name"
    
    with engine.connect() as conn:
        res = conn.execute(text(query), params)
        localities = [row[0] for row in res]
    return MetadataListResponse(values=localities)
