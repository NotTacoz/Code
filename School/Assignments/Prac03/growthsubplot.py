#
# growthsubplot.py - wow growth
#
import matplotlib.pyplot as plt
import numpy as np

print("\nSIMULATION - Unconstrained Growth\n")
length=100
population=100
growth_rate=0.1
time_step=0.5
num_iter = length/time_step
growth_step = growth_rate * time_step
print("initial VALUES:\n")
print("simu length (hours): ", length)
print("ini pop: ", population)
print("growth rate (/hr): ", growth_rate)
print("time step (part hour per step): ", time_step)
print("num iterations (sim length * time step per hour): ", num_iter)
print("growth step (growth rate epr time step: ", growth_step)
print("\nRESULTS:\n")
print("time: ", 0, " \tGrowth: ", 0, " \tPopulation: ", 100)

time_array = np.zeros(int(num_iter) +1)
population_array = np.zeros(int(num_iter) +1)

for i in range(1, int(num_iter) + 1):
    growth = growth_step * population
    population = population + growth
    time = i * time_step
    time_array[i] = (time)
    population_array[i] = (population)
    print("Time: ", time, " \tGrowth: ", growth, "\tPopulation: ", population)
print("\nCOMPLETe.\n")

print(time, "\n", population_array)

plt.subplot(211)
plt.plot(time_array, population_array, '--') 
plt.xlabel("time (hours)")
plt.ylabel("population (n of people)")
plt.title("Prac 3.1: Unconstrained Growth")

plt.subplot(212)
plt.plot(time_array, population_array, 'ro') 
plt.xlabel("time (hours)")
plt.ylabel("population (n of people)")
plt.title("Prac 3.1: Unconstrained Growth")
plt.show()
