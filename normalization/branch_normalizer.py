import sys
from pathlib import Path
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from config.branch_mapping import BRANCH_MAP, BRANCH_ALIASES

class BranchNormalizer:
    def __init__(self, engine):
        self.engine = engine
        self._family_cache = {}
        self._branch_cache = {} # branch_id by (cap_code, canonical_name)
        self._alias_cache = {}  # branch_id by alias_name
        self._load_caches()

    def _load_caches(self):
        with self.engine.connect() as conn:
            res = conn.execute(text("SELECT id, code FROM branch_families"))
            for row in res:
                self._family_cache[row[1]] = row[0]
                
            res = conn.execute(text("SELECT id, cap_code, canonical_name FROM branches"))
            for row in res:
                self._branch_cache[row[2]] = row[0]
                
            res = conn.execute(text("SELECT alias_name, branch_id FROM branch_aliases"))
            for row in res:
                self._alias_cache[row[0]] = row[1]

    def _determine_family(self, branch_name: str) -> int:
        for family_code, branches in BRANCH_MAP.items():
            if branch_name in branches:
                return self._family_cache[family_code]
        
        # Check aliases if not direct match
        branch_key = branch_name.strip().upper().replace(" ", "_")
        family_codes = BRANCH_ALIASES.get(branch_key)
        if family_codes:
            return self._family_cache[family_codes[0]]
            
        # Default to some fallback or error?
        # Create a generic family if missing
        return self._family_cache.get("CS") # Or handle gracefully

    def get_or_create(self, branch_code: str, branch_name: str) -> int:
        branch_name = branch_name.strip()
        branch_code = str(branch_code).strip()
        
        if branch_name in self._branch_cache:
            return self._branch_cache[branch_name]
            
        if branch_name in self._alias_cache:
            return self._alias_cache[branch_name]
            
        # Create new branch
        family_id = self._determine_family(branch_name)
        
        with self.engine.begin() as conn:
            # Upsert branch
            query = text("""
                INSERT INTO branches (cap_code, canonical_name, family_id)
                VALUES (:code, :name, :family)
                ON CONFLICT (canonical_name) DO NOTHING
                RETURNING id
            """)
            res = conn.execute(query, {
                "code": branch_code,
                "name": branch_name,
                "family": family_id
            })
            
            row = res.fetchone()
            if row:
                branch_id = row[0]
            else:
                res2 = conn.execute(text("SELECT id FROM branches WHERE canonical_name = :name"), {"name": branch_name})
                branch_id = res2.fetchone()[0]
                
            self._branch_cache[branch_name] = branch_id
            return branch_id
