import json
from pathlib import Path
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]

class CollegeNormalizer:
    def __init__(self, engine):
        self.engine = engine
        self._college_cache = {} # cap_code to id
        self._locality_cache = {} # name to id
        self._load_caches()
        
        with open(ROOT_DIR / "config" / "college_locality_map.json", "r") as f:
            self.locality_map = json.load(f)

    def _load_caches(self):
        with self.engine.connect() as conn:
            res = conn.execute(text("SELECT cap_code, id FROM colleges"))
            for row in res:
                self._college_cache[str(row[0])] = row[1]
                
            res = conn.execute(text("SELECT name, id FROM localities"))
            for row in res:
                self._locality_cache[row[0].lower()] = row[1]

    def _get_or_create_locality(self, locality_name: str, city_name: str) -> int:
        loc_key = locality_name.lower()
        if loc_key in self._locality_cache:
            return self._locality_cache[loc_key]
            
        with self.engine.begin() as conn:
            # Find city
            res = conn.execute(text("SELECT id FROM cities WHERE name = :city"), {"city": city_name})
            city_row = res.fetchone()
            if not city_row:
                raise ValueError(f"City {city_name} not found in DB")
            city_id = city_row[0]
            
            res = conn.execute(text("""
                INSERT INTO localities (name, city_id)
                VALUES (:name, :city_id)
                ON CONFLICT (name, city_id) DO NOTHING
                RETURNING id
            """), {"name": locality_name, "city_id": city_id})
            
            row = res.fetchone()
            if row:
                loc_id = row[0]
            else:
                res2 = conn.execute(text("SELECT id FROM localities WHERE name = :name AND city_id = :city_id"), 
                                  {"name": locality_name, "city_id": city_id})
                loc_id = res2.fetchone()[0]
                
            self._locality_cache[loc_key] = loc_id
            return loc_id

    def get_or_create(self, cap_code: str, college_name: str) -> int:
        cap_code = str(cap_code)
        
        if cap_code in self._college_cache:
            return self._college_cache[cap_code]
            
        # Determine locality
        mapping = self.locality_map.get(cap_code)
        if not mapping:
            # For prototype we only seed mapped ones, if it's missing it's outside prototype scope
            # We can map it to a generic "Unknown" but better to skip or put generic city
            raise ValueError(f"College {cap_code} not mapped to locality")
            
        loc_id = self._get_or_create_locality(mapping["locality"], mapping["city"])
        
        with self.engine.begin() as conn:
            query = text("""
                INSERT INTO colleges (cap_code, canonical_name, locality_id)
                VALUES (:cap_code, :name, :loc_id)
                ON CONFLICT (cap_code) DO NOTHING
                RETURNING id
            """)
            res = conn.execute(query, {
                "cap_code": cap_code,
                "name": college_name,
                "loc_id": loc_id
            })
            
            row = res.fetchone()
            if row:
                college_id = row[0]
            else:
                res2 = conn.execute(text("SELECT id FROM colleges WHERE cap_code = :cap_code"), {"cap_code": cap_code})
                college_id = res2.fetchone()[0]
                
            self._college_cache[cap_code] = college_id
            
            # Add alias
            conn.execute(text("""
                INSERT INTO college_aliases (college_id, alias_name, source)
                VALUES (:cid, :alias, 'PDF')
                ON CONFLICT (college_id, alias_name) DO NOTHING
            """), {"cid": college_id, "alias": college_name})
            
            return college_id
