# 7. Convert snake_case to camelCase
# Pattern: _([a-z])
# () → capture group
# group(1) → letter after underscore

import re

s = input()
result = re.sub(r"_([a-z])", lambda x: x.group(1).upper(), s)
print(result)
