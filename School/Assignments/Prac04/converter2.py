from conversions import *
import sys

print("Welcome to the converter machine we will convert your numbers for a price of $0.00!")


tho = ""
while True:
    tho = input("What would you like convert? C-F (C), C-K (R), K-C (K), K-F (P), F-C (F), F-K (L) or Exit (X)\n")

    if tho.upper() == "X":
        break

    bum_list = []
    bum = ""
    while (bum.upper() != "C"):
        bum = input("Enter values or continue (C): ")
        if bum.isdigit():
            bum_list.append(int(bum))


    if tho.upper() == "C":
        for i in bum_list:
            print(cel2fahr(i))
    elif tho.upper() == "R":
        for i in bum_list:
            print(cel2kel(i))
    elif tho.upper() == "K":
        for i in bum_list:
            print(kel2cel(i))
    elif tho.upper() == "P":
        for i in bum_list:
            print(kel2fahr(i))
    elif tho.upper() == "F":
        for i in bum_list:
            print(fahr2cel(i))
    elif tho.upper() == "L":
        for i in bum_list:
            print(fahr2kel(i))

print("Thanks for using our service!")
