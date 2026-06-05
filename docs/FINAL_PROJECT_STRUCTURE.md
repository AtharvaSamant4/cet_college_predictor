# Final Project Structure

Git-visible structure:

```text
project_root/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── backend/
│   ├── app.py
│   ├── routes/
│   └── schemas/
├── career/
│   └── branch_match_engine.py
├── config/
│   ├── branch_mapping.py
│   ├── category_mapping.py
│   ├── category_mapping_v2.py
│   └── user_branch_families.py
├── data/
│   ├── branch_career_profiles.csv
│   ├── branch_descriptions.csv
│   ├── branch_explorer.csv
│   ├── career_quiz_questions.json
│   ├── college_master.csv
│   ├── college_master_city.csv
│   ├── college_metadata.csv
│   ├── college_ranking_template.csv
│   ├── college_rankings.csv
│   └── master_cutoffs.csv
├── docs/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── src/
├── parsers/
│   ├── parse_all.py
│   ├── parser_2022.py
│   ├── parser_2023.py
│   └── parser_2024.py
└── recommender/
    └── recommend_v6.py
```

Ignored local/generated folders:

```text
analysis/
scratch/
comparison/
output/
cutoff_pdfs/
venv/
frontend/node_modules/
frontend/dist/
__pycache__/
```
