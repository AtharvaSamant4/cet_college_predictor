# Final HOD Demo Script

## 1. Problem Statement

Maharashtra CET students struggle to identify suitable engineering colleges because CAP cutoff PDFs are long, technical, and difficult to compare across years, categories, branches, and locations.

This system converts historical CAP cutoff data into a student-friendly college recommendation tool.

## 2. Existing Student Pain Points

- Students do not understand raw CAP category codes like `GOPENS`, `LOBCS`, or `PWDOPENS`.
- Students think in career families like Computer, AI, Mechanical, and Civil, not CAP branch names.
- Cutoff PDFs are hard to search manually.
- Students often miss good colleges because they search only one exact branch name.
- Parents and counselors need explainable results, not black-box predictions.

## 3. Dataset Statistics

- Total records: 88,144
- Total colleges: 375
- Total branches: 113
- Total raw categories: 82
- Years covered: 2022, 2023, 2024
- CAP rounds covered: 1, 2, 3

## 4. System Architecture

```text
React Frontend
      ↓
FastAPI Backend
      ↓
Recommendation Engine V6
      ↓
Cleaned CAP Cutoff Dataset
```

The frontend collects student inputs. The FastAPI backend validates requests and calls the existing recommendation engine. The engine uses historical cutoff data, category mapping, branch families, location filters, confidence bands, and reliability labels.

## 5. Recommendation Flow

1. Student enters percentile, category, branch family, and optional location.
2. Category is mapped from student-friendly input to raw CAP categories.
3. Branch family is mapped to all relevant branch names.
4. Colleges are filtered by branch, category, and location.
5. Historical average cutoff is calculated.
6. Difference is calculated:

```text
difference = student_percentile - average_cutoff
```

7. Confidence level is assigned:

- `VERY SAFE`
- `SAFE`
- `MODERATE`
- `DREAM`

8. Results are sorted and displayed with explanations.

## 6. Explainability Flow

Each recommendation shows:

- College name
- Branch name
- City
- Historical cutoff for 2022
- Historical cutoff for 2023
- Historical cutoff for 2024
- Average cutoff
- Student percentile
- Difference
- Confidence level
- Reliability level
- Recommendation reason

Example:

```text
Your percentile exceeds the historical cutoff by 2.13 points.
This branch has remained stable over the last three CAP cycles.
```

## 7. Sample Demo Scenarios

Use these during the demo:

| Scenario | Percentile | Category | Branch Family | Location |
| --- | ---: | --- | --- | --- |
| High percentile CS student | 95 | OPEN | Computer & IT | Pune |
| AI-focused student | 95 | OPEN | Artificial Intelligence | Pune |
| Mumbai OBC student | 90 | OBC | Computer & IT | Mumbai |
| Electronics student | 85 | OPEN | Electronics & Telecom | Pune |
| Nagpur mechanical student | 80 | SC | Mechanical | Nagpur |
| Nashik civil student | 75 | OPEN | Civil | Nashik |

## 8. Key Features

- Cleaned historical CAP dataset
- Student-friendly category mapping
- Student-friendly branch families
- AI search tags for CSE AI/ML, AI/DS, Data Science, and related branches
- Location-based filtering
- Safe, Moderate, Dream style recommendations
- Historical cutoff trend display
- Recommendation explainability
- FastAPI backend
- React frontend
- Stress-tested recommendation engine

## 9. Stress Test Results

Recommendation stress test:

- Total tests: 500
- Successes: 500
- Failures: 0
- Empty results: 11
- Empty result rate: 2.20%
- Average runtime: 0.3434 seconds
- Worst runtime: 0.4820 seconds

System audit:

- Data Audit: PASS
- Category Validation: PASS
- Branch Validation: PASS
- Recommendation Engine Testing: PASS
- Forecast Validation: PASS
- Reliability Validation: PASS
- Edge Case Testing: PASS
- Performance Testing: PASS
- Security and Robustness: PASS
- Overall audit score: 100/100

## 10. Current Limitations

- College ranking scores are not yet manually enriched.
- College metadata such as autonomous status, minority status, and region requires manual completion.
- Forecast coverage is only 31.69%, so forecast should remain internal and not be student-facing in the MVP.
- Recommendations are based on historical cutoff behavior, not guaranteed admission.

## 11. Future Scope

- Complete college ranking enrichment.
- Complete district, region, autonomous, minority, and college type metadata.
- Add college comparison in frontend.
- Add counselor dashboard.
- Add better fallback suggestions for low-result cases.
- Deploy backend and frontend publicly.
- Add verified official college metadata sources.
