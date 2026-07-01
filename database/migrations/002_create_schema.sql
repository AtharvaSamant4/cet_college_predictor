-- 002_create_schema.sql

-- Geographic Hierarchy
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, region_id)
);

CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    district_id INTEGER NOT NULL REFERENCES districts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, district_id)
);

CREATE TABLE localities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city_id INTEGER NOT NULL REFERENCES cities(id),
    pin_code VARCHAR(10),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, city_id)
);

-- Universities
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    short_name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Colleges
CREATE TABLE colleges (
    id SERIAL PRIMARY KEY,
    cap_code INTEGER NOT NULL UNIQUE,
    canonical_name VARCHAR(300) NOT NULL,
    short_name VARCHAR(100),
    locality_id INTEGER NOT NULL REFERENCES localities(id),
    university_id INTEGER REFERENCES universities(id),
    institution_type VARCHAR(30) CHECK (institution_type IN ('Government', 'Government-Aided', 'Unaided Private', 'University Dept', 'Autonomous', 'Deemed')),
    is_autonomous BOOLEAN NOT NULL DEFAULT FALSE,
    is_minority BOOLEAN NOT NULL DEFAULT FALSE,
    minority_type VARCHAR(50),
    naac_grade VARCHAR(5),
    nba_accredited BOOLEAN DEFAULT FALSE,
    website VARCHAR(200),
    established_year INTEGER,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE college_aliases (
    id SERIAL PRIMARY KEY,
    college_id INTEGER NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
    alias_name VARCHAR(300) NOT NULL,
    source VARCHAR(50) NOT NULL,
    year_seen INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(college_id, alias_name)
);

-- Branches
CREATE TABLE branch_families (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    cap_code VARCHAR(20) UNIQUE,
    canonical_name VARCHAR(200) NOT NULL UNIQUE,
    family_id INTEGER NOT NULL REFERENCES branch_families(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE branch_aliases (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    alias_name VARCHAR(200) NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(branch_id, alias_name)
);

-- Categories
CREATE TABLE category_groups (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE raw_categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    group_id INTEGER NOT NULL REFERENCES category_groups(id),
    seat_type VARCHAR(20) CHECK (seat_type IN ('Government', 'Unaided')),
    home_university BOOLEAN,
    outside_district BOOLEAN,
    state_level BOOLEAN,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cutoff Dimensions
CREATE TABLE cutoff_years (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL UNIQUE CHECK (year >= 2020 AND year <= 2030),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE cap_rounds (
    id SERIAL PRIMARY KEY,
    year_id INTEGER NOT NULL REFERENCES cutoff_years(id),
    round_number INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 4),
    pdf_filename VARCHAR(100),
    parsed_at TIMESTAMPTZ,
    record_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(year_id, round_number)
);

-- Core Fact Table
CREATE TABLE cutoff_records (
    id SERIAL PRIMARY KEY,
    college_id INTEGER NOT NULL REFERENCES colleges(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    raw_category_id INTEGER NOT NULL REFERENCES raw_categories(id),
    cap_round_id INTEGER NOT NULL REFERENCES cap_rounds(id),
    rank INTEGER,
    percentile DECIMAL(10,7),
    stage VARCHAR(5) DEFAULT 'I',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(college_id, branch_id, raw_category_id, cap_round_id, stage)
);

-- Audit and Verification
CREATE TABLE verification_records (
    id SERIAL PRIMARY KEY,
    college_id INTEGER NOT NULL REFERENCES colleges(id),
    field_name VARCHAR(50) NOT NULL,
    pdf_value TEXT,
    verified_value TEXT,
    source_url TEXT,
    verified_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE', 'NORMALIZE', 'VERIFY')),
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
