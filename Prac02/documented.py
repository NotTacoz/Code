#
# documented.py
#

import time # the time package

LINE_UP = '\033[1A' 
LINE_CLEAR = '\x1b[2K'

numlines = 4

eyes = ["\n< @ >  < @ > \n     db\n   \____/",
        "\n<@  >  <@  >\n     db\n   \____/",
        "\n<  @>  <  @>\n     db\n   \____/"]

for i in range(10): #loop 10 times
    if i % 2 == 0: #if the nth loop is an even loop
        print(eyes[0]) #animation 1 
    elif i % 4 == 1:
        print(eyes[1]) #if the nth loop leaves a remainder of 1 when dividedby 4 (1, 5, 9), print animation 2
    else: #all other scenarios
        print(eyes[2]) #print animation 3
    time.sleep(0.5) #delay for animation of 0.5 seconds
    for j in range(numlines): #go up one line, clear the line with teh predefine unicode, basically clearsall the lines for new animation.
        print(LINE_UP, end=LINE_CLEAR)
