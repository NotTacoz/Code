from conversions import *

print("Welcome to the converter machine we will convert your numbers for a price of $0.00!")

tho = ""
while (tho.upper() != "X"):
    tho = input(("What would you like convert? C-F (C), C-K (R), K-C (K), K-F (P), F-C (F), F-K (L) or Exit (X)\n"))
    if tho.upper() == "C":
        print(cel2fahr(int(input(("Celsius? ")))))
    elif tho.upper() == "R":
        print(cel2kel(int(input(("Celsius? ")))))
    elif tho.upper() == "K":
        print(kel2cel(int(input(("Kelvin? ")))))
    elif tho.upper() == "P":
        print(kel2fahr(int(input(("Kelvin? ")))))
    elif tho.upper() == "F":
        print(fahr2cel(int(input(("Fahrenheit? ")))))
    elif tho.upper() == "L":
        print(fahr2kel(int(input(("Fahrenheit? ")))))

print("Thanks for using our service!")
