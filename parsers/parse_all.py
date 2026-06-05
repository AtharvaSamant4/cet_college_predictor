import pdfplumber
import pandas as pd
import re
import os

PDF_FOLDER = "cutoff_pdfs"
OUTPUT_FOLDER = "output"
CATEGORY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*$")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def parse_pdf(pdf_path, year, round_no):

    records = []

    with pdfplumber.open(pdf_path) as pdf:

        current_college_code = None
        current_college_name = None

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            # --------------------------
            # Find college on page
            # --------------------------

            for line in lines:

                match = re.match(
                    r"^(\d{4,5})\s*-\s*(.+)$",
                    line.strip()
                )

                if match:

                    code = match.group(1)

                    if len(code) <= 5:

                        current_college_code = code
                        current_college_name = match.group(2)

                        break

            # --------------------------
            # Find branches
            # --------------------------

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

                # --------------------------
                # Categories
                # --------------------------

                cat_match = re.search(
                    r"Stage\s+(.*?)\s+I\s",
                    block,
                    re.DOTALL
                )

                if not cat_match:
                    continue

                categories = (
                    cat_match.group(1)
                    .replace("\n", " ")
                    .split()
                )

                categories = [
                    x
                    for x in categories
                    if x not in ["S"]
                    and CATEGORY_PATTERN.match(x)
                ]

                # --------------------------
                # Ranks
                # --------------------------

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

                # --------------------------
                # Percentiles
                # --------------------------

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
                        "year": year,
                        "round": round_no,
                        "college_code": current_college_code,
                        "college_name": current_college_name,
                        "branch_code": branch_code,
                        "branch_name": branch_name,
                        "category": categories[idx],
                        "rank": ranks[idx],
                        "percentile": percentiles[idx]
                    })

    return pd.DataFrame(records)


# ======================================
# Process all PDFs
# ======================================

for pdf_file in os.listdir(PDF_FOLDER):

    if not pdf_file.endswith(".pdf"):
        continue

    match = re.match(
        r"(\d{4})_CAP(\d)\.pdf",
        pdf_file
    )

    if not match:
        continue

    year = int(match.group(1))
    round_no = int(match.group(2))

    print(f"\nProcessing {pdf_file}")

    pdf_path = os.path.join(
        PDF_FOLDER,
        pdf_file
    )

    df = parse_pdf(
        pdf_path,
        year,
        round_no
    )

    output_file = os.path.join(
        OUTPUT_FOLDER,
        pdf_file.replace(".pdf", ".csv")
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Rows: {len(df)} | Saved: {output_file}"
    )

print("\nDONE!")
