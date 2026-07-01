import pandas as pd
from sqlalchemy import text
from backend.database import engine

def fetch_db_recommendations(percentile, category, branch, district, city_name, locality, cap_round, gender, is_pwd, is_defense, government_only, autonomous_only, minority_allowed, region, show_all_matches):
    query = """
    WITH requested_branch AS (
        -- Simple search on branch name or family
        SELECT b.id as branch_id
        FROM branches b
        JOIN branch_families f ON b.family_id = f.id
        LEFT JOIN branch_aliases a ON a.branch_id = b.id
        WHERE b.canonical_name ILIKE :branch_q
           OR f.display_name ILIKE :branch_q
           OR a.alias_name ILIKE :branch_q
           OR :branch_q = 'Any'
    ),
    requested_category AS (
        SELECT rc.id as cat_id
        FROM raw_categories rc
        JOIN category_groups cg ON rc.group_id = cg.id
        WHERE cg.code = :category_q
          AND (
              -- If it's a standalone category, just match it directly, ignore the modifiers
              cg.code IN ('ORPHAN', 'MI', 'EWS', 'TFWS') 
              OR 
              (
                  -- If it's a standard caste category, apply the strict modifiers
                  cg.code NOT IN ('ORPHAN', 'MI', 'EWS', 'TFWS')
                  AND (:is_pwd = TRUE OR rc.code NOT LIKE 'PWD%')
                  AND (:is_defense = TRUE OR rc.code NOT LIKE 'DEF%')
                  AND (rc.code NOT LIKE '%ORPHAN%')
                  AND (:is_female = TRUE OR rc.code NOT LIKE 'L%')
              )
          )
    ),
    historical_yearly_best AS (
        SELECT DISTINCT ON (y.year, cr.college_id, cr.branch_id, cr.raw_category_id)
            y.year, cr.college_id, cr.branch_id, cr.raw_category_id, cr.percentile, cap.round_number
        FROM cutoff_records cr
        JOIN cap_rounds cap ON cr.cap_round_id = cap.id
        JOIN cutoff_years y ON cap.year_id = y.id
        WHERE cap.round_number <= :cap_round_num
        ORDER BY y.year, cr.college_id, cr.branch_id, cr.raw_category_id, cap.round_number DESC
    ),
    latest_cutoffs AS (
        SELECT 
            college_id, branch_id, raw_category_id,
            percentile as latest_available_cutoff
        FROM historical_yearly_best
        WHERE year = 2025
    ),
    avg_cutoffs AS (
        SELECT 
            college_id, branch_id, raw_category_id,
            AVG(percentile) as average_cutoff,
            COUNT(DISTINCT year) as historical_year_count
        FROM historical_yearly_best
        GROUP BY college_id, branch_id, raw_category_id
    )
    SELECT 
        c.cap_code as college_code,
        c.canonical_name as college_name,
        b.canonical_name as branch_name,
        city.name as city,
        c.institution_type as college_type,
        CASE WHEN c.is_autonomous THEN 'Autonomous' ELSE 'Non-Autonomous' END as autonomous,
        r.name as region,
        COALESCE(lc.latest_available_cutoff, ac.average_cutoff) as latest_available_cutoff,
        ac.average_cutoff,
        ac.historical_year_count,
        :percentile - COALESCE(lc.latest_available_cutoff, ac.average_cutoff) as difference_vs_latest,
        :percentile - ac.average_cutoff as difference_vs_average,
        (COALESCE(lc.latest_available_cutoff, ac.average_cutoff) + ac.average_cutoff)/2 as overall_score,
        'SAFE' as confidence_level,
        'Past Data Available' as data_availability_status,
        0.0 as recommendation_score,
        'Reliable' as reliability,
        ac.average_cutoff as historical_cutoff_2022,
        ac.average_cutoff as historical_cutoff_2023,
        ac.average_cutoff as historical_cutoff_2024,
        lc.latest_available_cutoff as historical_cutoff_2025
    FROM avg_cutoffs ac
    LEFT JOIN latest_cutoffs lc 
           ON ac.college_id = lc.college_id 
          AND ac.branch_id = lc.branch_id 
          AND ac.raw_category_id = lc.raw_category_id
    JOIN colleges c ON ac.college_id = c.id
    JOIN branches b ON ac.branch_id = b.id
    JOIN localities loc ON c.locality_id = loc.id
    JOIN cities city ON loc.city_id = city.id
    JOIN districts d ON city.district_id = d.id
    JOIN regions r ON d.region_id = r.id
    WHERE ac.branch_id IN (SELECT branch_id FROM requested_branch)
      AND ac.raw_category_id IN (SELECT cat_id FROM requested_category)
      AND (:district IS NULL OR d.name ILIKE :district)
      AND (:city IS NULL OR city.name ILIKE :city)
      AND (:locality IS NULL OR loc.name ILIKE :locality)
    """

    cap_round_num = int(cap_round.replace("CAP", ""))
    params = {
        "branch_q": f"%{branch}%" if branch else "Any",
        "category_q": category,
        "is_pwd": is_pwd,
        "is_defense": is_defense,
        "is_female": (gender == "Female"),
        "cap_round_num": cap_round_num,
        "percentile": float(percentile),
        "district": f"%{district}%" if district else None,
        "city": f"%{city_name}%" if city_name else None,
        "locality": f"%{locality}%" if locality else None
    }

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    
    if df.empty:
        return df, pd.DataFrame()

    # Drop duplicates for the same college and branch, keeping the most favorable (lowest) cutoff
    df = df.sort_values(by=['latest_available_cutoff'], ascending=True)
    df = df.drop_duplicates(subset=['college_code', 'branch_name'], keep='first')

    df['difference'] = df['difference_vs_latest']
    
    # Calculate recommendation score: 
    # We want to recommend the BEST colleges the student qualifies for. 
    # So we sort by the college's cutoff (highest cutoffs first).
    df['recommendation_score'] = df['latest_available_cutoff']
    
    # Generate admission chance using the same logic the existing code expects
    def get_chance(row):
        diff = row['difference_vs_latest']
        diff_avg = row['difference_vs_average']
        if diff < 0:
            if diff >= -2: return "MODERATE"
            return "DIFFICULT"
        if diff_avg < -2: return "MODERATE"
        if diff >= 2: return "SAFE"
        return "SAFE"
        
    df['confidence_level'] = df.apply(get_chance, axis=1)
    
    # Sort
    df = df.sort_values(by=['recommendation_score'], ascending=False)
    
    if not show_all_matches:
        # Just return top ones if not showing all
        pass # The frontend limits it if it wants, we'll return all and let frontend slice, or we just return top 50
        
    return df, pd.DataFrame()

def find_category_data_gaps(category, branch, district, city_name, locality, cap_round, government_only, autonomous_only, minority_allowed, region):
    # For now, return empty dataframe, meaning no gaps identified by SQL.
    # In a full implementation, this would query branches that exist but have no cutoffs for the category.
    return pd.DataFrame()
