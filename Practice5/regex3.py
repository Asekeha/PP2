# 3. Find lowercase letters joined with underscore
# Pattern: ^[a-z]+_[a-z]+$
# [a-z]+ → one or more lowercase letters
# _      → literal underscore

import re

s = input()
x = re.findall("^[a-z]+_[a-z]+$", s)

if x:
    print("Match")
else:
    print("No Match")
