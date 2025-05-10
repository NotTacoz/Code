# Student Name: Thomas Han
# Student ID:   22881119
#
# task4.py - bluh
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


def plot_world(world, blist, ax):
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(world.T, origin="lower", cmap="tab20")
    ax.scatter(xvalues, yvalues, color="y")

    hive_position = [22, 20]
    
    ax.scatter(hive_position[0], hive_position[1], s=400, color="white", marker='s' )

    ax.set_xlabel("X position")
    ax.set_title("Property")
    ax.set_ylabel("Y position")

simlength = 10
hiveX = 30
hiveY = 25
blist = []

blist.append(Bee("b1", (5,14)))
blist.append(Bee("b2", (10,14))) 
blist.append(Bee("b3", (5,10))) 


# hive will range between 0 and 10
# 10 is brown, not ready
# 0 is ready
# 1-5 is honey level
hive = np.full((hiveX,hiveY),10)
print(hive)
hive[13:16][0:25] = 1
for i in range(len(hive[14])):
    if i % 2 == 0:
        hive[14][i] = 5

plt.ion()

# wow! look its the property
propX=50
propY=40
world = np.full((propX,propY),5)
world[0][0] = 19
world[10:15,30:35]=14
world[30:40, 5:10] = 0
world[25:51:2, 20:40:2] = 12
world[25, 20] = 2
# world[20:24, 18:22] =15
world[2:10:2, 2:5] = 4

fig, axes = plt.subplots(1, 2, figsize=(10,6))

for t in range(simlength):
    for b in blist:
        b.step_change()
        
    
    plot_hive(hive, blist, axes[0])
    plot_world(world, blist[0:2], axes[1])
    fig.suptitle(f"BEE WORLD simlength={t}", size=48)
    
    fig.savefig("task4.png") 
    plt.show()
    plt.pause(0.2)
    axes[0].clear()
    axes[1].clear()

