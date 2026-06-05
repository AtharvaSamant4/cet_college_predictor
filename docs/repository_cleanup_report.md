# Repository Cleanup Report

## Cleanup Actions

- Added `.gitignore`.
- Added `.env.example`.
- Replaced stale root `README.md` with current 2022-2025 project documentation.
- Removed unused historical recommendation engines:
  - `recommender/recommend_v1.py`
  - `recommender/recommend_v2.py`
  - `recommender/recommend_v3.py`
  - `recommender/recommend_v4.py`
  - `recommender/recommend_v5.py`
- Removed duplicate documentation:
  - `docs/final_readme.md`

## Kept With Reason

- `career/`: active backend dependency for career quiz.
- `data/master_cutoffs.csv`: runtime dataset.
- `frontend/package-lock.json`: needed for reproducible frontend installs.
- `frontend/.env.production.example`: safe environment template.

## Ignored With Reason

- `analysis/`: generated audit reports and local QA artifacts.
- `scratch/`: experiments.
- `comparison/`: unused standalone comparison script.
- `output/`: generated parser outputs.
- `cutoff_pdfs/`: large local source PDFs.
- `frontend/dist/`: generated build output.
- `frontend/node_modules/`: dependency install output.
- `venv/`: local Python environment.

## Final Git-Visible Root

- `.env.example`
- `.gitignore`
- `README.md`
- `requirements.txt`
- `backend/`
- `career/`
- `config/`
- `data/`
- `docs/`
- `frontend/`
- `parsers/`
- `recommender/`

## Note On Requested Root Shape

The requested root list did not include `career/`. It is kept because it is active production code imported by `backend/routes/career.py`. Removing it would break the backend.
