#!/usr/bin/python3
import datetime
import random

f = open('data.txt', 'w')
for i in range(100):
    str = '{}_{}_{}'.format(random.randint(10000, 100000), random.randint(10000, 100000), random.randint(10000, 100000))
    f.write('{}\n'.format(str))
f.close()