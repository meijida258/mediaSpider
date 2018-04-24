import sys
import os

PACKAGE_PARENT = '.'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pymongo import MongoClient
import time, datetime
import pandas, numpy
import os, csv, re
import matplotlib.pyplot as plt
from tools import get_datetime, get_timestamp, write_csv



def time_clock(func):
    def wrapper(*args, **kwargs):
        start_time = time.clock()
        result = func(*args, **kwargs)
        print(func.__name__)
        print(time.clock() - start_time)
        return result
    return wrapper
class M:
    @time_clock
    def a(self):
        time.sleep(1)

    @time_clock
    def b(self, t):
        if t:
            time.sleep(t)
        else:
            time.sleep(1)
m = M()
m.a()
m.b(None)


