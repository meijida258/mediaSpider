from operator import methodcaller
import inspect

def a_0():
    pass
class A:
    def a_0(self):
        print(1)

    def b_0(self):
        print(2)
def b_0():
    pass

def c_0():
    pass

m = [func for name, func in inspect.getmembers(A, inspect.isfunction)]
for i in m:
    att