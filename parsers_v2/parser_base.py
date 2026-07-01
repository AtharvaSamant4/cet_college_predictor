import pdfplumber
import pandas as pd
import re
from .table_extractor import group_words_by_lines, extract_blocks
from .header_mapper import extract_headers, is_header_line
from .category_mapper import map_values_to_headers
from .stage_mapper import is_stage_i

def strict_validate(mapped_ranks, rank_words, mapped_percentiles, percentile_words, coll, branch):
    # Rule 7 implementation
    # Every extracted value word MUST be mapped. If the length differs, it means a value was overwritten 
    # (multiple values mapped to same header) or completely unmapped.
    valid_rank_words = [w for w in rank_words if w["text"] not in ["I", "S", ""]]
    valid_perc_words = [w for w in percentile_words if w["text"] not in ["I", "S", ""]]
    
    if len(mapped_ranks) != len(valid_rank_words):
        raise ValueError(f"FATAL: Mapped ranks count ({len(mapped_ranks)}) != Valid rank words ({len(valid_rank_words)}) at College {coll} Branch {branch}")
        
    if len(mapped_percentiles) != len(valid_perc_words):
        raise ValueError(f"FATAL: Mapped percentiles count ({len(mapped_percentiles)}) != Valid percentile words ({len(valid_perc_words)}) at College {coll} Branch {branch}")


class ParserBase:
    def __init__(self, year, round_no, pdf_path):
        self.year = year
        self.round_no = round_no
        self.pdf_path = pdf_path
        self.records = []

    def run(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages):
                if page_num % 100 == 0:
                    print(f"  Processing page {page_num}/{total_pages}...", flush=True)
                words = page.extract_words(x_tolerance=2, y_tolerance=2)
                structured_lines = group_words_by_lines(words)
                blocks = extract_blocks(structured_lines)
                
                for (coll_code, coll_name), (branch_code, branch_name), block_lines in blocks:
                    headers = []
                    for i, (l_words, l_text) in enumerate(block_lines):
                        if is_header_line(l_words):
                            potential_headers = extract_headers(l_words)
                            if potential_headers:
                                headers = potential_headers
                                
                        if is_stage_i(l_text):
                            if not headers:
                                continue
                                
                            rank_words = [w for w in l_words if re.match(r"^\d+$", w["text"])]
                            
                            percentile_words = []
                            if i + 1 < len(block_lines):
                                p_words, p_text = block_lines[i+1]
                                percentile_words = [w for w in p_words if re.match(r"^\([\d\.]+\)$", w["text"])]
                                
                            try:
                                mapped_ranks = map_values_to_headers(rank_words, headers)
                                mapped_percentiles = map_values_to_headers(percentile_words, headers)
                            except ValueError as e:
                                raise ValueError(f"At {coll_code} {branch_code}: {e}")
                            
                            strict_validate(mapped_ranks, rank_words, mapped_percentiles, percentile_words, coll_code, branch_code)
                            
                            for cat in headers:
                                c = cat["category"]
                                rank_val = mapped_ranks.get(c, None)
                                perc_val = mapped_percentiles.get(c, None)
                                
                                if rank_val or perc_val:
                                    if perc_val:
                                        perc_val = perc_val.replace("(", "").replace(")", "")
                                    self.records.append({
                                        "year": self.year,
                                        "round": self.round_no,
                                        "college_code": coll_code,
                                        "college_name": coll_name,
                                        "branch_code": branch_code,
                                        "branch_name": branch_name,
                                        "category": c,
                                        "rank": rank_val,
                                        "percentile": perc_val
                                    })
        return pd.DataFrame(self.records)
