#!/usr/bin/env python
import random
outputFile = "sample_input.txt"
r = random.Random()
r.seed()
neg = False

output = open(outputFile, 'w')

tags = ("A", "B", "C", "D", "E")

for i in range(0,99):
	for i in range(3):
		temp = r.uniform(0.0, 1000.0)
		if (neg):
			temp = str(temp * (1 + r.randint(0, 1) * -2))
		else:
			temp = str(temp)
		
			output.write("!"+tags[r.randint(0,4)]+":"+temp+";")
	output.write('\n')