from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT_DIR / "data" / "branch_career_profiles.csv"
EXPLORER_PATH = ROOT_DIR / "data" / "branch_explorer.csv"


ANSWER_TO_PROFILE = {
    "coding": "coding_weight",
    "math": "math_weight",
    "physics": "math_weight",
    "electronics": "electronics_weight",
    "mechanical": "mechanical_weight",
    "civil": "design_weight",
    "chemistry": "chemistry_weight",
    "data": "coding_weight",
    "salary": "salary_potential",
    "government": "government_job_friendly",
    "startup": "startup_friendly",
    "abstract": "math_weight",
    "design": "design_weight",
    "communication": "communication_weight",
    "future": "future_growth_score",
}

ANSWER_REASON = {
    "coding": "strong coding interest",
    "math": "good mathematics comfort",
    "physics": "interest in physics and problem solving",
    "electronics": "interest in electronics",
    "mechanical": "interest in machines and automobiles",
    "civil": "interest in infrastructure and design",
    "chemistry": "interest in chemistry",
    "data": "interest in analyzing data",
    "salary": "high salary preference",
    "government": "government job preference",
    "startup": "startup interest",
    "abstract": "abstract problem-solving interest",
    "design": "product design interest",
    "communication": "comfort working with people",
    "future": "future-focused career preference",
}


def clamp_answer(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    return max(1, min(5, number))


def load_profiles():
    profiles = pd.read_csv(PROFILE_PATH)
    explorer = pd.read_csv(EXPLORER_PATH, keep_default_na=False)
    return profiles.merge(explorer, on="branch_name", how="left")


def branch_match_score(profile, answers):
    weighted_score = 0
    max_score = 0

    for answer_key, profile_key in ANSWER_TO_PROFILE.items():
        answer = clamp_answer(answers.get(answer_key, 0))
        if answer <= 0:
            continue
        profile_value = float(profile.get(profile_key, 0))
        weighted_score += answer * profile_value
        max_score += 5 * 10

    if max_score == 0:
        return 0

    score = (weighted_score / max_score) * 100
    branch = str(profile.get("branch_name", "")).lower()

    if clamp_answer(answers.get("coding", 0)) >= 4 and any(
        term in branch
        for term in ["computer", "information technology", "software", "cyber", "data science"]
    ):
        score += 18
    if clamp_answer(answers.get("data", 0)) >= 4 and any(
        term in branch for term in ["data", "artificial intelligence", "machine learning"]
    ):
        score += 12
    if clamp_answer(answers.get("mechanical", 0)) >= 4 and any(
        term in branch
        for term in ["mechanical", "automobile", "automotive", "production", "manufacturing"]
    ):
        score += 20
    if clamp_answer(answers.get("government", 0)) >= 4 and any(
        term in branch for term in ["civil", "structural", "electrical"]
    ):
        score += 22
    if clamp_answer(answers.get("electronics", 0)) >= 4 and any(
        term in branch
        for term in ["electronics", "telecommunication", "communication", "vlsi", "5g", "instrumentation"]
    ):
        score += 22

    return round(max(0, min(100, score)), 2)


def build_reasons(profile, answers):
    scored_reasons = []
    for answer_key, profile_key in ANSWER_TO_PROFILE.items():
        answer = clamp_answer(answers.get(answer_key, 0))
        profile_value = float(profile.get(profile_key, 0))
        if answer >= 4 and profile_value >= 7:
            scored_reasons.append((answer * profile_value, ANSWER_REASON[answer_key]))

    scored_reasons.sort(reverse=True)
    reasons = [reason for _, reason in scored_reasons[:3]]
    if reasons:
        return reasons
    return ["balanced fit based on your interests"]


def match_branches(answers, limit=10):
    profiles = load_profiles()
    rows = []

    for _, profile in profiles.iterrows():
        score = branch_match_score(profile, answers)
        rows.append({
            "branch_name": profile["branch_name"],
            "match_score": score,
            "reasons": build_reasons(profile, answers),
            "what_you_study": profile.get("what_you_study", ""),
            "who_should_choose": profile.get("who_should_choose", ""),
            "career_paths": profile.get("career_paths", ""),
            "average_salary_range": profile.get("average_salary_range", ""),
            "future_scope": profile.get("future_scope", ""),
            "difficulty_level": int(profile.get("difficulty_level", 0)),
            "salary_potential": int(profile.get("salary_potential", 0)),
            "future_growth_score": int(profile.get("future_growth_score", 0)),
        })

    return sorted(
        rows,
        key=lambda row: (
            row["match_score"],
            row["future_growth_score"],
            row["salary_potential"],
            row["branch_name"],
        ),
        reverse=True,
    )[:limit]
