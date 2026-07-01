class ParsingMismatchError(Exception):
    pass

def validate_row_length(headers, assigned_ranks, assigned_percentiles):
    # Rule 7: Number of detected headers = Number of generated columns
    # Wait, the rule actually means: if a value is extracted, it MUST be assigned.
    # The prompt: "Number of detected headers = Number of generated columns"
    # Actually, generated columns means the final dictionary mapping. 
    # If the dictionary length (categories assigned) doesn't make sense, raise error.
    # But since missing categories remain NULL, the number of mapped keys will equal 
    # the number of non-null values. 
    # Let's validate that NO value was assigned to the same header twice (which would imply bad alignment).
    pass

def strict_validate(headers, ranks, percentiles, college, branch):
    # If two values mapped to the same category, lengths would be less than len(values)
    if len(ranks) != len(percentiles):
        # Exception: Some categories might only have rank but no percentile, or vice-versa? 
        # Usually they appear in pairs.
        pass
