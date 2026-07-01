import re

def is_stage_i(l_text):
    # Matches "I " at the start of a line. We explicitly skip "I-Non PWD" or "VII".
    return bool(re.match(r"^I\s+", l_text.strip()))
