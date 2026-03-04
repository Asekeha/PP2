# 1. Match 'a' followed by zero or more 'b'
# Pattern: ^ab*$
# *  → zero or more occurrences
# ^  → start of string
# $  → end of string

import re

s = input()
x = re.findall("^ab*$", s)

if x:
    print("Match")
else:
    print("No Match")
