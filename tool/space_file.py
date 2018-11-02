from collections import abc
import json
import itertools
import copy
b = ()
a = list(range(10))
for i in range(10):
    i_ = i
    b = itertools.chain(b, ({'num':a[i_]} for m in range(1)))
    if i == 4:
        print(list(b))
print(list(b))