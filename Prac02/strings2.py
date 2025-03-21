#
# strings2.py : Read in a string and print it in forwards
#               using a loop and method call

instring = 2*(input("Enter a string: ")).upper()

# 2 upper, 3 dulicating code																			
# start:0, step: 2, end: len(index)
index = 0
print(f'the string [every 2nd] :', end='')
while index < (len(instring)):
	print(instring[index], end='')
	index=index+2
print()

# reversing with a for range loop
lenthstr = len(instring)
print(f'the string [every 2nd] :', end='')
for index in range(0,lenthstr,2):
	print(instring[index],end='')
print()

# reversing with slicing
print('the string [every 2nd] :', instring[0:len(instring):2])
