def map_values_to_headers(value_words, headers):
    mapping = {}
    for vw in value_words:
        text = vw["text"].strip()
        if text in ["I", "S", ""] or "Stage" in text:
            continue
            
        v_center = (vw["x0"] + vw["x1"]) / 2
        
        closest_header = None
        min_dist = float('inf')
        for h in headers:
            dist = abs(h["center"] - v_center)
            if dist < min_dist:
                min_dist = dist
                closest_header = h["category"]
                
        if closest_header:
            if closest_header in mapping:
                raise ValueError(f"Alignment Error: Two values mapped to same category {closest_header}. Values: {mapping[closest_header]}, {text}")
            mapping[closest_header] = text
            
    return mapping
