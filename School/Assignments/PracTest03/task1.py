# Student Name: Thomas Han
# Student ID:   22881119
#
# task1.py - add 4 more bees and made them yellow and title and label and also save as an image
#
# Version information: 1 
#
# Usage: python3 <title>.py
#
import matplotlib.pyplot as plt
import numpy as np
from buzzness import Bee

def plot_hive(hive, blist, ax):
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower") 
    ax.scatter(xvalues, yvalues, color="y")
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
hive = np.zeros((hiveX,hiveY))

#plt.ion()

for t in range(simlength):
    for b in blist:
        # b.step_change()
        pass
    fig, axes = plt.subplots(1, 1, figsize=(10,6))

    plot_hive(hive, blist, axes)
    #plot_hive(hive, blist, axes[0])
    
    plt.show()
    #plt.pause(1)
    #plt.clf()
 
fig.savefig("task1.png") 
