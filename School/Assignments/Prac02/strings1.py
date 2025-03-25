#
# strings1.py : Read in a string and print it in reverse
#               using a loop and method call

instring = input("Enter a string: ")

# 2 upper, 3 dulicating code

# reversing w/ while loop
print(f'Reversed string is :', end='')
index = len(instring)-1
while index > -1:
	print(instring[index], end='')
	index=index-1
print()

# reversing with a for range loop
print('Reverse string is :', end='')
for index in range(len(instring)-1,-1,-1):
	print(instring[index],end='')
print()

# reversing with slicing
print('Reversed string is :', instring[::-1])
