#!/usr/bin/env python

import math

spacing = 1  # m
lines = []
numStrings = 32
ledsPerString = 50
ledSpacing = 0.1

for string in range(0, numStrings):
    angle = 2*3.14 / numStrings * string
    for led in range(0, ledsPerString):
        y = math.sin(angle) * led*ledSpacing
        x = math.cos(angle) * led*ledSpacing
        lines.append('  {"point": [%.2f, %.2f, 0.00]}' %
                     (x, y))
print '[\n' + ',\n'.join(lines) + '\n]'
