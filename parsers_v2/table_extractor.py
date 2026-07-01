import re

def group_words_by_lines(words, y_tolerance=2):
    lines = {}
    for w in words:
        y = round(w["top"] / y_tolerance) * y_tolerance
        if y not in lines:
            lines[y] = []
        lines[y].append(w)
    
    sorted_ys = sorted(lines.keys())
    structured_lines = []
    for y in sorted_ys:
        l_words = sorted(lines[y], key=lambda w: w["x0"])
        l_text = " ".join([w["text"] for w in l_words])
        structured_lines.append((l_words, l_text))
    return structured_lines

def extract_blocks(structured_lines):
    blocks = []
    current_college = None
    current_branch = None
    current_block_lines = []
    
    for l_words, l_text in structured_lines:
        c_match = re.match(r"^(\d{4,5})\s*-\s*(.+)$", l_text.strip())
        if c_match and len(c_match.group(1)) <= 5:
            current_college = (c_match.group(1), c_match.group(2))
            continue
            
        b_match = re.match(r"^(\d{9,10})\s*-\s*(.+)$", l_text.strip())
        if b_match:
            if current_branch and current_college:
                blocks.append((current_college, current_branch, current_block_lines))
            current_branch = (b_match.group(1), b_match.group(2).strip())
            current_block_lines = []
            continue
            
        if current_branch:
            current_block_lines.append((l_words, l_text))
            
    if current_branch and current_college:
        blocks.append((current_college, current_branch, current_block_lines))
        
    return blocks
