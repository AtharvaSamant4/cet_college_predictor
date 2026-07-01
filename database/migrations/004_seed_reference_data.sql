-- 004_seed_reference_data.sql

-- Regions
INSERT INTO regions (name) VALUES
('Mumbai Region'),
('Pune Region'),
('Nashik Region'),
('Aurangabad Region'),
('Amravati Region'),
('Nagpur Region')
ON CONFLICT (name) DO NOTHING;

-- Districts (for Mumbai Region initially)
INSERT INTO districts (name, region_id) 
SELECT 'Mumbai', id FROM regions WHERE name = 'Mumbai Region'
ON CONFLICT (name, region_id) DO NOTHING;

INSERT INTO districts (name, region_id) 
SELECT 'Mumbai Suburban', id FROM regions WHERE name = 'Mumbai Region'
ON CONFLICT (name, region_id) DO NOTHING;

INSERT INTO districts (name, region_id) 
SELECT 'Thane', id FROM regions WHERE name = 'Mumbai Region'
ON CONFLICT (name, region_id) DO NOTHING;

INSERT INTO districts (name, region_id) 
SELECT 'Palghar', id FROM regions WHERE name = 'Mumbai Region'
ON CONFLICT (name, region_id) DO NOTHING;

INSERT INTO districts (name, region_id) 
SELECT 'Raigad', id FROM regions WHERE name = 'Mumbai Region'
ON CONFLICT (name, region_id) DO NOTHING;

-- Cities
INSERT INTO cities (name, district_id) 
SELECT 'Mumbai', id FROM districts WHERE name = 'Mumbai'
ON CONFLICT (name, district_id) DO NOTHING;

INSERT INTO cities (name, district_id) 
SELECT 'Mumbai', id FROM districts WHERE name = 'Mumbai Suburban'
ON CONFLICT (name, district_id) DO NOTHING;

INSERT INTO cities (name, district_id) 
SELECT 'Thane', id FROM districts WHERE name = 'Thane'
ON CONFLICT (name, district_id) DO NOTHING;

INSERT INTO cities (name, district_id) 
SELECT 'Navi Mumbai', id FROM districts WHERE name = 'Thane'
ON CONFLICT (name, district_id) DO NOTHING;

INSERT INTO cities (name, district_id) 
SELECT 'Navi Mumbai', id FROM districts WHERE name = 'Raigad'
ON CONFLICT (name, district_id) DO NOTHING;


-- Branch Families
INSERT INTO branch_families (code, display_name) VALUES
('CS', 'Computer Science & Engineering'),
('IT', 'Information Technology'),
('AI_DS', 'Artificial Intelligence & Data Science'),
('AI_ML', 'Artificial Intelligence & Machine Learning'),
('ENTC', 'Electronics & Telecommunication'),
('ELECTRICAL', 'Electrical Engineering'),
('MECHANICAL', 'Mechanical Engineering'),
('CIVIL', 'Civil Engineering'),
('CHEMICAL', 'Chemical Engineering'),
('ROBOTICS', 'Robotics & Automation'),
('AUTOMOBILE', 'Automobile Engineering'),
('INSTRUMENTATION', 'Instrumentation Engineering'),
('AERONAUTICAL', 'Aeronautical Engineering'),
('AGRICULTURE', 'Agricultural Engineering'),
('BIOTECH', 'Bio Technology'),
('FOOD_TECH', 'Food Technology'),
('FIRE_SAFETY', 'Fire & Safety Engineering'),
('TEXTILE', 'Textile Engineering'),
('MATERIALS', 'Materials & Polymer Technology'),
('PRINTING_PACKAGING', 'Printing & Packaging'),
('MINING', 'Mining Engineering')
ON CONFLICT (code) DO NOTHING;

-- Category Groups
INSERT INTO category_groups (code, display_name) VALUES
('OPEN', 'Open (General)'),
('OBC', 'Other Backward Classes'),
('SC', 'Scheduled Caste'),
('ST', 'Scheduled Tribe'),
('VJ', 'Vimukta Jati (VJ / DT - A)'),
('NT1', 'Nomadic Tribes 1 (NT-B)'),
('NT2', 'Nomadic Tribes 2 (NT-C)'),
('NT3', 'Nomadic Tribes 3 (NT-D)'),
('SEBC', 'Socially and Educationally Backward Classes'),
('EWS', 'Economically Weaker Section'),
('TFWS', 'Tuition Fee Waiver Scheme'),
('MI', 'Minority'),
('ORPHAN', 'Orphan'),
('PWD', 'Persons with Disability'),
('DEFENSE', 'Defense')
ON CONFLICT (code) DO NOTHING;

-- Cutoff Years
INSERT INTO cutoff_years (year) VALUES (2022), (2023), (2024), (2025)
ON CONFLICT (year) DO NOTHING;
