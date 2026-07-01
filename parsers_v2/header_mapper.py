import re

CATEGORY_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*$")

def is_header_line(l_words):
    if not l_words: return False
    cat_count = 0
    for w in l_words:
        text = w["text"].strip()
        if text not in ["Stage", "S"] and CATEGORY_PATTERN.match(text):
            cat_count += 1
    if cat_count >= 2 and cat_count / len(l_words) > 0.4:
        return True
    return False

def extract_headers(line_words):
    headers = []
    for w in line_words:
        text = w["text"].strip()
        # Avoid literal "Stage" or stray "S"
        if text not in ["Stage", "S"] and CATEGORY_PATTERN.match(text):
            center = (w["x0"] + w["x1"]) / 2
            headers.append({
                "category": text,
                "x0": w["x0"],
                "x1": w["x1"],
                "center": center
            })
    return headers
