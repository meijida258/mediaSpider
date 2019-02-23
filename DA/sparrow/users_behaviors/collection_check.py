import numpy as np
import pandas as pd

def get_data():
    data = pd.read_csv('lottery_data4_9.csv', index_col=0)
    task_data = data[['date', 'task_award', 'name']]
    task_data_date = pd.date_range(start='2018-04-01', end='2018-09-30', freq='D')
    print(task_data_date)

get_data()