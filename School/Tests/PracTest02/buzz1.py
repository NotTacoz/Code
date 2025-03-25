#
# Student ID   : 22881119
# Student Name : Thomas Han
#
# buzz0.py - plot trees for the bees
#
import numpy as np
import matplotlib.pyplot as plt

treeX = np.array([3,3,1,5])
treeY = np.array([1,5,3,3])

plt.scatter(treeX, treeY, color="green")
plt.scatter(3, 3, color="yellow", marker=",", s=50)

plt.title("Buzz1: Green trees")
plt.xlabel("x position")
plt.ylabel("y position")

plt.show()
