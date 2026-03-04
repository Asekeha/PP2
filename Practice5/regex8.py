# 8. Split a string at uppercase letters
# Pattern: (?=[A-Z])
# (?= ) → positive lookahead

import re

s = input()
result = re.split(r"(?=[A-Z])", s)
print(result)
