import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from normalization.category_normalizer import CategoryNormalizer
from normalization.branch_normalizer import BranchNormalizer
from normalization.college_normalizer import CollegeNormalizer

def run_seed():
    load_dotenv(ROOT_DIR / ".env")
    engine = create_engine(os.getenv("DATABASE_URL"), isolation_level="AUTOCOMMIT")
    
    cat_norm = CategoryNormalizer(engine)
    branch_norm = BranchNormalizer(engine)
    college_norm = CollegeNormalizer(engine)
    
    print("Loading master_cutoffs.csv...")
    df = pd.read_csv(ROOT_DIR / "data" / "master_cutoffs.csv")
    
    # Filter to only prototype colleges
    prototype_codes = list(college_norm.locality_map.keys())
    # college_code is int in CSV, map keys are strings
    df['college_code'] = df['college_code'].astype(str)
    df = df[df['college_code'].isin(prototype_codes)]
    
    print(f"Filtered to {len(df)} cutoff records for prototype colleges.")
    
    # Cache to avoid DB lookups for years and rounds
    cap_round_cache = {} # (year, round) -> id
    
    with engine.begin() as conn:
        def get_or_create_cap_round(year: int, rnd: int) -> int:
            key = (year, rnd)
            if key in cap_round_cache:
                return cap_round_cache[key]
                
            # ensure year exists
            conn.execute(text("INSERT INTO cutoff_years (year) VALUES (:y) ON CONFLICT DO NOTHING"), {"y": year})
            res = conn.execute(text("SELECT id FROM cutoff_years WHERE year = :y"), {"y": year})
            year_id = res.fetchone()[0]
            
            # ensure round exists
            conn.execute(text("""
                INSERT INTO cap_rounds (year_id, round_number) 
                VALUES (:yid, :rnd) 
                ON CONFLICT (year_id, round_number) DO NOTHING
            """), {"yid": year_id, "rnd": rnd})
            
            res = conn.execute(text("SELECT id FROM cap_rounds WHERE year_id = :yid AND round_number = :rnd"), 
                               {"yid": year_id, "rnd": rnd})
            round_id = res.fetchone()[0]
            
            cap_round_cache[key] = round_id
            return round_id

        print("Normalizing and inserting data...")
        
        # Prepare batch insert data
        cutoff_inserts = []
        
        # We can't batch resolve easily because normalizers insert on the fly.
        # So we process row by row, but bulk insert cutoffs.
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            try:
                college_id = college_norm.get_or_create(row['college_code'], row['college_name'])
                branch_id = branch_norm.get_or_create(row['branch_code'], row['branch_name'])
                cat_id = cat_norm.get_or_create(row['category'])
                round_id = get_or_create_cap_round(int(row['year']), int(row['round']))
                
                # Percentile can be "NaN" or empty in some cases, handle it
                percentile = float(row['percentile'])
                rank = int(row['rank']) if pd.notna(row['rank']) else None
                
                cutoff_inserts.append({
                    "college_id": college_id,
                    "branch_id": branch_id,
                    "raw_category_id": cat_id,
                    "cap_round_id": round_id,
                    "rank": rank,
                    "percentile": percentile,
                    "stage": "I"
                })
            except Exception as e:
                print(f"Error processing row {idx} (College {row['college_code']}): {e}")
                
        print("Bulk inserting cutoff records...")
        
        # Deduplicate inserts based on unique constraint
        unique_inserts = {}
        for c in cutoff_inserts:
            key = (c["college_id"], c["branch_id"], c["raw_category_id"], c["cap_round_id"], c["stage"])
            # Keep highest percentile if duplicates exist (should not happen, but safeguard)
            if key not in unique_inserts or c["percentile"] > unique_inserts[key]["percentile"]:
                unique_inserts[key] = c
                
        final_inserts = list(unique_inserts.values())
        
        if final_inserts:
            conn.execute(text("""
                INSERT INTO cutoff_records (college_id, branch_id, raw_category_id, cap_round_id, rank, percentile, stage)
                VALUES (:college_id, :branch_id, :raw_category_id, :cap_round_id, :rank, :percentile, :stage)
                ON CONFLICT (college_id, branch_id, raw_category_id, cap_round_id, stage) DO NOTHING
            """), final_inserts)
            
        print(f"Successfully inserted {len(final_inserts)} cutoff records.")

if __name__ == "__main__":
    run_seed()
