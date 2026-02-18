# Convert a whole list of Fahrenheit temperatures to Celsius at once
fahrenheit_list = [77, 95, 50, 32]
celsius_list = list(map(lambda f: (f - 32) * 5 / 9, fahrenheit_list))
print(celsius_list)

# Multiply every number in the list by 2
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

# Convert a list of strings to uppercase
words = ["hello", "function", "lambda"]
upper_words = list(map(lambda w: w.upper(), words))
print(upper_words)

# Add a specific tax amount to a list of prices
prices = [100, 200, 300]
final_prices = list(map(lambda p: p * 1.12, prices))
print(final_prices)
