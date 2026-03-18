# List of fruits
fruits = ["apple", "banana", "pear", "tangerine"]

# enumerate() returns index and value at the same time
# i = index (starting from 0), v = value
for i, v in enumerate(fruits):
    # i+1 is used to start numbering from 1 instead of 0
    # sep=":" changes separator between values
    print(i + 1, v, sep=":")


# List of football clubs
clubs = ["Real Madrid", "AC Milan", "Bayern Munich", "Barcelona"]

# Number of Champions League titles for each club
ucl = [15, 7, 6, 5]

# zip() combines two lists into pairs (tuple)
# Each club is paired with its number of trophies
# * is used to unpack the list when printing
print(*list(zip(clubs, ucl)))


# Variable with integer value
x = 10

# type() returns the data type of a variable
print(type(x))

# isinstance() checks if variable is of a specific type
print(isinstance(x, int))


# String that represents a number
a = "5"

# Convert string to integer
b = int(a)

# Perform arithmetic operation
print(b + 3)


# List of numbers as strings
nums = ["1", "2", "3"]

# map() applies int() to each element in the list
# Converts all strings to integers
nums_int = list(map(int, nums))

# Print converted list
print(nums_int)
