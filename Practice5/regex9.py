# 9. Insert spaces before capital letters
# Pattern: (?<!^)([A-Z])
# (?<!^) → not at beginning of string

import re

s = input()
result = re.sub(r"(?<!^)([A-Z])", r" \1", s)
print(result)
