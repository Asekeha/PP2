# Shared variable for all instances
class Student:
    uni = "KBTU"
    def __init__(self, name):
        self.name = name

s1 = Student("Askar")
print(s1.uni)
print(s1.name)

# Variable to count total objects created
class Counter:
    total = 0
    def __init__(self):
        Counter.total += 1

c1 = Counter()
c2 = Counter()
print(Counter.total)

# Using a class variable as a constant
class Math:
    pi = 3.14
    def __init__(self, radius):
        self.radius = radius

circle = Math(5)
print(circle.pi * circle.radius)

# Shared tax rate for all items
class Item:
    tax = 0.12
    def __init__(self, price):
        self.price = price

phone = Item(500)
print(phone.price * phone.tax)

# Changing a class variable for everyone
class Theme:
    color = "white"

t1 = Theme()
Theme.color = "black"
print(t1.color)
