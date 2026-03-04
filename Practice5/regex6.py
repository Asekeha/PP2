# 6. Replace space, comma, or dot with colon
# Pattern: [ ,.]
# [] → character set

import re

s = input()
result = re.sub("[ ,.]", ":", s)
print(result)
