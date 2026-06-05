from pathlib import Path
import sys
import warnings

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "master_cutoffs.csv"
METADATA_PATH = ROOT_DIR / "data" / "college_metadata.csv"
RANKINGS_PATH = ROOT_DIR / "data" / "college_rankings.csv"
RANKING_TEMPLATE_PATH = ROOT_DIR / "data" / "college_ranking_template.csv"
RELIABILITY_PATH = ROOT_DIR / "analysis" / "forecast_reliability.csv"
_DATA_CACHE = None

MIN_VISIBLE_RECOMMENDATIONS = 20

LOCATION_GROUPS = {
    "mumbai": ["Mumbai", "Thane", "Navi Mumbai"],
    "thane": ["Mumbai", "Thane", "Navi Mumbai"],
    "navi mumbai": ["Mumbai", "Thane", "Navi Mumbai"],
    "pune": ["Pune", "Pimpri", "PCMC"],
    "pimpri": ["Pune", "Pimpri", "PCMC"],
    "pcmc": ["Pune", "Pimpri", "PCMC"],
}

LOCATION_ALIASES = {
    "mumbia": "Mumbai",
    "mumbay": "Mumbai",
    "bombay": "Mumbai",
    "punne": "Pune",
    "puna": "Pune",
    "poona": "Pune",
    "nasik": "Nashik",
    "nashilk": "Nashik",
    "nashik road": "Nashik",
    "thanee": "Thane",
    "thana": "Thane",
    "navimumbai": "Navi Mumbai",
    "new mumbai": "Navi Mumbai",
    "aurangabad": "Sambhajinagar",
    "chhatrapati sambhajinagar": "Sambhajinagar",
}

LOCATION_COLLEGE_TERMS = {
    "pune": ["COEP Technological University"],
    "pimpri": ["COEP Technological University"],
    "pcmc": ["COEP Technological University"],
}

TOP_COLLEGE_TERMS = [
    "VJTI",
    "Veermata Jijabai",
    "Sardar Patel Institute of Technology",
    "COEP",
    "Pune Institute of Computer Technology",
    "Walchand",
    "Vishwakarma Institute of Technology",
    "Dwarkadas J. Sanghvi",
    "Thadomal Shahani",
    "Pimpri Chinchwad College of Engineering",
]

sys.path.append(str(ROOT_DIR))

from config.branch_mapping import BRANCH_MAP, get_branches_for_input
from config.category_mapping import CATEGORY_MAP
from config.user_branch_families import (
    DISPLAY_BRANCH_FAMILIES,
    USER_BRANCH_SEARCH_TAGS,
    get_user_family_branches,
)


DISPLAY_COLUMNS = [
    "college_name",
    "branch_name",
    "city",
    "historical_cutoff_2022",
    "historical_cutoff_2023",
    "historical_cutoff_2024",
    "historical_cutoff_2025",
    "average_cutoff",
    "latest_available_cutoff",
    "difference_vs_average",
    "difference_vs_latest",
    "difference",
    "confidence_level",
    "reliability",
    "college_type",
    "autonomous",
    "region",
    "overall_score",
    "data_availability_status",
    "branch_quality_score",
    "admission_probability_score",
    "recommendation_score",
]

CONFIDENCE_ORDER = {
    "VERY SAFE": 1,
    "SAFE": 2,
    "MODERATE": 3,
    "DREAM": 4,
}

RELIABILITY_ORDER = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "UNKNOWN": 4,
}

RELIABILITY_GROUP_COLUMNS = [
    "college_name",
    "branch_name",
    "category",
]


def is_yes(value):
    return str(value).strip().lower() in {"y", "yes", "true", "1"}


def is_safe(diff):
    return 0 <= diff <= 5


def is_moderate(diff):
    return -2 <= diff < 0


def classify_confidence(row):
    difference_vs_latest = row["difference_vs_latest"]
    difference_vs_average = row["difference_vs_average"]

    if difference_vs_latest < -2:
        return "DREAM"
    if difference_vs_latest < 0:
        return "MODERATE"
    if difference_vs_average < -2:
        return "MODERATE"
    if difference_vs_latest >= 3 and difference_vs_average >= 0:
        return "VERY SAFE"
    return "SAFE"


def clean_text_columns(df):
    object_columns = df.select_dtypes(include="object").columns
    df[object_columns] = df[object_columns].fillna("")
    return df


def classify_reliability(volatility, max_yearly_change):
    if volatility < 3 and max_yearly_change < 5:
        return "HIGH"
    if volatility < 8 and max_yearly_change < 15:
        return "MEDIUM"
    return "LOW"


def build_reliability_from_cutoffs(cutoffs):
    yearly_cutoffs = (
        cutoffs
        .groupby(RELIABILITY_GROUP_COLUMNS + ["year"])["percentile"]
        .mean()
        .reset_index()
    )
    available_years = sorted(int(year) for year in yearly_cutoffs["year"].unique())
    reliability = (
        yearly_cutoffs
        .pivot_table(
            index=RELIABILITY_GROUP_COLUMNS,
            columns="year",
            values="percentile",
        )
        .reset_index()
        .rename(columns={year: f"cutoff_{year}" for year in available_years})
    )
    cutoff_columns = [f"cutoff_{year}" for year in available_years]
    reliability = reliability.dropna(subset=cutoff_columns).copy()

    change_columns = []
    for previous_year, current_year in zip(available_years, available_years[1:]):
        column = f"change_{str(previous_year)[-2:]}_{str(current_year)[-2:]}"
        reliability[column] = (
            reliability[f"cutoff_{current_year}"]
            - reliability[f"cutoff_{previous_year}"]
        )
        change_columns.append(column)

    reliability["volatility"] = reliability[cutoff_columns].std(axis=1, ddof=0)
    reliability["max_yearly_change"] = reliability[change_columns].abs().max(axis=1)
    reliability["reliability"] = reliability.apply(
        lambda row: classify_reliability(
            row["volatility"],
            row["max_yearly_change"],
        ),
        axis=1,
    )
    return reliability[RELIABILITY_GROUP_COLUMNS + ["reliability"]]


def load_reliability(cutoffs):
    if not RELIABILITY_PATH.exists():
        return build_reliability_from_cutoffs(cutoffs)

    return pd.read_csv(RELIABILITY_PATH)


def load_data():
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE.copy()

    cutoffs = pd.read_csv(DATA_PATH)
    metadata = clean_text_columns(
        pd.read_csv(METADATA_PATH, keep_default_na=False)
    )
    rankings = pd.read_csv(RANKINGS_PATH, keep_default_na=False)
    reliability = load_reliability(cutoffs)

    rankings["overall_score"] = pd.to_numeric(
        rankings["overall_score"],
        errors="coerce",
    ).fillna(0)

    df = cutoffs.merge(
        metadata,
        on=["college_code", "college_name"],
        how="left",
    )
    df = df.merge(
        rankings[["college_code", "overall_score"]],
        on="college_code",
        how="left",
    )
    if RANKING_TEMPLATE_PATH.exists():
        ranking_template = pd.read_csv(
            RANKING_TEMPLATE_PATH,
            keep_default_na=False,
        )
        ranking_template["template_overall_score"] = pd.to_numeric(
            ranking_template["overall_score"],
            errors="coerce",
        )
        ranking_template = ranking_template[
            ["college_name", "template_overall_score"]
        ].drop_duplicates("college_name")
        df = df.merge(
            ranking_template,
            on="college_name",
            how="left",
        )
        df["overall_score"] = df["template_overall_score"].combine_first(
            df["overall_score"]
        )
        df = df.drop(columns=["template_overall_score"])
    df = df.merge(
        reliability[["college_name", "branch_name", "category", "reliability"]],
        on=["college_name", "branch_name", "category"],
        how="left",
    )

    df["overall_score"] = df["overall_score"].fillna(0)
    df["reliability"] = df["reliability"].fillna("UNKNOWN")
    df = clean_text_columns(df)

    _DATA_CACHE = df
    return df.copy()


def apply_student_filters(
    df,
    student_category,
    branch_input,
    location=None,
    government_only=False,
    autonomous_only=False,
    minority_allowed=True,
    region=None,
):
    categories = resolve_categories(student_category)
    branches = resolve_branches(branch_input)

    filtered = df[
        df["category"].isin(categories)
        & df["branch_name"].isin(branches)
    ].copy()

    filtered = apply_location_filter(filtered, location)

    if government_only:
        filtered = filtered[
            filtered["government_or_private"].str.contains(
                "government",
                case=False,
                na=False,
            )
            | filtered["college_type"].str.contains(
                "government",
                case=False,
                na=False,
            )
        ]

    if autonomous_only:
        filtered = filtered[
            filtered["autonomous"].str.lower().isin(
                ["yes", "y", "true", "autonomous", "1"]
            )
        ]

    if not minority_allowed:
        filtered = filtered[
            filtered["minority_status"].str.strip().isin(["", "No", "NO", "no"])
        ]

    if region and region.strip():
        region_key = region.strip()
        filtered = filtered[
            filtered["region"].str.contains(region_key, case=False, na=False)
        ]

    return filtered


def resolve_categories(student_category):
    categories = CATEGORY_MAP.get(student_category.strip().upper(), [])
    if not categories:
        raise ValueError("Unknown category. Use one of: " + ", ".join(CATEGORY_MAP))
    return categories


def resolve_branches(branch_input):
    branches = get_user_family_branches(branch_input)
    if not branches:
        branches = get_branches_for_input(branch_input)
    if not branches:
        branch_key = branch_input.strip().lower()
        branches = [
            branch
            for branch in USER_BRANCH_SEARCH_TAGS
            if branch.lower() == branch_key
        ]
    if not branches:
        raise ValueError(
            "Unknown branch. Choose a branch from the suggestions or use a branch family."
        )
    return branches


def normalize_location(location):
    if location is None:
        return None
    if isinstance(location, (list, tuple, set)):
        normalized = []
        for value in location:
            clean_value = normalize_location(value)
            if clean_value:
                normalized.append(clean_value)
        return normalized

    location_key = str(location).strip()
    if not location_key:
        return None
    if location_key.lower() == "all maharashtra":
        return None
    return LOCATION_ALIASES.get(location_key.lower(), location_key)


def location_group_for(location):
    location = normalize_location(location)
    if not location or not str(location).strip():
        return []
    return LOCATION_GROUPS.get(str(location).strip().lower(), [])


def apply_location_filter(df, location):
    location = normalize_location(location)
    if not location:
        return df
    if isinstance(location, (list, tuple, set)):
        locations = [str(value).strip() for value in location if str(value).strip()]
        if not locations:
            return df
        mask = pd.Series(False, index=df.index)
        for value in locations:
            mask = (
                mask
                | df["city"].str.contains(value, case=False, regex=False, na=False)
                | df["college_name"].str.contains(value, case=False, regex=False, na=False)
            )
        return df[mask]

    location_key = str(location).strip()
    if not location_key or location_key.lower() == "all maharashtra":
        return df
    mask = (
        df["city"].str.contains(location_key, case=False, regex=False, na=False)
        | df["college_name"].str.contains(location_key, case=False, regex=False, na=False)
    )
    for college_term in LOCATION_COLLEGE_TERMS.get(location_key.lower(), []):
        mask = mask | df["college_name"].str.contains(
            college_term,
            case=False,
            regex=False,
            na=False,
        )
    return df[mask]


def apply_context_filters(
    df,
    branches,
    location=None,
    government_only=False,
    autonomous_only=False,
    minority_allowed=True,
    region=None,
):
    filtered = df[df["branch_name"].isin(branches)].copy()

    filtered = apply_location_filter(filtered, location)

    if government_only:
        filtered = filtered[
            filtered["government_or_private"].str.contains(
                "government",
                case=False,
                na=False,
            )
            | filtered["college_type"].str.contains(
                "government",
                case=False,
                na=False,
            )
        ]

    if autonomous_only:
        filtered = filtered[
            filtered["autonomous"].str.lower().isin(
                ["yes", "y", "true", "autonomous", "1"]
            )
        ]

    if not minority_allowed:
        filtered = filtered[
            filtered["minority_status"].str.strip().isin(["", "No", "NO", "no"])
        ]

    if region and region.strip():
        region_key = region.strip()
        filtered = filtered[
            filtered["region"].str.contains(region_key, case=False, na=False)
        ]

    return filtered


def find_category_data_gaps(
    df,
    student_category,
    branch_input,
    location=None,
    government_only=False,
    autonomous_only=False,
    minority_allowed=True,
    region=None,
):
    categories = resolve_categories(student_category)
    branches = resolve_branches(branch_input)
    base = apply_context_filters(
        df,
        branches,
        location=location,
        government_only=government_only,
        autonomous_only=autonomous_only,
        minority_allowed=minority_allowed,
        region=region,
    )

    if base.empty:
        return pd.DataFrame()

    all_combinations = (
        base
        .groupby(["college_code", "college_name", "branch_name"], dropna=False)
        .agg(
            city=("city", first_non_empty),
            college_type=("college_type", first_non_empty),
            autonomous=("autonomous", first_non_empty),
            region=("region", first_non_empty),
            overall_score=("overall_score", "max"),
        )
        .reset_index()
    )

    available_keys = (
        base[base["category"].isin(categories)]
        [["college_code", "branch_name"]]
        .drop_duplicates()
    )

    missing = all_combinations.merge(
        available_keys.assign(has_selected_category=True),
        on=["college_code", "branch_name"],
        how="left",
    )
    missing = missing[missing["has_selected_category"].isna()].copy()
    if missing.empty:
        return missing

    missing["selected_category"] = student_category.strip().upper()
    missing["data_availability_status"] = "NO_CATEGORY_HISTORY"
    missing["availability_message"] = (
        "No historical "
        + missing["selected_category"]
        + " cutoff data was found for this branch. The branch exists, "
        + "but we cannot estimate admission chances for this category."
    )
    return missing.sort_values(
        by=["overall_score", "college_name", "branch_name"],
        ascending=[False, True, True],
    )


def aggregate_reliability(values):
    ranks = [
        RELIABILITY_ORDER.get(str(value).strip().upper(), RELIABILITY_ORDER["UNKNOWN"])
        for value in values
    ]
    worst_rank = max(ranks) if ranks else RELIABILITY_ORDER["UNKNOWN"]

    for reliability, rank in RELIABILITY_ORDER.items():
        if rank == worst_rank:
            return reliability

    return "UNKNOWN"


def first_non_empty(values):
    for value in values:
        text = str(value).strip()
        if text:
            return text
    return ""


def yearly_cutoff(values, years, target_year):
    year_values = values[years == target_year]
    if year_values.empty:
        return None
    return year_values.mean()


def latest_available_cutoff(row):
    for column in [
        "historical_cutoff_2025",
        "historical_cutoff_2024",
        "historical_cutoff_2023",
        "historical_cutoff_2022",
    ]:
        value = row[column]
        if pd.notna(value) and float(value) > 0:
            return value
    return row["average_cutoff"]


def build_recommendations(filtered, student_percentile):
    lower_band = student_percentile - 2
    current_band = student_percentile

    grouped = (
        filtered
        .groupby(["college_code", "college_name", "branch_name"], dropna=False)
        .agg(
            average_cutoff=("percentile", "mean"),
            historical_cutoff_2022=(
                "percentile",
                lambda values: yearly_cutoff(values, filtered.loc[values.index, "year"], 2022),
            ),
            historical_cutoff_2023=(
                "percentile",
                lambda values: yearly_cutoff(values, filtered.loc[values.index, "year"], 2023),
            ),
            historical_cutoff_2024=(
                "percentile",
                lambda values: yearly_cutoff(values, filtered.loc[values.index, "year"], 2024),
            ),
            historical_cutoff_2025=(
                "percentile",
                lambda values: yearly_cutoff(values, filtered.loc[values.index, "year"], 2025),
            ),
            city=("city", first_non_empty),
            college_type=("college_type", first_non_empty),
            autonomous=("autonomous", first_non_empty),
            region=("region", first_non_empty),
            overall_score=("overall_score", "max"),
            reliability=("reliability", aggregate_reliability),
            record_count=("percentile", "count"),
            year_count=("year", "nunique"),
        )
        .reset_index()
    )

    grouped["data_availability_status"] = grouped.apply(
        lambda row: "LIMITED_DATA"
        if row["year_count"] < 2 or row["record_count"] < 3
        else "AVAILABLE",
        axis=1,
    )
    grouped["difference"] = current_band - grouped["average_cutoff"]
    grouped["latest_available_cutoff"] = grouped.apply(latest_available_cutoff, axis=1)
    grouped["difference_vs_average"] = current_band - grouped["average_cutoff"]
    grouped["difference_vs_latest"] = current_band - grouped["latest_available_cutoff"]

    branch_quality = grouped.groupby("branch_name")["average_cutoff"].mean()
    grouped["branch_quality_score"] = grouped["branch_name"].map(branch_quality)
    grouped["admission_probability_score"] = (
        100 - grouped["difference"].abs().clip(upper=20) * 5
    ).clip(lower=0, upper=100)
    grouped["far_safe_penalty"] = (grouped["difference"] - 15).clip(lower=0) * 2
    grouped["college_quality_score"] = grouped["average_cutoff"]
    grouped["recommendation_score"] = (
        grouped["college_quality_score"] * 0.55
        + grouped["branch_quality_score"] * 0.25
        + grouped["admission_probability_score"] * 0.20
        - grouped["far_safe_penalty"]
    )

    grouped["lower_band_difference"] = lower_band - grouped["average_cutoff"]
    grouped["current_band_difference"] = current_band - grouped["average_cutoff"]
    grouped["safe_at_lower_band"] = grouped["lower_band_difference"].apply(is_safe)
    grouped["safe_at_current_band"] = grouped["current_band_difference"].apply(is_safe)
    grouped["confidence_level"] = grouped.apply(classify_confidence, axis=1)
    grouped["confidence_rank"] = grouped["confidence_level"].map(CONFIDENCE_ORDER)
    grouped["reliability_rank"] = grouped["reliability"].map(RELIABILITY_ORDER)

    return grouped.sort_values(
        by=[
            "recommendation_score",
            "average_cutoff",
            "confidence_rank",
            "overall_score",
        ],
        ascending=[False, False, True, False],
    )


def is_top_college_name(college_name):
    name = str(college_name).lower()
    return any(term.lower() in name for term in TOP_COLLEGE_TERMS)


def select_visible_recommendations(recommendations, limit):
    if recommendations.empty:
        return recommendations

    top = recommendations.head(limit).copy()
    pinned = recommendations[
        recommendations["college_name"].apply(is_top_college_name)
    ].copy()

    if pinned.empty:
        return top

    visible = (
        pd.concat([pinned, top], ignore_index=True)
        .drop_duplicates(["college_code", "branch_name"], keep="first")
        .sort_values(
            by=[
                "location_priority",
                "recommendation_score",
                "average_cutoff",
                "confidence_rank",
                "overall_score",
            ],
            ascending=[False, False, False, True, False],
        )
    )
    return visible.reset_index(drop=True)


def empty_result_message(category, branch_input, location=None):
    location_text = location.strip() if isinstance(location, str) and location.strip() else None
    if location_text:
        return (
            f"No colleges were found for {category.upper()} + {branch_input} in "
            f"{location_text}. We may not have enough historical seat data for "
            "this category and branch in that location. Try nearby cities or "
            "Maharashtra-wide search."
        )
    return (
        f"No colleges were found for {category.upper()} + {branch_input}. "
        "We may not have enough historical seat data for this category and branch."
    )


def recommend(
    student_percentile,
    student_category,
    branch_input,
    location=None,
    government_only=False,
    autonomous_only=False,
    minority_allowed=True,
    region=None,
    limit=20,
    show_all_matches=False,
    df=None,
):
    if df is None:
        df = load_data()
    fallback_message = ""
    original_location = location.strip() if isinstance(location, str) else location
    location = normalize_location(location)
    location_correction_message = ""
    if (
        isinstance(original_location, str)
        and original_location
        and isinstance(location, str)
        and original_location.lower() != location.lower()
    ):
        location_correction_message = (
            f"Showing results for {location}. It looks like "
            f"'{original_location}' was a typo."
        )

    attempts = [
        {
            "location": location,
            "region": region,
            "message": "",
        }
    ]

    location_group = location_group_for(location)
    if location_group:
        attempts.append({
            "location": location_group,
            "region": region,
            "message": (
                f"Showing nearby colleges from the {', '.join(location_group)} region "
                f"because exact {location} results were limited."
            ),
        })

    if location and str(location).strip() and region and region.strip():
        attempts.append({
            "location": None,
            "region": region,
            "message": (
                f"Exact {location} results were limited. Showing nearby matches from "
                f"{region.strip()} region."
            ),
        })

    if (location and str(location).strip()) or (region and region.strip()):
        attempts.append({
            "location": None,
            "region": None,
            "message": (
                "Exact location results were limited. Showing Maharashtra-wide matches "
                "so you still have options to review."
            ),
        })

    recommendations = pd.DataFrame()
    exact_location_recommendations = pd.DataFrame()
    for attempt in attempts:
        filtered = apply_student_filters(
            df,
            student_category,
            branch_input,
            location=attempt["location"],
            government_only=government_only,
            autonomous_only=autonomous_only,
            minority_allowed=minority_allowed,
            region=attempt["region"],
        )
        current_recommendations = build_recommendations(filtered, student_percentile)
        current_recommendations["location_priority"] = 0

        is_exact_location_attempt = (
            isinstance(attempt["location"], str)
            and bool(attempt["location"].strip())
            and bool(location_group_for(attempt["location"]))
        )
        if (
            is_exact_location_attempt
            and not current_recommendations.empty
            and len(current_recommendations) < MIN_VISIBLE_RECOMMENDATIONS
        ):
            exact_location_recommendations = current_recommendations.copy()
            exact_location_recommendations["location_priority"] = 1
            continue

        if not exact_location_recommendations.empty and not current_recommendations.empty:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*",
                    category=FutureWarning,
                )
                combined_recommendations = pd.concat(
                    [exact_location_recommendations, current_recommendations],
                    ignore_index=True,
                )
            recommendations = (
                combined_recommendations
                .drop_duplicates(["college_code", "branch_name"], keep="first")
                .sort_values(
                    by=[
                        "location_priority",
                        "recommendation_score",
                        "average_cutoff",
                        "confidence_rank",
                        "overall_score",
                    ],
                    ascending=[False, False, False, True, False],
                )
                .reset_index(drop=True)
            )
        else:
            recommendations = current_recommendations

        enough_results = len(recommendations) >= MIN_VISIBLE_RECOMMENDATIONS
        is_last_attempt = attempt is attempts[-1]
        if not recommendations.empty and (enough_results or is_last_attempt):
            fallback_message = attempt["message"]
            if location_correction_message:
                fallback_message = (
                    f"{location_correction_message} {fallback_message}".strip()
                )
            break

    if recommendations.empty and not fallback_message:
        fallback_message = empty_result_message(
            student_category,
            branch_input,
            location=location,
        )
        if location_correction_message:
            fallback_message = (
                f"{location_correction_message} {fallback_message}".strip()
            )

    recommendations.attrs["fallback_message"] = fallback_message

    if show_all_matches:
        return recommendations, recommendations

    return select_visible_recommendations(recommendations, limit), recommendations


def print_recommendations(recommendations):
    fallback_message = recommendations.attrs.get("fallback_message", "")
    if fallback_message:
        print(fallback_message)
        print()

    if recommendations.empty:
        print("No recommendations found.")
        return

    print(
        recommendations[DISPLAY_COLUMNS].to_string(
            index=False,
            formatters={
                "average_cutoff": "{:.2f}".format,
                "overall_score": "{:.2f}".format,
            },
        )
    )


def main():
    student_percentile = float(input("Enter Percentile: "))
    student_category = input("Enter Category (OPEN/OBC/SC/ST/EWS/TFWS/VJ): ")
    branch_input = input("Enter Branch Group (CS/IT/AI/AI_DS/AI_ML/ENTC/etc): ")
    location = input("Enter Preferred Location (optional): ")
    government_only = is_yes(input("Government Only? (y/n): "))
    autonomous_only = is_yes(input("Autonomous Only? (y/n): "))
    minority_allowed = is_yes(input("Minority Allowed? (y/n): ") or "y")
    region = input("Enter Region (optional): ")

    top_recommendations, _ = recommend(
        student_percentile,
        student_category,
        branch_input,
        location=location,
        government_only=government_only,
        autonomous_only=autonomous_only,
        minority_allowed=minority_allowed,
        region=region,
    )

    print("\nCOUNSELOR SHORTLIST\n")
    print_recommendations(top_recommendations)


if __name__ == "__main__":
    main()
