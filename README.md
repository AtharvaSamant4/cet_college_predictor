# Maharashtra CET College Predictor

Student-friendly Maharashtra MHT-CET CAP college predictor using historical cutoff data from 2022 to 2025.

## Project Overview

This project helps engineering aspirants shortlist colleges by entering:

- CET percentile
- Category
- Branch or branch family
- Preferred location

The system returns recommendation cards with admission chance, latest cutoff, historical average, city, branch, and a plain-language explanation.

## Problem Statement

Students and parents usually read CAP cutoff PDFs manually, compare many category codes, and struggle to understand which colleges are realistic. This application converts historical CAP cutoff records into a searchable, explainable shortlist.

## Features

- Student-facing recommendation engine
- Branch family and branch keyword search
- Category mapping for CAP category codes
- Location and nearby-region fallback
- College metadata and city mapping
- 2022-2025 historical cutoff display
- Category-history warnings when data is unavailable
- Required percentile calculator
- Branch explorer
- Career match quiz
- FastAPI backend
- Vite + React frontend

## Architecture

```text
React / Vite frontend
        |
        v
FastAPI backend
        |
        v
CSV data layer
```

Future production architecture can move the CSV layer into PostgreSQL.

```text
React / Next.js
        |
        v
FastAPI
        |
        v
PostgreSQL
```

## Tech Stack

- Python
- FastAPI
- Pandas
- Vite
- React
- CSV data files

## Dataset Statistics

- Records: 138,798
- Colleges: 409
- Branches: 117
- Categories: 88 raw CAP categories
- Years: 2022, 2023, 2024, 2025
- CAP data source: parsed historical CAP cutoff PDFs

## Data Coverage

The recommendation engine uses historical cutoff records from:

- 2022 CAP rounds
- 2023 CAP rounds
- 2024 CAP rounds
- 2025 CAP rounds

## Installation

Clone the repository and install backend dependencies:

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Backend Setup

Run FastAPI locally:

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Frontend Setup

Run the Vite frontend:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Frontend URL:

```text
http://127.0.0.1:5173
```

## Environment Variables

Create environment files from `.env.example`.

Frontend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Backend:

```env
ALLOWED_ORIGINS=http://127.0.0.1:5173
```

For deployment, replace both values with public URLs.

## Running Locally

Terminal 1:

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Deployment requires:

- public backend URL
- public frontend URL
- `VITE_API_URL` configured before frontend build
- `ALLOWED_ORIGINS` configured for backend CORS

## Screenshots

Add screenshots here before publishing the GitHub release:

- Home page
- Recommendation results
- Target percentile page
- Branch explorer

## Known Limitations

- Recommendations are based on historical cutoff trends, not guaranteed admission outcomes.
- Sparse category and branch combinations may show limited or unavailable historical data.
- Actual CAP outcomes depend on seat matrix, reservation distribution, CAP round dynamics, and applicant competition.
- Forecasting is kept internal and is not part of the student-facing MVP.

## Future Roadmap

- PostgreSQL data layer
- Admin interface for metadata enrichment
- Manual college ranking enrichment
- Public deployment automation
- Load testing and caching
- Official CAP seat-matrix integration
