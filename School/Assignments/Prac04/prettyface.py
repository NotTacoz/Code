#
# prettyface.py
#
import matplotlib.pyplot as plt 
import scipy.datasets

face = scipy.datasets.face(gray=True) 
plt.imshow(face)
plt.imshow(face, cmap=plt.cm.gray) 
plt.show()
