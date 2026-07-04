import pandas as pd
from sqlalchemy import text
from functools import lru_cache
from backend.database import engine
from config.university_mapping import get_home_university

@lru_cache(maxsize=1024)
def fetch_db_recommendations(percentile, category, branch, district, city_name, locality, cap_round, gender, is_pwd, is_defense, government_only, autonomous_only, home_district, is_tfws, is_ews, minority_type, region, show_all_matches):
    user_university = get_home_university(home_district)
    
    # EWS is strictly for OPEN category candidates
    if category != "OPEN":
        is_ews = False
    
    query = """
    WITH requested_branch AS (
        SELECT b.id as branch_id
        FROM branches b
        JOIN branch_families f ON b.family_id = f.id
        LEFT JOIN branch_aliases a ON a.branch_id = b.id
        WHERE b.canonical_name ILIKE :branch_q
           OR f.display_name ILIKE :branch_q
           OR a.alias_name ILIKE :branch_q
           OR :branch = 'Any'
    ),
    requested_category AS (
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
    ),
    latest_year AS (
        SELECT MAX(year) as max_year FROM cutoff_years
    ),
    active_branches AS (
        SELECT DISTINCT cr.college_id, cr.branch_id
        FROM cutoff_records cr
        JOIN cap_rounds cap ON cr.cap_round_id = cap.id
        JOIN cutoff_years y ON cap.year_id = y.id
        CROSS JOIN latest_year ly
        WHERE y.year = ly.max_year
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
        CROSS JOIN latest_year ly
        WHERE year = ly.max_year
    ),
    avg_cutoffs AS (
        SELECT 
            college_id, branch_id, raw_category_id,
            AVG(percentile) as average_cutoff,
            COUNT(DISTINCT year) as historical_year_count,
            MAX(percentile) - MIN(percentile) as cutoff_range,
            MAX(CASE WHEN year = 2022 THEN percentile END) as cutoff_2022,
            MAX(CASE WHEN year = 2023 THEN percentile END) as cutoff_2023,
            MAX(CASE WHEN year = 2024 THEN percentile END) as cutoff_2024
        FROM historical_yearly_best
        GROUP BY college_id, branch_id, raw_category_id
    )
    SELECT 
        c.cap_code as college_code,
        c.canonical_name as college_name,
        b.canonical_name as branch_name,
        city.name as city,
        d.name as college_district,
        c.institution_type as college_type,
        CASE WHEN c.is_autonomous THEN 'Autonomous' ELSE 'Non-Autonomous' END as autonomous,
        r.name as region,
        rc_cte.raw_category_code,
        COALESCE(lc.latest_available_cutoff, ac.average_cutoff) as latest_available_cutoff,
        ac.average_cutoff,
        ac.historical_year_count,
        :percentile - COALESCE(lc.latest_available_cutoff, ac.average_cutoff) as difference_vs_latest,
        :percentile - ac.average_cutoff as difference_vs_average,
        (COALESCE(lc.latest_available_cutoff, ac.average_cutoff) + ac.average_cutoff)/2 as overall_score,
        'SAFE' as confidence_level,
        'Past Data Available' as data_availability_status,
        0.0 as recommendation_score,
        CASE 
            WHEN ac.historical_year_count < 2 THEN 'UNKNOWN'
            WHEN ac.cutoff_range <= 3.0 THEN 'HIGH'
            WHEN ac.cutoff_range <= 7.0 THEN 'MEDIUM'
            ELSE 'LOW' 
        END as reliability,
        ac.cutoff_2022 as historical_cutoff_2022,
        ac.cutoff_2023 as historical_cutoff_2023,
        ac.cutoff_2024 as historical_cutoff_2024,
        lc.latest_available_cutoff as historical_cutoff_2025
    FROM avg_cutoffs ac
    JOIN active_branches ab ON ac.college_id = ab.college_id AND ac.branch_id = ab.branch_id
    JOIN requested_category rc_cte ON ac.raw_category_id = rc_cte.cat_id
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
      AND (:district IS NULL OR d.name ILIKE :district)
      AND (:city IS NULL OR city.name ILIKE :city)
      AND (:locality IS NULL OR loc.name ILIKE :locality)
      AND (rc_cte.raw_category_code NOT LIKE '%MI%' OR c.minority_type = :user_minority_type)
    """

    if autonomous_only:
        query += " AND c.is_autonomous = TRUE"
    
    if government_only:
        query += " AND c.institution_type IN ('Government', 'Government-Aided', 'University Dept')"
        
    if region:
        query += " AND r.name ILIKE :region"
    cap_round_num = int(cap_round.replace("CAP", ""))
    params = {
        "branch": branch if branch else "Any",
        "branch_q": f"%{branch}%" if branch else "Any",
        "category_q": category,
        "is_pwd": is_pwd,
        "is_defense": is_defense,
        "is_female": (gender == "Female"),
        "is_tfws": is_tfws,
        "is_ews": is_ews,
        "has_minority": minority_type != "Not Applicable",
        "user_minority_type": minority_type,
        "cap_round_num": cap_round_num,
        "percentile": float(percentile),
        "district": f"%{district}%" if district else None,
        "city": f"%{city_name}%" if city_name else None,
        "locality": f"%{locality}%" if locality else None,
        "region": f"%{region}%" if region else None
    }

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    
    if df.empty:
        return df, pd.DataFrame()

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
        return df, pd.DataFrame()

    df['original_branch_name'] = df['branch_name']
    df['seat_category'] = df['raw_category_code'].apply(lambda x: x if x in ['TFWS', 'EWS', 'MI'] else 'Standard')
    df.loc[df['seat_category'] != 'Standard', 'branch_name'] = df['branch_name'] + " (" + df['seat_category'] + ")"

    seat_priority = {'TFWS': 1, 'EWS': 2, 'MI': 3, 'Standard': 4}
    
    def calc_dedup_score(row):
        diff = row['difference_vs_latest']
        priority = seat_priority.get(row['seat_category'], 4)
        cutoff = row['latest_available_cutoff']
        
        # Consider a seat mathematically reachable if difference is >= -2.0 
        # (meaning it will fall into Possible, High Chance, or Very High Chance)
        is_reachable = diff >= -2.0
        
        if is_reachable:
            # Prioritize special quotas (TFWS/EWS) if they are realistically reachable!
            return (priority * 1000) + cutoff
        else:
            # If it's a pipe dream, prioritize the easiest possible path (lowest cutoff)
            return 10000 + cutoff

    df['dedup_score'] = df.apply(calc_dedup_score, axis=1)

    if gender == "Male":
        # Mathematical inference: A Male candidate's DataFrame will only lack a 'Standard' seat 
        # if all its standard seats were prefixed with 'L' (Ladies seats) and thus filtered out by SQL. 
        # This means the college is a Women's College. We must drop their Special Quota seats (TFWS/EWS) too!
        valid_combos = df[df['seat_category'] == 'Standard'][['college_code', 'original_branch_name']].drop_duplicates()
        df = df.merge(valid_combos, on=['college_code', 'original_branch_name'], how='inner')

    if user_university is not None:
        df = df.sort_values(by=['dedup_score'], ascending=True)
        df = df.drop_duplicates(subset=['college_code', 'original_branch_name'], keep='first')
    else:
        # Separate into home and other possible seats
        df_home = df[df.apply(is_home_seat, axis=1)]
        df_other = df[df.apply(is_other_seat, axis=1)]
        
        df_home = df_home.sort_values(by=['dedup_score'], ascending=True)
        df_home = df_home.drop_duplicates(subset=['college_code', 'original_branch_name'], keep='first')
        
        df_other = df_other.sort_values(by=['dedup_score'], ascending=True)
        df_other = df_other.drop_duplicates(subset=['college_code', 'original_branch_name'], keep='first')
        
        df = pd.concat([df_home, df_other])
        df = df.sort_values(by=['dedup_score'], ascending=True)
        df = df.drop_duplicates(subset=['college_code', 'original_branch_name'], keep='first')

    df['difference_vs_average'] = df['difference_vs_average'].fillna(0)
    df['difference_vs_latest'] = df['difference_vs_latest'].fillna(0)
    df['average_cutoff'] = df['average_cutoff'].fillna(df['latest_available_cutoff'])
    df['overall_score'] = df['overall_score'].fillna(df['latest_available_cutoff'])
    df['historical_year_count'] = df['historical_year_count'].fillna(1)
    df['difference'] = df['difference_vs_latest']
    df['recommendation_score'] = df['latest_available_cutoff']
    
    def get_chance(row):
        diff = row['difference_vs_latest']
        diff_avg = row['difference_vs_average']
        latest = row['latest_available_cutoff']
        avg = row['average_cutoff']
        
        # Anomaly Detection: If the latest year spiked more than 5 percentiles above the historical average
        is_spike = (latest - avg) >= 5
        
        if diff < 0:
            # You missed the latest year's cutoff
            if is_spike and diff_avg >= 0:
                # Latest year was a massive spike, but you beat the historical average!
                # Don't dump this into Difficult. It's realistically possible.
                if diff >= -5:
                    return "HIGH CHANCE"
                return "POSSIBLE"
                
            # Normal logic
            if diff >= -2: return "POSSIBLE"
            return "DIFFICULT"
            
        # diff >= 0 (You beat the latest cutoff)
        if diff_avg < -2: 
            # You beat latest, but latest crashed significantly below the historical average.
            # We are cautious.
            return "POSSIBLE"
        
        if diff >= 2:
            if diff_avg >= 0:
                return "VERY HIGH CHANCE"
            else:
                return "HIGH CHANCE"
                
        return "HIGH CHANCE"
        
    df['confidence_level'] = df.apply(get_chance, axis=1)
    df = df.sort_values(by=['recommendation_score'], ascending=False)
    
    return df, pd.DataFrame()

def find_category_data_gaps(category, branch, district, city_name, locality, cap_round, government_only, autonomous_only, minority_allowed, region, gender="Male", is_pwd=False, is_defense=False, is_tfws=False, is_ews=False, minority_type="Not Applicable", home_district=None):
    user_university = get_home_university(home_district)
    
    # EWS is strictly for OPEN category candidates
    if category != "OPEN":
        is_ews = False

    query = """
    WITH latest_year AS (
        SELECT MAX(year) as max_year FROM cutoff_years
    ),
    active_branches AS (
        SELECT DISTINCT cr.college_id, cr.branch_id
        FROM cutoff_records cr
        JOIN cap_rounds cap ON cr.cap_round_id = cap.id
        JOIN cutoff_years y ON cap.year_id = y.id
        CROSS JOIN latest_year ly
        WHERE y.year = ly.max_year
    ),
    requested_branch AS (
        SELECT b.id as branch_id
        FROM branches b
        JOIN branch_families f ON b.family_id = f.id
        LEFT JOIN branch_aliases a ON a.branch_id = b.id
        WHERE b.canonical_name ILIKE :branch_q
           OR f.display_name ILIKE :branch_q
           OR a.alias_name ILIKE :branch_q
           OR :branch = 'Any'
    ),
    requested_category AS (
        SELECT rc.id as cat_id, rc.code as raw_category_code
        FROM raw_categories rc
        JOIN category_groups cg ON rc.group_id = cg.id
        WHERE 
            (
                cg.code = :category_q
                AND cg.code NOT IN ('ORPHAN', 'MI', 'EWS', 'TFWS')
                AND (:is_pwd = TRUE OR rc.code NOT LIKE 'PWD%')
                AND (:is_defense = TRUE OR rc.code NOT LIKE 'DEF%')
                AND (rc.code NOT LIKE '%ORPHAN%')
                AND (:is_female = TRUE OR rc.code NOT LIKE 'L%')
            )
            OR (:is_tfws = TRUE AND cg.code = 'TFWS' AND :category_q = 'TFWS')
            OR (:is_ews = TRUE AND cg.code = 'EWS' AND :category_q = 'EWS')
            OR (:has_minority = TRUE AND cg.code = 'MI' AND :category_q = 'MI')
    ),
    exists_male_standard AS (
        SELECT DISTINCT cr.college_id
        FROM cutoff_records cr
        JOIN raw_categories rc ON cr.raw_category_id = rc.id
        JOIN category_groups cg ON rc.group_id = cg.id
        WHERE cg.code = 'OPEN' 
          AND rc.code NOT LIKE 'L%'
          AND rc.code NOT LIKE 'PWD%'
          AND rc.code NOT LIKE 'DEF%'
    )
    SELECT 
        c.cap_code as college_code,
        c.canonical_name as college_name,
        b.canonical_name as branch_name,
        city.name as city,
        d.name as college_district,
        rc_cte.raw_category_code,
        'NO_CATEGORY_HISTORY' as data_availability_status,
        'This branch is active but has no past cutoff data for ' || :category_q || ' category.' as availability_message,
        :category_q as selected_category
    FROM active_branches ab
    JOIN colleges c ON ab.college_id = c.id
    JOIN branches b ON ab.branch_id = b.id
    JOIN localities loc ON c.locality_id = loc.id
    JOIN cities city ON loc.city_id = city.id
    JOIN districts d ON city.district_id = d.id
    JOIN regions r ON d.region_id = r.id
    LEFT JOIN cutoff_records cr 
           ON ab.college_id = cr.college_id 
          AND ab.branch_id = cr.branch_id
    LEFT JOIN requested_category rc_cte
           ON cr.raw_category_id = rc_cte.cat_id
    WHERE ab.branch_id IN (SELECT branch_id FROM requested_branch)
      AND (:district IS NULL OR d.name ILIKE :district)
      AND (:city IS NULL OR city.name ILIKE :city)
      AND (:locality IS NULL OR loc.name ILIKE :locality)
      AND (:region IS NULL OR r.name ILIKE :region)
      AND (:autonomous_only = FALSE OR c.is_autonomous = TRUE)
      AND (:government_only = FALSE OR c.institution_type IN ('Government', 'Government-Aided', 'University Dept'))
      AND (:is_male = FALSE OR ab.college_id IN (SELECT college_id FROM exists_male_standard))
      AND (rc_cte.raw_category_code IS NULL OR rc_cte.raw_category_code NOT LIKE '%MI%' OR c.minority_type = :user_minority_type)
    """

    params = {
        "branch": branch if branch else "Any",
        "branch_q": f"%{branch}%" if branch and branch != "Any" else "%",
        "category_q": category,
        "is_pwd": is_pwd,
        "is_defense": is_defense,
        "is_female": (gender == "Female"),
        "is_male": (gender == "Male"),
        "is_tfws": is_tfws,
        "is_ews": is_ews,
        "has_minority": minority_type != "Not Applicable",
        "user_minority_type": minority_type,
        "district": f"%{district}%" if district else None,
        "city": f"%{city_name}%" if city_name else None,
        "locality": f"%{locality}%" if locality else None,
        "region": f"%{region}%" if region else None,
        "autonomous_only": autonomous_only,
        "government_only": government_only
    }

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    
    if df.empty:
        return pd.DataFrame()
        
    df['college_university'] = df['college_district'].apply(get_home_university)
    
    if user_university is not None:
        def is_valid_seat(row):
            code = row['raw_category_code']
            if pd.isna(code):
                return True
            if code.endswith('S') or code in ('TFWS', 'EWS', 'MI', 'ORPHAN') or 'AI' in code:
                return True
            if code.endswith('H'):
                return user_university == row['college_university']
            if code.endswith('O'):
                return user_university != row['college_university']
            return True
            
        df = df[df.apply(is_valid_seat, axis=1)]
        
    if df.empty:
        return pd.DataFrame()
        
    grouped = df.groupby(['college_code', 'college_name', 'branch_name', 'city', 'college_district', 'data_availability_status', 'availability_message', 'selected_category'])['raw_category_code'].apply(lambda x: x.notnull().any()).reset_index()
    gaps = grouped[grouped['raw_category_code'] == False].drop(columns=['raw_category_code'])
    return gaps

