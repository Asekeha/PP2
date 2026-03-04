# 2. Match 'a' followed by two to three 'b'
# Pattern: ^ab{2,3}$
# {2,3} → between 2 and 3 repetitions

import re

s = input()
x = re.findall("^ab{2,3}$", s)

if x:
    print("Match")
else:
    print("No Match")
