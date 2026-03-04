# 10. Convert camelCase to snake_case
# Pattern: (?<!^)([A-Z])
# Add underscore before capital letters
# Then convert to lowercase

import re

s = input()
result = re.sub(r"(?<!^)([A-Z])", r"_\1", s).lower()
print(result)
