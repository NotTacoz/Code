#
# Student ID   : 22881119
# Student Name : Thomas Han
#
# buzz4.py - plot trees for the bees
#

# importing packages
import numpy as np
import math
import matplotlib.pyplot as plt

nTrees = int(input("Please enter the desired number of trees (5-20): ")) # initial input

while 5 > nTrees or nTrees > 20: # loop until value is within range (or a non int is inputted, which breaks the code)
    if nTrees:
        print("\nPlease input a number from 5-20\n")
    nTrees = int(input("Please enter the desired number of trees (5-20): "))


treeX = np.array(np.random.uniform(low=1, high=5,size=(nTrees)))
treeY = np.array(np.random.uniform(low=1, high=5, size=(nTrees)))

fig, (ax1, ax2) = plt.subplots(1, 2)

# fig code
fig.suptitle("Floaty trees and distances")
fig.set_size_inches(10, 5) # 10in x 5in graph so things are overlayed ontop of each other

# ax1 code
ax1.scatter(treeX, treeY, color="green")
ax1.scatter(3, 3, color="yellow", marker=",", s=100)

ax1.title.set_text(f"Buzz3: {nTrees} floaty random trees")
ax1.set_xlabel("x position") # changing label to 'x position'
ax1.set_ylabel("y position") # changing label to 'y position'

ax1.set_xlim(0, 6)
ax1.set_ylim(0, 6)

distance = []
# now this the the chart
for i in range(nTrees): # loop for finding distance for every point from bee at (3,3)
    valueX = treeX[i] # x coordinate of the ith value
    valueY = treeY[i] # y coordinate of the ith value point
    
    distance.append(math.sqrt((valueX-3)**2+(valueY-3)**2))  # finding the distance between (3,3) and the point (x,y) for a given i

ax2.title.set_text(f"distance to {nTrees} trees")
ax2.set_ylabel("Distance") #label..
ax2.bar(range(nTrees), distance, color="yellow", edgecolor="black", hatch="*") # creating the bar graph

plt.show() #show our graph
