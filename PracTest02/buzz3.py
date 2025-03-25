#
# Student ID   : 22881119
# Student Name : Thomas Han
#
# buzz2.py - plot trees for the bees
#
import numpy as np
import matplotlib.pyplot as plt

nTrees = int(input("Please enter the desired number of trees (5-20): "))

while 5 > nTrees or nTrees > 20:
    if nTrees:
        print("\nPlease input a number from 5-20\n")
    nTrees = int(input("Please enter the desired number of trees (5-20): "))
    print("HI")


treeX = np.array(np.random.uniform(low=1, high=5,size=(nTrees)))
treeY = np.array(np.random.uniform(low=1, high=5, size=(nTrees)))

plt.scatter(treeX, treeY, color="green")
plt.scatter(3, 3, color="yellow", marker=",", s=100) # bee at center of graph (3,3) 

plt.title(f"Buzz3: {nTrees} 20 floaty random trees")
plt.xlabel("x position")
plt.ylabel("y position")

plt.xlim(0, 6)
plt.ylim(0, 6)

plt.show()
