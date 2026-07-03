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
        res = conn.execute(text("SELECT cap_code, canonical_name FROM colleges WHERE canonical_name ILIKE :q OR CAST(cap_code AS TEXT) ILIKE :q LIMIT 10"), {"q": f"%{q}%"})
        results = [{"college_code": row[0], "college_name": row[1]} for row in res]
    return {"results": results}

@router.get("/college-branches")
def search_college_branches(college: str, q: str = ""):
    with engine.connect() as conn:
        res = conn.execute(text("""
        WITH latest_year AS (
            SELECT MAX(year) as max_year FROM cutoff_years
        )
        SELECT b.canonical_name as branch_name, array_agg(DISTINCT f.display_name) as families
        FROM branches b
        JOIN cutoff_records cr ON b.id = cr.branch_id
        JOIN cap_rounds cap ON cr.cap_round_id = cap.id
        JOIN cutoff_years y ON cap.year_id = y.id
        CROSS JOIN latest_year ly
        JOIN colleges c ON cr.college_id = c.id
        LEFT JOIN branch_families f ON b.family_id = f.id
        WHERE c.canonical_name = :college
          AND b.canonical_name ILIKE :q
          AND y.year = ly.max_year
        GROUP BY b.canonical_name
        ORDER BY b.canonical_name
        LIMIT 20
    """), {"college": college, "q": f"%{q}%"})
        results = [{"branch_name": row[0]} for row in res]
    return {"results": results}

@router.post("/target-percentile", response_model=TargetPercentileResponse)
def target_percentile(request: TargetPercentileRequest):
    import pandas as pd
    from config.university_mapping import get_home_university
    
    user_university = get_home_university(request.home_district)

    # EWS is strictly for OPEN category candidates
    is_ews = request.is_ews
    if request.category != "OPEN":
        is_ews = False

    query = """
    WITH requested_category AS (
        SELECT rc.id as cat_id, rc.code as raw_category_code
        FROM raw_categories rc
        JOIN category_groups cg ON rc.group_id = cg.id
        WHERE 
            (
                cg.code IN (:category_q, 'OPEN')
                AND cg.code NOT IN ('ORPHAN', 'MI', 'EWS', 'TFWS')
                AND (:is_pwd = TRUE OR rc.code NOT LIKE 'PWD%')
                AND (:is_defense = TRUE OR rc.code NOT LIKE 'DEF%')
                AND (rc.code NOT LIKE '%ORPHAN%')
                AND (:is_female = TRUE OR rc.code NOT LIKE 'L%')
            )
            OR (:is_tfws = TRUE AND cg.code = 'TFWS')
            OR (:is_ews = TRUE AND cg.code = 'EWS')
            OR (:has_minority = TRUE AND cg.code = 'MI')
    )
    SELECT cr.percentile, y.year, cap.round_number, d.name as college_district, rc_cte.raw_category_code
    FROM cutoff_records cr
    JOIN colleges c ON cr.college_id = c.id
    JOIN branches b ON cr.branch_id = b.id
    JOIN requested_category rc_cte ON cr.raw_category_id = rc_cte.cat_id
    JOIN cap_rounds cap ON cr.cap_round_id = cap.id
    JOIN cutoff_years y ON cap.year_id = y.id
    JOIN localities loc ON c.locality_id = loc.id
    JOIN cities city ON loc.city_id = city.id
    JOIN districts d ON city.district_id = d.id
    WHERE c.canonical_name = :college 
      AND b.canonical_name = :branch
      AND (rc_cte.raw_category_code NOT LIKE '%MI%' OR c.minority_type = :user_minority_type)
    """

    params = {
        "college": request.college,
        "branch": request.branch,
        "category_q": request.category,
        "is_pwd": request.is_pwd,
        "is_defense": request.is_defense,
        "is_female": (request.gender == "Female"),
        "is_tfws": request.is_tfws,
        "is_ews": is_ews,
        "has_minority": request.minority_type != "Not Applicable",
        "user_minority_type": request.minority_type
    }

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
        
    def empty_response(msg):
        return TargetPercentileResponse(
            college_name=request.college,
            branch_name=request.branch,
            category=request.category,
            safety_margin=request.safety_margin,
            suggested_target_percentile=0.0,
            error_message=msg
        )

    if df.empty:
        return empty_response("No historical cutoffs found for this combination in the database.")

    df['college_university'] = df['college_district'].apply(get_home_university)
    
    def is_home_seat(row):
        code = row['raw_category_code']
        if code.endswith('O'):
            return False
        return True

    def is_other_seat(row):
        code = row['raw_category_code']
        if code.endswith('H'):
            return False
        return True

    if user_university is not None:
        def is_valid_seat(row):
            code = row['raw_category_code']
            if code.endswith('S') or code in ('TFWS', 'EWS', 'MI', 'ORPHAN') or 'AI' in code:
                return True
            if code.endswith('H'):
                return user_university == row['college_university']
            if code.endswith('O'):
                return user_university != row['college_university']
            return True
            
        df = df[df.apply(is_valid_seat, axis=1)]
        if df.empty:
            return empty_response("No eligible seats available for your specific profile.")
            
        # Women's College Check for Male Candidates
        df['seat_category'] = df['raw_category_code'].apply(lambda x: x if x in ['TFWS', 'EWS', 'MI'] else 'Standard')
        if request.gender == "Male":
            if 'Standard' not in df['seat_category'].values:
                return empty_response("This appears to be a Women's College. Male candidates are not eligible.")
                
        yearly_cutoffs = df.groupby('year')['percentile'].min()
    else:
        df_home = df[df.apply(is_home_seat, axis=1)]
        df_other = df[df.apply(is_other_seat, axis=1)]
        
        # Women's College Check for Male Candidates
        df['seat_category'] = df['raw_category_code'].apply(lambda x: x if x in ['TFWS', 'EWS', 'MI'] else 'Standard')
        if request.gender == "Male":
            if 'Standard' not in df['seat_category'].values:
                return empty_response("This appears to be a Women's College. Male candidates are not eligible.")
        
        home_cutoffs = df_home.groupby('year')['percentile'].min()
        other_cutoffs = df_other.groupby('year')['percentile'].min()
        
        # Take the max of the min cutoffs to be safe but preserve category
        yearly_cutoffs = pd.concat([home_cutoffs, other_cutoffs], axis=1).max(axis=1)
        
    latest_year = yearly_cutoffs.index.max()
    
    # Verify the branch wasn't closed
    max_year_query = "SELECT MAX(year) FROM cutoff_years"
    branch_max_year_query = """
    SELECT MAX(y.year)
    FROM cutoff_records cr
    JOIN colleges c ON cr.college_id = c.id
    JOIN branches b ON cr.branch_id = b.id
    JOIN cap_rounds cap ON cr.cap_round_id = cap.id
    JOIN cutoff_years y ON cap.year_id = y.id
    WHERE c.canonical_name = :college AND b.canonical_name = :branch
    """
    with engine.connect() as conn:
        global_max_year = conn.execute(text(max_year_query)).scalar()
        branch_max_year = conn.execute(text(branch_max_year_query), {"college": request.college, "branch": request.branch}).scalar()
        
    if branch_max_year is None or branch_max_year < global_max_year:
        return empty_response("This branch appears to be closed in the latest admission cycle.")
        
    latest_cutoff = float(yearly_cutoffs[latest_year])
    avg_cutoff = float(yearly_cutoffs.mean())
    target = min(100.0, max(latest_cutoff, avg_cutoff) + request.safety_margin)
    
    return TargetPercentileResponse(
        college_name=request.college,
        branch_name=request.branch,
        category=request.category,
        safety_margin=request.safety_margin,
        suggested_target_percentile=round(target, 2),
        cutoff_2022=round(float(yearly_cutoffs.get(2022)), 2) if 2022 in yearly_cutoffs else None,
        cutoff_2023=round(float(yearly_cutoffs.get(2023)), 2) if 2023 in yearly_cutoffs else None,
        cutoff_2024=round(float(yearly_cutoffs.get(2024)), 2) if 2024 in yearly_cutoffs else None,
        cutoff_2025=round(float(yearly_cutoffs.get(2025)), 2) if 2025 in yearly_cutoffs else None
    )

@router.get("/branch-search")
def search_branches(q: str):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT canonical_name FROM branches WHERE canonical_name ILIKE :q LIMIT 10"), {"q": f"%{q}%"})
        results = [{"branch_name": row[0]} for row in res]
    return {"results": results}
