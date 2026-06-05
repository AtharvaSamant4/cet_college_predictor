# Deployment Guide

## Overview

The project has two deployable parts:

- FastAPI backend
- Vite React frontend

The frontend must know the public backend URL at build time through `VITE_API_URL`.

## Backend Deployment

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Production command example:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

## Frontend Deployment

Install dependencies:

```bash
cd frontend
npm install
```

Build:

```bash
npm run build
```

Deploy the generated `frontend/dist/` folder to a static frontend host.

## Environment Variables

Root template:

```env
VITE_API_URL=
ALLOWED_ORIGINS=
```

Frontend:

```env
VITE_API_URL=https://your-backend-url
```

Backend:

```env
ALLOWED_ORIGINS=https://your-frontend-url
```

## CORS

The backend reads `ALLOWED_ORIGINS` and allows requests from the configured frontend origin.

Example:

```env
ALLOWED_ORIGINS=https://cet-college-predictor.example.com
```

For multiple origins, use commas:

```env
ALLOWED_ORIGINS=https://site-one.example.com,https://site-two.example.com
```

## VITE_API_URL

Vite exposes variables starting with `VITE_` to frontend code at build time.

Example:

```env
VITE_API_URL=https://cet-api.example.com
```

If this is missing during deployment, the frontend can load but API calls may fail.

## Local Development

Terminal 1:

```bash
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

## ngrok Demo

Start backend and frontend locally, then expose both ports:

```bash
ngrok http 8000
ngrok http 5173
```

Set frontend environment:

```env
VITE_API_URL=https://your-backend-ngrok-url
```

Set backend environment:

```env
ALLOWED_ORIGINS=https://your-frontend-ngrok-url
```

## GitHub Push Workflow

Initialize repository if needed:

```bash
git init
git remote add origin https://github.com/AtharvaSamant4/cet_college_predictor.git
```

Review files:

```bash
git status --short
git status --short --ignored
```

Stage and commit:

```bash
git add .
git commit -m "Release v1"
```

Push:

```bash
git branch -M main
git push -u origin main
```
