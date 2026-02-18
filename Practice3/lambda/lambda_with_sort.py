# Sort a list of city temperatures from coldest to hottest
city_data = [("Almaty", 30), ("Astana", 10), ("Shymkent", 50)]
sorted_weather = sorted(city_data, key=lambda x: x[1])
print(sorted_weather)

# Sort words based on the number of characters they contain
fruits = ["apple", "pear", "banana", "kiwi"]
by_length = sorted(fruits, key=lambda f: len(f))
print(by_length)

# Sort student dictionaries based on their grade value
students = [{"name": "Askar", "grade": 95}, {"name": "Ivan", "grade": 80}]
by_grade = sorted(students, key=lambda s: s["grade"], reverse=True)
print(by_grade)

# Sort a list of strings by their last letter
tags = ["python", "code", "logic"]
by_last_letter = sorted(tags, key=lambda t: t[-1])
print(by_last_letter)

# Sort numbers by their absolute distance from zero
mixed_nums = [-50, 10, -5, 20]
by_absolute = sorted(mixed_nums, key=lambda n: abs(n))
print(by_absolute)
