#!/usr/bin/env python
import random
outputFile = "sample_input.txt"
r = random.Random()
r.seed()

output = open(outputFile, 'w')

tags = ("PRE1", "ACL1", "TEM1", "TEM2", "TEM3")

for i in range(0,99):
	temp = r.uniform(0.0, 1000.0)
	temp = str(temp)[:9]
	for i in range(3):
		output.write("!"+tags[r.randint(0,4)]+":"+temp+";")
	output.write('\n')