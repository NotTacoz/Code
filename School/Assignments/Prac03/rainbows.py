import matplotlib.pyplot as plt
import math
import numpy as np

# func 1: -x^2 + 40
# func 2: -x^2 + 35
# func 3: -x^2 + 30
# func 4: -x^2 + 25
# func 5: -x^2 + 20

arr1 = (np.zeros(80))
arr2 = (np.zeros(80))
arr3 = (np.zeros(80))
arr4 = (np.zeros(80))
arr5 = (np.zeros(80))
arr6 = (np.zeros(80))
arr7 = (np.zeros(80))


print(arr1, arr2)

for i in range(-40, 40):
    b = 40
    for j in range(1, 8):
        print(i)
        var_name = f"arr{j}"
        try:
            (globals()[var_name])[(i+40)] = math.sqrt(-(i)**2 + b**2)            
        except:
            (globals()[var_name])[(i+40)] = -50
        b = b - 5

plt.xlim(-40,40)
plt.ylim(0,40)
print(arr1, arr2)
print(arr1, arr2, arr3)
pp = range(-40, 40)
plt.plot(pp, arr1, color="red")
plt.plot(pp, arr2, color="orange")
plt.plot(pp, arr3, color="y")
plt.plot(pp, arr4, color="green")
plt.plot(pp, arr5, color="blue")
plt.plot(pp, arr6, color="indigo")
plt.plot(pp, arr7, color="violet")

plt.scatter(pp, arr1, color="r")
plt.scatter(pp, arr2, color="orange")
plt.scatter(pp, arr3, color="y")
plt.scatter(pp, arr4, color="g")
plt.scatter(pp, arr5, color="b")
plt.scatter(pp, arr6, color="indigo")
plt.scatter(pp, arr7, color="violet")


plt.show()
