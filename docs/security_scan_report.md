# Security Scan Report

## Scan Scope

Scanned Git-visible source, config, frontend, backend, docs, and data metadata files.

Excluded generated/local folders:

- `frontend/node_modules/`
- `frontend/dist/`
- `venv/`
- `analysis/`
- `scratch/`
- `cutoff_pdfs/`
- `output/`
- Python cache folders

## Patterns Checked

- API key
- secret
- token
- password
- authorization
- bearer
- OpenAI-style `sk-` keys
- Gemini-style `AIza` keys
- ngrok authtokens
- client secrets
- private keys

## Findings

No real secrets found.

## False Positives

- `frontend/package-lock.json` contains `js-tokens`, which is a public npm package name.

## Environment Files

Safe template:

- `.env.example`

Ignored local environment files:

- `.env`
- `.env.*`
- `frontend/.env`
- `frontend/.env.*`

Published example exception:

- `frontend/.env.production.example`

## Verdict

PASS. No secret was found that blocks GitHub publication.
