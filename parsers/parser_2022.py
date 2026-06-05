import pdfplumber
import pandas as pd
import re

PDF_PATH = "cutoff_pdfs/2022_CAP1.pdf"

records = []

with pdfplumber.open(PDF_PATH) as pdf:

    current_college_code = None
    current_college_name = None

    for page_num, page in enumerate(pdf.pages):

        text = page.extract_text()

        if not text:
            continue

        lines = text.split("\n")

        # -----------------------------------
        # Find college on this page
        # -----------------------------------

        for line in lines:

            college_match = re.match(
                r"^(\d{4,5})\s*-\s*(.+)$",
                line.strip()
            )

            if college_match:

                code = college_match.group(1)

                # avoid branch codes
                if len(code) <= 5:

                    current_college_code = code
                    current_college_name = college_match.group(2)

                    break

        # -----------------------------------
        # Find all branches on page
        # -----------------------------------

        branch_matches = list(
            re.finditer(
                r"(\d{9,10})\s*-\s*(.+)",
                text
            )
        )

        for i, match in enumerate(branch_matches):

            branch_code = match.group(1)
            branch_name = match.group(2).strip()

            start = match.start()

            if i < len(branch_matches) - 1:
                end = branch_matches[i + 1].start()
            else:
                end = len(text)

            block = text[start:end]

            # -----------------------------------
            # Categories
            # -----------------------------------

            cat_match = re.search(
                r"Stage\s+(.*?)\s+I\s",
                block,
                re.DOTALL
            )

            if not cat_match:
                continue

            categories = (
                cat_match
                .group(1)
                .replace("\n", " ")
                .split()
            )

            categories = [
                c for c in categories
                if c not in ["S"]
            ]

            # -----------------------------------
            # Rank line
            # -----------------------------------

            rank_match = re.search(
                r"I\s+([\d\s]+)\s+\(",
                block,
                re.DOTALL
            )

            if not rank_match:
                continue

            ranks = re.findall(
                r"\d+",
                rank_match.group(1)
            )

            # -----------------------------------
            # Percentiles
            # -----------------------------------

            percentiles = re.findall(
                r"\(([\d\.]+)\)",
                block
            )

            count = min(
                len(categories),
                len(ranks),
                len(percentiles)
            )

            for idx in range(count):

                records.append({
                    "year": 2022,
                    "round": 1,
                    "college_code": current_college_code,
                    "college_name": current_college_name,
                    "branch_code": branch_code,
                    "branch_name": branch_name,
                    "category": categories[idx],
                    "rank": ranks[idx],
                    "percentile": percentiles[idx]
                })

df = pd.DataFrame(records)

df.to_csv(
    "2022_CAP1.csv",
    index=False
)

print()
print("=" * 50)
print("ROWS:", len(df))
print("=" * 50)
print()

print(df.head(20))
print()

print("Saved -> 2022_CAP1.csv")