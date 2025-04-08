# Student Name: Thomas Han
# Student ID:   22881119
#
# task2.py - add 4 more bees and made them yellow and title and label and also save as an image
#
# Version information: 1 
#
# Usage: python3 <title>.py
#
import matplotlib.pyplot as plt
import numpy as np
from buzzness import Bee

# 0: empty hexagon cells
# 1-5 increase amounts of honey
# 10 not ready for honey

def plot_hive(hive, blist, ax):
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower", cmap="YlOrBr")
    ax.scatter(xvalues, yvalues, color="y")
    # ax.bar(14, 25, width=3, bottom=-0.5)

    alt_y = []
    i = 0
    while i < 25:
        alt_y.append(i)
        i = i + 1.5

    # ax.scatter([14]*len(alt_y), alt_y, color="orange", marker='s', s=100)

    # plt.set_cmap('YlOrBr')

    ax.set_xlabel("X position")
    ax.set_title("Bee Hive")
    ax.set_ylabel("Y position")

simlength = 1
hiveX = 30
hiveY = 25
b1 = Bee("b1", (5,10))
blist = [b1]

blist.append(Bee("b2", (5,14))) 
blist.append(Bee("b3", (5,18))) 
blist.append(Bee("b4", (10,14))) 
blist.append(Bee("b5", (10,18))) 

# hive will range between 0 and 10
# 10 is brown, not ready
# 0 is ready
# 1-5 is honey level
hive = np.full((hiveX,hiveY),10)
print(hive)
print(len(hive))
for (j in range(25)):
    hive[13][j] = 1

#plt.ion()

for t in range(simlength):
    for b in blist:
        b.step_change()
    fig, axes = plt.subplots(1, 1, figsize=(10,6))

    plot_hive(hive, blist, axes)
    # plot_hive(hive, blist, axes[0])
    
    plt.show()
    #plt.pause(1)
    #plt.clf()
 
fig.savefig("task2.png") 
