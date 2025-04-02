#
# conversions.py – module with functions to convert between units #
# fahr2cel : Convert from Fahrenheit to Celsius.
#
def fahr2cel(fahr):
    """Convert from Fahrenheit to Celsius. Argument:
    fahr – the temperature in Fahrenheit """
    celsius = (fahr - 32) * (5/9) 
    return celsius

def fahr2kel(fahr):
    return ((fahr - 32) * 5/9 + 273.15)

def cel2fahr(cel):
    return ((cel * 9/5) + 32)

def cel2kel(cel):
    return ((cel + 273.15))

def kel2cel(kel):
    return (kel - 273.15)

def kel2fahr(kel):
    return ((kel - 273.15) * (9/5) + 32)

def main():
    print("Hi! Thanks for running my file directly, however I am meant to be ran with other code like ./converter2.py! :-)")

if __name__ == '__main__':
    main()
