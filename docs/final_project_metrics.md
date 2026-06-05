# Final Project Metrics

## Dataset Metrics

| Metric | Value |
| --- | ---: |
| Total Records | 88,144 |
| Total Colleges | 375 |
| Total Branches | 113 |
| Total Raw Categories | 82 |
| Years Covered | 2022, 2023, 2024 |
| CAP Rounds Covered | 1, 2, 3 |

## Recommendation Runtime

| Metric | Value |
| --- | ---: |
| Stress Tests | 500 |
| Successful Tests | 500 |
| Failed Tests | 0 |
| Empty Results | 11 |
| Empty Result Rate | 2.20% |
| Average Runtime | 0.3434 seconds |
| Worst Runtime | 0.4820 seconds |
| Median Recommendation Count | 6 |

## Stress Test Results By Branch Family

| Family | Tests | Empty Results | Average Count |
| --- | ---: | ---: | ---: |
| Artificial Intelligence | 52 | 0 | 55.1 |
| Chemical | 50 | 1 | 14.7 |
| Civil | 44 | 0 | 20.1 |
| Computer & IT | 51 | 0 | 42.8 |
| Electronics & Telecom | 48 | 0 | 34.2 |
| Mechanical | 48 | 0 | 30.5 |
| Others | 54 | 0 | 21.2 |
| Production & Manufacturing | 51 | 5 | 3.9 |
| Robotics & Automation | 53 | 4 | 6.7 |
| Textile | 49 | 1 | 5.5 |

## Audit Results

| Module | Status |
| --- | --- |
| Data Audit | PASS |
| Category Validation | PASS |
| Branch Validation | PASS |
| Recommendation Engine Testing | PASS |
| Forecast Validation | PASS |
| Reliability Validation | PASS |
| Edge Case Testing | PASS |
| Performance Testing | PASS |
| Security and Robustness | PASS |

Overall audit score: 100/100

## Forecast Metrics

| Metric | Value |
| --- | ---: |
| Total College-Branch-Category Combinations | 26,706 |
| Forecastable Combinations | 8,463 |
| Non-Forecastable Combinations | 18,243 |
| Forecast Coverage | 31.69% |

Product decision: forecast should remain internal only for the MVP.
