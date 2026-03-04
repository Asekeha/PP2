# 5. Match 'a' followed by anything, ending in 'b'
# Pattern: ^a.*b$
# .* → any character, zero or more

import re

s = input()
x = re.findall("^a.*b$", s)

if x:
    print("Match")
else:
    print("No Match")
