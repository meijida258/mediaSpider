# -*- coding: UTF-8 -*-
from PIL import Image

a = Image.open('C:/Users/Administrator/Desktop/连杀音效/14.jpg')
b = Image.open('C:/Users/Administrator/Desktop/连杀音效/13.jpg')
a_, b_ = a.histogram(), b.histogram()
# result = math.sqrt(reduce(operator.add,  list(map(lambda a,b: (a-b)**2, h1, h2)))/len(h1))
# (lambda a,b: (a-b)**2, h1, h2)
h1 = 2
h2 = 3
c = lambda a, b:(a-b)**2, h1, h2
print(c)