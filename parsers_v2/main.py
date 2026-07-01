import os
import re
import pandas as pd
from .parser_base import ParserBase

PDF_FOLDER = "cutoff_pdfs"
OUTPUT_FILE = "data/master_cutoffs_v2.csv"

def run_all():
    all_dfs = []
    
    for pdf_file in sorted(os.listdir(PDF_FOLDER)):
        if not pdf_file.endswith(".pdf"):
            continue
            
        match = re.match(r"(\d{4})_CAP(\d)\.pdf", pdf_file)
        if not match:
            continue
            
        year = int(match.group(1))
        round_no = int(match.group(2))
        
        print(f"Parsing {pdf_file} using Parser V2 (Coordinate Extraction)...")
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        
        parser = ParserBase(year, round_no, pdf_path)
        try:
            df = parser.run()
            all_dfs.append(df)
            print(f"  -> Extracted {len(df)} records")
        except Exception as e:
            print(f"  -> ERROR parsing {pdf_file}: {e}")
            raise e
            
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Generated {OUTPUT_FILE} with {len(final_df)} validated records.")

if __name__ == "__main__":
    run_all()
