from fastapi import APIRouter
from backend.database import engine
from sqlalchemy import text
from backend.schemas.request_models import TargetPercentileRequest
from backend.schemas.response_models import (
    BranchSearchResponse,
    TargetPercentileResponse,
)

router = APIRouter(tags=["student-tools"])

@router.get("/college-search")
def search_colleges(q: str):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT cap_code, canonical_name FROM colleges WHERE canonical_name ILIKE :q LIMIT 10"), {"q": f"%{q}%"})
        results = [{"college_code": row[0], "college_name": row[1]} for row in res]
    return {"results": results}

@router.get("/college-branches")
def search_college_branches(college: str, q: str = ""):
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT DISTINCT b.canonical_name 
            FROM branches b
            JOIN cutoff_records cr ON b.id = cr.branch_id
            JOIN colleges c ON cr.college_id = c.id
            WHERE c.canonical_name = :college AND b.canonical_name ILIKE :q
            LIMIT 10
        """), {"college": college, "q": f"%{q}%"})
        results = [{"branch_name": row[0]} for row in res]
    return {"results": results}

@router.post("/target-percentile", response_model=TargetPercentileResponse)
def target_percentile(request: TargetPercentileRequest):
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT cr.percentile, y.year, cap.round_number
            FROM cutoff_records cr
            JOIN colleges c ON cr.college_id = c.id
            JOIN branches b ON cr.branch_id = b.id
            JOIN raw_categories rc ON cr.raw_category_id = rc.id
            JOIN category_groups cg ON rc.group_id = cg.id
            JOIN cap_rounds cap ON cr.cap_round_id = cap.id
            JOIN cutoff_years y ON cap.year_id = y.id
            WHERE c.canonical_name = :college 
              AND b.canonical_name = :branch
              AND cg.code = :category
            ORDER BY y.year DESC, cap.round_number ASC
        """), {
            "college": request.college,
            "branch": request.branch,
            "category": request.category
        })
        records = [row for row in res]
        
    if not records:
        return TargetPercentileResponse(
            college_name=request.college,
            branch_name=request.branch,
            selected_category=request.category,
            safety_margin=request.safety_margin,
            target_percentile=0.0,
            latest_cutoff=0.0,
            historical_average=0.0,
            message="No historical cutoffs found for this combination in the database."
        )
        
    latest_cutoff = float(records[0][0])
    avg_cutoff = sum(float(r[0]) for r in records) / len(records)
    target = max(latest_cutoff, avg_cutoff) + request.safety_margin
    
    return TargetPercentileResponse(
        college_name=request.college,
        branch_name=request.branch,
        selected_category=request.category,
        safety_margin=request.safety_margin,
        target_percentile=round(target, 2),
        latest_cutoff=round(latest_cutoff, 2),
        historical_average=round(avg_cutoff, 2),
        message=f"Aim for {round(target, 2)} percentile to be safe."
    )

@router.get("/branch-search")
def search_branches(q: str):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT canonical_name FROM branches WHERE canonical_name ILIKE :q LIMIT 10"), {"q": f"%{q}%"})
        results = [{"branch_name": row[0]} for row in res]
    return {"results": results}
