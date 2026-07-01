import os
import sys
from sqlalchemy import text
from typing import Dict, Optional

class CategoryNormalizer:
    def __init__(self, engine):
        self.engine = engine
        self._group_cache = {}
        self._raw_cache = {}
        self._load_caches()

    def _load_caches(self):
        with self.engine.connect() as conn:
            # Load category groups
            res = conn.execute(text("SELECT id, code FROM category_groups"))
            for row in res:
                self._group_cache[row[1]] = row[0]
            
            # Load raw categories
            res = conn.execute(text("SELECT id, code FROM raw_categories"))
            for row in res:
                self._raw_cache[row[1]] = row[0]

    def _determine_group(self, raw_code: str) -> str:
        # Determine the base category group from raw code
        if "OPEN" in raw_code: return "OPEN"
        if "OBC" in raw_code: return "OBC"
        if "SC" in raw_code: return "SC"
        if "ST" in raw_code: return "ST"
        if "VJ" in raw_code: return "VJ"
        if "NT1" in raw_code: return "NT1"
        if "NT2" in raw_code: return "NT2"
        if "NT3" in raw_code: return "NT3"
        if "SEBC" in raw_code: return "SEBC"
        if "EWS" in raw_code: return "EWS"
        if "TFWS" in raw_code: return "TFWS"
        if "MI" in raw_code: return "MI"
        if "ORPHAN" in raw_code: return "ORPHAN"
        if raw_code.startswith("DEF") or raw_code.startswith("DEFR"): return "DEFENSE"
        if raw_code.startswith("PWD") or raw_code.startswith("PWDR"): return "PWD"
        return "OPEN" # Fallback

    def _parse_attributes(self, raw_code: str):
        seat_type = None
        if raw_code.startswith("G"): seat_type = "Government"
        elif raw_code.startswith("L"): seat_type = "Unaided"
        
        home_university = raw_code.endswith("H")
        outside_district = raw_code.endswith("O")
        state_level = raw_code.endswith("S")
        
        return seat_type, home_university, outside_district, state_level

    def get_or_create(self, raw_code: str) -> int:
        if raw_code in self._raw_cache:
            return self._raw_cache[raw_code]
            
        group_code = self._determine_group(raw_code)
        group_id = self._group_cache.get(group_code)
        if not group_id:
            raise ValueError(f"Unknown category group {group_code} for raw code {raw_code}")
            
        seat_type, home_u, outside_d, state_l = self._parse_attributes(raw_code)
        
        with self.engine.begin() as conn:
            query = text("""
                INSERT INTO raw_categories (code, group_id, seat_type, home_university, outside_district, state_level)
                VALUES (:code, :group_id, :seat_type, :home_u, :outside_d, :state_l)
                ON CONFLICT (code) DO NOTHING
                RETURNING id
            """)
            res = conn.execute(query, {
                "code": raw_code,
                "group_id": group_id,
                "seat_type": seat_type,
                "home_u": home_u,
                "outside_d": outside_d,
                "state_l": state_l
            })
            
            row = res.fetchone()
            if row:
                cat_id = row[0]
            else:
                # Fetched nothing means it was already inserted by another process
                res2 = conn.execute(text("SELECT id FROM raw_categories WHERE code = :code"), {"code": raw_code})
                cat_id = res2.fetchone()[0]
                
            self._raw_cache[raw_code] = cat_id
            return cat_id
