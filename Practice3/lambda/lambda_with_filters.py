# Keep only temperatures that are above freezing point (32F)
temps = [77, 95, 50, 32, 20, 10]
above_freezing = list(filter(lambda t: t > 32, temps))
print(above_freezing)

# Filter a list to keep only even numbers
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda n: n % 2 == 0, nums))
print(evens)

# Extract only the words that start with the letter 'P'
languages = ["Python", "C++", "Java", "PHP", "Go"]
p_langs = list(filter(lambda l: l.startswith("P"), languages))
print(p_langs)

# Remove empty strings from a list of data
user_data = ["Askar", "", "KBTU", "", "Student"]
clean_data = list(filter(lambda x: x != "", user_data))
print(clean_data)
