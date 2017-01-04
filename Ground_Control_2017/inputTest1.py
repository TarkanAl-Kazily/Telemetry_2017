import time
inputFile = "input.txt"

accl = 0.0
tempA = 32.0
tempB = 32.0
tempC = 32.0
press = 1.0

for i in range(0,50):
    startTime = time.time()
    
    if i < 2:
        accl = accl
    elif (i < 20):
        accl = 15
        tempA += 35.4
        tempB += 12.8
        tempC += 35.8
        press -= 0.03
    else:
        accl =  -9.8
        tempA -= 8.3
        tempB -= 8.3
        tempC -= 8.3
        press += 0.03

    file = open(inputFile, "w")
    file.write(str(round(accl, 1)) + "\n" + str(round(tempA, 1)) + "\n" + str(round(tempB, 1)) + "\n" + str(round(tempC, 1)) + "\n" + str(round(press, 1)) + "\n")
    file.close
    print(i)

    while time.time() - startTime < 0.5:
        time.sleep(0.01)

file = open(inputFile, "w")
file.write(str(0.0) + "\n" + str(32.0) + "\n" + str(32.0) + "\n" + str(32.0) + "\n" + str(1.0) + "\n")
file.close
