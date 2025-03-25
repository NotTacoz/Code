#
# numbersarray.py: Read ten numbers give sum, min, max & mean 
#
import numpy as np
import matplotlib.pyplot as plt

numarray = np.zeros(10)   # create an empty 10 element array 

print('Enter ten numbers...')

for i in range(len(numarray)):
    print('Enter a number (', i, ')...')
    numarray[i] = int(input())

max = numarray.max() 
min = numarray.min()

print('max and min is: ', max, min) 

print('average is: ', numarray.sum()/10)

plt.plot(range(10), numarray, '--')

plt.title("Plot of numbers you have entered")

plt.show()
