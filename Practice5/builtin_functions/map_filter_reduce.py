a = [1,2,3,4,5,6]
b = list(map(lambda x: x * 2 ,a))
c = list(filter(lambda x: x % 3 == 0,a))
print(b)
print(c)

from functools import reduce
result = reduce(lambda x,y:x*y,a)
print(result)
# List of numbers
a = [1, 2, 3, 4, 5, 6]

# map() applies a function to each element in the list
# lambda x: x * 2 means each element is multiplied by 2
# Result: [2, 4, 6, 8, 10, 12]
b = list(map(lambda x: x * 2, a))

# filter() selects elements based on a condition
# lambda x: x % 3 == 0 means keep numbers divisible by 3
# Result: [3, 6]
c = list(filter(lambda x: x % 3 == 0, a))

# Print results of map and filter
print(b)
print(c)

from functools import reduce

# reduce() applies a function cumulatively to the elements
# lambda x, y: x * y multiplies all elements together
# (((1*2)*3)*4)*5*6 = 720
result = reduce(lambda x, y: x * y, a)

# Print the final result
print(result)
