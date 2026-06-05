# HOD Demo Checklist

## Before Demo

- [ ] Backend running
- [ ] Frontend running
- [ ] API docs opening
- [ ] Sample inputs ready
- [ ] Demo cases ready
- [ ] Screenshots ready
- [ ] Internet not required for demo
- [ ] Dataset files present
- [ ] No terminal errors visible

## Commands

Backend:

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```powershell
cd frontend
npm run dev -- --port 5173
```

URLs:

```text
Frontend: http://127.0.0.1:5173
Backend Docs: http://127.0.0.1:8000/docs
Health Check: http://127.0.0.1:8000/health
```

## Sample Inputs

### Case 1

- Percentile: 95
- Category: OPEN
- Branch Family: Computer & IT
- Location: Pune

### Case 2

- Percentile: 95
- Category: OPEN
- Branch Family: Artificial Intelligence
- Location: Pune

### Case 3

- Percentile: 90
- Category: OBC
- Branch Family: Computer & IT
- Location: Mumbai

### Case 4

- Percentile: 80
- Category: SC
- Branch Family: Mechanical
- Location: Nagpur

## During Demo

- [ ] Show problem statement
- [ ] Show dataset statistics
- [ ] Show frontend recommendation form
- [ ] Run Computer & IT Pune demo
- [ ] Point out confidence buckets
- [ ] Open a recommendation card
- [ ] Explain historical cutoff trend
- [ ] Explain recommendation reason
- [ ] Show fallback behavior if a location has few matches
- [ ] Show backend API docs briefly

## Screenshots To Keep Ready

- [ ] Home recommendation form
- [ ] Recommendation result buckets
- [ ] Recommendation card with explanation
- [ ] API docs page
- [ ] Audit score/report
- [ ] Stress test metrics
