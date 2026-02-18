#a function with one argument
def my_function(fname): # fname is a parameter
  print(fname + " Refsnes")

my_function("Emil") # "Emil" is an argument
my_function("Tobias")
my_function("Linus")

#Default Parameter Values
def my_function(name = "friend"):
  print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")
#using functions with lists
fruits = my_function()
print(fruits[0])
print(fruits[1])
print(fruits[2])
#To specify that a function can have only keyword arguments, add *, before the arguments:
def my_function(*, name):
  print("Hello", name)

my_function(name = "Emil")
