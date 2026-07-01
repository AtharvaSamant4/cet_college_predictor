-- 003_create_indexes.sql

-- Primary Indexes (for recommendation queries)
CREATE INDEX idx_cutoff_category_branch ON cutoff_records(raw_category_id, branch_id);
CREATE INDEX idx_college_locality ON colleges(locality_id);
CREATE INDEX idx_locality_city ON localities(city_id);
CREATE INDEX idx_cutoff_round ON cutoff_records(cap_round_id);
CREATE INDEX idx_cutoff_college_branch ON cutoff_records(college_id, branch_id);

-- Search Indexes (for fuzzy matching)
CREATE INDEX idx_college_name_trgm ON colleges USING gin (canonical_name gin_trgm_ops);
CREATE INDEX idx_alias_name_trgm ON college_aliases USING gin (alias_name gin_trgm_ops);
CREATE INDEX idx_branch_name_trgm ON branches USING gin (canonical_name gin_trgm_ops);
CREATE INDEX idx_branch_alias_trgm ON branch_aliases USING gin (alias_name gin_trgm_ops);

-- Analytical Indexes (for trends)
CREATE INDEX idx_cutoff_percentile ON cutoff_records(percentile);
CREATE INDEX idx_cutoff_covering ON cutoff_records(raw_category_id, branch_id, college_id, cap_round_id, percentile);
