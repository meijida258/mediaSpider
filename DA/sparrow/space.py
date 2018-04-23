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

df1 = pandas.DataFrame([['a', 122], ['b', 222]],
                   columns=['user_id', 'date'])

df3 = pandas.DataFrame([['c', 312], ['b', 123],['a', 222],['a', 333]],
                    columns=['user_id', 'date'])

df4 = pandas.DataFrame([['a'], ['b'],['d']], columns=['user_id'])
print(df4)
print(df3)
print(pandas.merge(df4, pandas.concat([df1, df3]), how='outer'))

