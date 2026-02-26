import datetime

#1
today = datetime.date.today()
ago5 = datetime.timedelta(days=5)
print(today - ago5)

#2
today1 = datetime.date.today()
difference = datetime.timedelta(days=1)
yesterday = today1 - difference
tomorrow = today1 + difference

print(yesterday,today1,tomorrow)

#3 

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")
print(now)

#4

date1 = datetime.date(2007, 8, 2)
date2 = datetime.date(2007, 2, 18)

diff = (abs(date2 - date1)).total_seconds()
print(diff)
