#
# Student ID   : 22881119
# Student Name : Thomas Han
#
# buzz2.py - plot trees for the bees
#
import numpy as np
import matplotlib.pyplot as plt

treeX = np.array(np.random.randint(low=1, high=5,size=(10)))
treeY = np.array(np.random.randint(low=1, high=5, size=(10)))

plt.scatter(treeX, treeY, color="green")
plt.scatter(3, 3, color="yellow", marker=",", s=100)

plt.title("Buzz2: Ten random trees")
plt.xlabel("x position")
plt.ylabel("y position")

plt.xlim(0, 6)
plt.ylim(0, 6)

plt.show()
