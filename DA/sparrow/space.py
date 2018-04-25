import sys
import os

PACKAGE_PARENT = '.'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
print(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from pymongo import MongoClient
import time, datetime
import pandas, numpy
import os, csv, re
import matplotlib.pyplot as plt
from tools import get_datetime, get_timestamp, write_csv
# from users_behaviors.users_consume import UserMoney

a = [[1, 2,3], [1,3,4]]
a_ = pandas.DataFrame(a, columns=['a', 'b', 'c'])
a_['d'] = 1
print(a_)

