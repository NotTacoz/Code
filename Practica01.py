n = input("Enter your name ") # creating the variable n, which is set as the user inputted name wow

print(f"\nWelcome to Practical Test 01 {n}\n")

#inputs
l = int(input("Enter lower bound: "))
u = int(input("Enter upper bound: "))
step_size = int(input("Enter step size: "))

i = u # start at highest value
while i >= l: # loop until the thingy is lower than lowest value
	if (i % 6 == 0 or i % 7 == 0):
		print(i) #print the number if remainer is 0 when divided by 6 or 7
	i = i - step_size # decrease by desired step size


print("\ngood luck for college") # good luck

