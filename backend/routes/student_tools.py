from pathlib import Path
import re

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.schemas.request_models import TargetPercentileRequest
from backend.schemas.response_models import (
    BranchInfoItem,
    BranchInfoResponse,
    BranchSearchItem,
    BranchSearchResponse,
    TargetPercentileResponse,
)
from config.category_mapping import CATEGORY_MAP
from config.user_branch_families import USER_BRANCH_SEARCH_TAGS


ROOT_DIR = Path(__file__).resolve().parents[2]
MASTER_PATH = ROOT_DIR / "data" / "master_cutoffs.csv"
BRANCH_DESCRIPTIONS_PATH = ROOT_DIR / "data" / "branch_descriptions.csv"

router = APIRouter(tags=["student-tools"])

INTEREST_KEYWORDS = {
    "coding": ["computer", "software", "information technology", "data", "cyber", "artificial intelligence"],
    "math": ["artificial intelligence", "data science", "computer", "electronics", "electrical"],
    "electronics": ["electronics", "telecommunication", "electrical", "instrumentation", "5g", "vlsi"],
    "business": ["business systems", "logistics", "production", "management"],
    "robotics": ["robotics", "automation", "iot", "mechatronics"],
    "design": ["design", "civil", "mechanical", "architectural", "fashion"],
}

SEARCH_ALIASES = {
    "ai": ["artificial intelligence", "machine learning", "data science", "robotics"],
    "aids": ["artificial intelligence and data science", "ai and data science", "data science"],
    "aiml": ["artificial intelligence and machine learning", "ai and ml", "machine learning"],
    "cs": ["computer", "computer science", "computer engineering", "software"],
    "cse": ["computer science and engineering", "computer engineering"],
    "it": ["information technology", "computer"],
}


def load_master():
    return pd.read_csv(MASTER_PATH)


def families_for_branch(branch_name):
    return sorted(USER_BRANCH_SEARCH_TAGS.get(branch_name, []))


def category_values(category):
    category_key = category.strip().upper()
    return CATEGORY_MAP.get(category_key, [category_key])


def match_text(series, value):
    value = value.strip().lower()
    exact = series.astype(str).str.lower().eq(value)
    if exact.any():
        return exact
    return series.astype(str).str.lower().str.contains(value, regex=False, na=False)


def make_acronym(text):
    words = re.findall(r"[A-Za-z]+", str(text))
    skip_words = {"of", "and", "the", "for", "in"}
    return "".join(word[0] for word in words if word.lower() not in skip_words).lower()


def normalize_search_text(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def college_search_mask(series, value):
    query = value.strip().lower()
    normalized_query = normalize_search_text(query)
    text = series.astype(str)
    lower = text.str.lower()
    acronym = text.map(make_acronym)
    normalized = text.map(normalize_search_text)

    mask = lower.str.contains(query, regex=False, na=False)
    mask = mask | acronym.str.contains(normalized_query, regex=False, na=False)
    mask = mask | normalized.str.contains(normalized_query, regex=False, na=False)
    return mask


def match_college(series, value):
    text_match = match_text(series, value)
    if text_match.any():
        return text_match
    query = value.strip().lower()
    normalized_query = normalize_search_text(query)
    acronym = series.astype(str).map(make_acronym)
    normalized = series.astype(str).map(normalize_search_text)
    return acronym.eq(normalized_query) | normalized.str.contains(normalized_query, regex=False, na=False)


def branch_search_terms(query):
    compact = query.replace(" ", "").replace("&", "")
    alias_terms = SEARCH_ALIASES.get(query, []) + SEARCH_ALIASES.get(compact, [])
    terms = alias_terms if alias_terms and len(query) <= 4 else [query, *alias_terms]
    return [term for term in dict.fromkeys(terms) if term]


@router.get("/branch-search", response_model=BranchSearchResponse)
def branch_search(q: str = Query("", min_length=0)):
    query = q.strip().lower()
    branches = sorted(load_master()["branch_name"].dropna().astype(str).unique())

    if query:
        terms = branch_search_terms(query)
        branches = [
            branch
            for branch in branches
            if any(term in branch.lower() for term in terms)
            or any(term in family.lower() for family in families_for_branch(branch) for term in terms)
        ]

    return BranchSearchResponse(
        query=q,
        results=[
            BranchSearchItem(
                branch_name=branch,
                families=families_for_branch(branch),
            )
            for branch in branches[:30]
        ],
    )


@router.get("/college-search")
def college_search(q: str = Query("", min_length=0)):
    query = q.strip()
    df = load_master()
    colleges = (
        df[["college_code", "college_name"]]
        .drop_duplicates()
        .sort_values("college_name")
    )

    if query:
        colleges = colleges[college_search_mask(colleges["college_name"], query)]

    return {
        "query": q,
        "results": colleges.head(20).to_dict("records"),
    }


@router.get("/college-branches")
def college_branches(
    college: str = Query("", min_length=0),
    q: str = Query("", min_length=0),
):
    df = load_master()
    if college.strip():
        df = df[match_college(df["college_name"], college)].copy()
    if df.empty:
        return {"college": college, "results": []}

    branches = sorted(df["branch_name"].dropna().astype(str).unique())
    query = q.strip().lower()
    if query:
        branches = [
            branch
            for branch in branches
            if query in branch.lower()
        ]

    return {
        "college": college,
        "results": [{"branch_name": branch} for branch in branches[:30]],
    }


@router.post("/target-percentile", response_model=TargetPercentileResponse)
def target_percentile(request: TargetPercentileRequest):
    df = load_master()
    categories = category_values(request.category)
    filtered = df[
        df["category"].isin(categories)
        & match_college(df["college_name"], request.college)
        & match_text(df["branch_name"], request.branch)
    ].copy()

    if filtered.empty:
        raise HTTPException(
            status_code=404,
            detail="No cutoff data found for the selected college, branch, and category.",
        )

    college_name = str(filtered["college_name"].mode().iloc[0])
    branch_name = str(filtered["branch_name"].mode().iloc[0])
    yearly = filtered.groupby("year")["percentile"].mean()

    cutoffs = {
        2022: yearly.get(2022),
        2023: yearly.get(2023),
        2024: yearly.get(2024),
        2025: yearly.get(2025),
    }
    available_cutoffs = [value for value in cutoffs.values() if pd.notna(value)]
    target = min(100, max(available_cutoffs) + request.safety_margin)

    return TargetPercentileResponse(
        college_name=college_name,
        branch_name=branch_name,
        category=request.category.strip().upper(),
        cutoff_2022=None if pd.isna(cutoffs[2022]) else round(float(cutoffs[2022]), 2),
        cutoff_2023=None if pd.isna(cutoffs[2023]) else round(float(cutoffs[2023]), 2),
        cutoff_2024=None if pd.isna(cutoffs[2024]) else round(float(cutoffs[2024]), 2),
        cutoff_2025=None if pd.isna(cutoffs[2025]) else round(float(cutoffs[2025]), 2),
        safety_margin=round(float(request.safety_margin), 2),
        suggested_target_percentile=round(float(target), 2),
    )


@router.get("/branch-info", response_model=BranchInfoResponse)
def branch_info(
    q: str = "",
    interest: str = "",
):
    df = pd.read_csv(BRANCH_DESCRIPTIONS_PATH, keep_default_na=False)
    query = q.strip().lower()
    interest_key = interest.strip().lower()

    if query:
        text = (
            df["branch_name"]
            + " "
            + df["description"]
            + " "
            + df["subjects"]
            + " "
            + df["skills_required"]
            + " "
            + df["career_paths"]
        ).str.lower()
        df = df[text.str.contains(query, regex=False, na=False)]

    if interest_key:
        keywords = INTEREST_KEYWORDS.get(interest_key, [interest_key])
        text = (
            df["branch_name"]
            + " "
            + df["description"]
            + " "
            + df["subjects"]
            + " "
            + df["skills_required"]
            + " "
            + df["career_paths"]
        ).str.lower()
        mask = pd.Series(False, index=df.index)
        for keyword in keywords:
            mask = mask | text.str.contains(keyword, regex=False, na=False)
        df = df[mask]

    items = []
    for _, row in df.sort_values("branch_name").head(50).iterrows():
        items.append(
            BranchInfoItem(
                branch_name=row["branch_name"],
                description=row["description"],
                subjects=row["subjects"],
                skills_required=row["skills_required"],
                career_paths=row["career_paths"],
                families=families_for_branch(row["branch_name"]),
            )
        )

    return BranchInfoResponse(results=items)
