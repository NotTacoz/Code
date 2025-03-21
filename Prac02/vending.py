#
# vending.py - vending machine
#

print("\n\033[95mWELCOME TO THE Snack VENDING MACHINE\n")

treats = [[1, "Choco Pie", 100, 5], [2, "Hello Panda", 50, 10], [3, "Fortune Cookie", 30, 10], [4, "Fig Roll", 30, 10], [5, "Maliban Orange Cream", 30, 10], [6, "Maliban Custard Cream", 30, 10], [7, "Maliban Chocolate Cream", 30, 10], [8, "Eccles Cake", 80, 5], [9, 'Wagon Wheel', 150, 0]]

treat = input('\n Would you like a tasty delicious snack? (Y/N)... ').upper()

#5, 25, 8, 8 + 3
print("Which treat would you like?")

def printSelection():
	Broke = f"+{53*'-'}+"
	print('\033[94m'+Broke)
	print(f"|  {'No':<3} | {'Name':<24} | ${'Price':<7} | {'Count':>6}|")
	print(Broke)
	for i in treats:
		num = i[0]
		nam = i[1]
		price = round(float(i[2]/100), 2)
		count = str(i[3])
	
		print(f"|  {num:<3} | {nam:<24} | ${price:<7} | {count:>6}|")

	print(Broke)


while treat != "N":
	printSelection()
	usel = int(input("Enter your selection: ")) -1

	if treats[usel][3] != 0:
		price = round(float(treats[usel][2]/100), 2)
		print(f"That will be : ${price}")
		treats[usel][3] = treats[usel][3] - 1
	else:
		print(f"\033[91mWE ARE ALL OUT OF {treats[usel][1]} ")
	
	treat = input('\n Would you like a tasty delicious snack? (Y/N)... ').upper()

print("GLAD TO BE OF SERVICE!")
