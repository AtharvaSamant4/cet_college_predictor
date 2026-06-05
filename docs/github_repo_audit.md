# GitHub Repository Audit

## Scope

Repository root: `cet_college_predictor`

Git-visible file count after `.gitignore`: 54.

## KEEP

Production application files:

- `README.md`
- `requirements.txt`
- `.gitignore`
- `.env.example`
- `backend/`
- `career/`
- `config/`
- `data/`
- `frontend/`
- `parsers/`
- `recommender/recommend_v6.py`
- `docs/`

Notes:

- `career/` is kept because `backend/routes/career.py` imports `career.branch_match_engine`.
- `recommender/recommend_v6.py` is the only production recommendation engine kept.

## REMOVE

Removed during cleanup:

- `recommender/recommend_v1.py`
- `recommender/recommend_v2.py`
- `recommender/recommend_v3.py`
- `recommender/recommend_v4.py`
- `recommender/recommend_v5.py`
- `docs/final_readme.md`

Reason:

- Old recommender versions were not imported by backend, frontend, docs, parsers, or config.
- `docs/final_readme.md` duplicated the root `README.md`.

## IGNORE

Local/generated folders excluded by `.gitignore`:

- `analysis/`
- `scratch/`
- `comparison/`
- `output/`
- `cutoff_pdfs/`
- `venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `__pycache__/`
- `.vscode/`
- `.idea/`
- ngrok logs and temporary files

## GENERATED

Generated artifacts intentionally not published:

- Parsed intermediate CAP CSVs under `output/`
- Audit reports under `analysis/`
- Frontend build output under `frontend/dist/`
- Python bytecode caches
- Node dependencies
- Local browser profiles

## SECRET

No real secrets were found in Git-visible files.

False positive:

- `frontend/package-lock.json` contains the package name `js-tokens`; this is not a credential.

## Risk Notes

- `data/master_cutoffs.csv` is about 20 MB and is required for the current CSV-based backend.
- CAP PDFs are ignored because the cleaned master CSV is the runtime source.
- `comparison/` is ignored because it is not connected to the production backend or frontend.
