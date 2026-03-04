# 4. One uppercase letter followed by lowercase letters
# Pattern: ^[A-Z][a-z]+$
# [A-Z]   → one capital letter
# [a-z]+  → one or more lowercase letters

import re

s = input()
x = re.findall("^[A-Z][a-z]+$", s)

if x:
    print("Match")
else:
    print("No Match")
