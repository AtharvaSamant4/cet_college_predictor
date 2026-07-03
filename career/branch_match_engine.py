import os
import pandas as pd
from pathlib import Path
from backend.schemas.response_models import CareerMatchItem

ROOT_DIR = Path(__file__).resolve().parents[1]

# Load data once
profiles_df = pd.read_csv(ROOT_DIR / "data" / "branch_career_profiles.csv")
explorer_df = pd.read_csv(ROOT_DIR / "data" / "branch_explorer.csv")
merged_df = pd.merge(profiles_df, explorer_df, on="branch_name", how="left")

# Map question IDs to CSV column names
WEIGHT_MAP = {
    "coding": "coding_weight",
    "math": "math_weight",
    "electronics": "electronics_weight",
    "mechanical": "mechanical_weight",
    "chemistry": "chemistry_weight",
    "design": "design_weight",
    "communication": "communication_weight",
    "salary": "salary_potential",
    "government": "government_job_friendly",
    "startup": "startup_friendly",
    "future": "future_growth_score",
    "physics": "math_weight", # proxy
    "civil": "mechanical_weight", # proxy
    "data": "coding_weight", # proxy
    "abstract": "math_weight", # proxy
}

def match_branches(answers: dict, limit: int = 10):
    results = []
    
    # Calculate score for each branch
    for _, row in merged_df.iterrows():
        total_distance = 0
        max_distance = 0
        reasons = []
        
        for q_id, user_val in answers.items():
            if q_id in WEIGHT_MAP:
                col = WEIGHT_MAP[q_id]
                branch_val = row.get(col, 0)
                if pd.isna(branch_val):
                    branch_val = 0
                
                # Normalize answer to 0-10 scale
                norm_user = (user_val - 1) * (10 / 4) # 1->0, 5->10
                
                # Calculate distance between student preference and branch reality
                distance = abs(norm_user - branch_val)
                total_distance += distance
                max_distance += 10 # Maximum possible distance for any trait is 10
                
                # Generate a reason if strong match
                if user_val >= 4 and branch_val >= 7:
                    if q_id == "coding": reasons.append("Strong match for your coding interest")
                    elif q_id == "salary": reasons.append("Matches your high salary expectations")
                    elif q_id == "government": reasons.append("Excellent for government jobs")
                    elif q_id == "startup": reasons.append("Great for startup ambitions")
        
        # Convert total_distance to a percentage match (lower distance = higher match)
        final_score = 100 - (total_distance / max_distance * 100) if max_distance > 0 else 0
        
        if len(reasons) == 0:
            reasons.append("Balanced match for your overall profile")
            
        results.append(CareerMatchItem(
            branch_name=str(row.get("branch_name", "Unknown")),
            match_score=round(final_score, 1),
            reasons=reasons[:2],
            what_you_study=str(row.get("what_you_study", "Not available")),
            who_should_choose=str(row.get("who_should_choose", "Not available")),
            career_paths=str(row.get("career_paths", "Not available")),
            average_salary_range=str(row.get("average_salary_range", "Not available")),
            future_scope=str(row.get("future_scope", "Not available")),
            difficulty_level=int(row.get("difficulty_level", 5) if pd.notna(row.get("difficulty_level")) else 5),
            salary_potential=int(row.get("salary_potential", 5) if pd.notna(row.get("salary_potential")) else 5),
            future_growth_score=int(row.get("future_growth_score", 5) if pd.notna(row.get("future_growth_score")) else 5),
        ))
        
    # Sort by match_score descending
    results.sort(key=lambda x: x.match_score, reverse=True)
    return results[:limit]
