#1

def sq(n):
    for i in range(n+1):
        yield i*i
n = int(input())
for i in sq(n):
    print(i)

#2
def even(x):
    for i in range(x+1):
        if i % 2 == 0:
            yield i

x = int(input())
nums = []
for i in even(x):
    nums.append(i)
for i in range(len(nums)-1):
    print(nums[i],end=',')
print(nums[len(nums)-1])

#3
def div(a):
    for i in range(a+1):
        if i % 12 == 0:
            yield i

a = int(input())
for i in div(a):
    print(i)

#4
def squares(a,b):
    for i in range(a,b+1):
        yield i*i
a1 = int(input())
b1 = int(input())
for i in squares(a1,b1):
    print(i,end=' ')

#5
def count_down(c):
    while c >= 0:
        yield c
        c-=1
c = int(input())
for i in count_down(c):
    print(i)

#6
def pri(n):
    while n >= 0:
        yield n
        n -= 1
    
n = int(input())
first = True
for i in pri(n):
    if not first:
        print(",", end = "")
    print(i, end = "")
    first = False
