import random
import copy, time
import pandas as pd
import numpy as np
import tqdm

source_pro = [0.00038,0.00159,0.00297,0.0053,0.00795,0.0106,0.06627]
# m = [4, 20, 50, 103, 183, 289, 952] #0.88
m = np.array(source_pro).cumsum()

# m = [4, 20, 50, 104, 184, 291, 961] #0.89
# m = [4, 19, 48, 99, 176, 278, 918] #0.85
q = [500,100,50,20,10,6,2,0]
p = 10

def get():
    raw_data = 10000
    km = 0
    log = {}
    while raw_data > p:
        m1 = list(copy.copy(m))
        raw_data -= p
        # randi = random.randint(0, 9999)
        randi = random.random()
        m1.append(randi)
        s_m1 = sorted(m1)
        if randi in m:
            bet = q[s_m1.index(randi) + 1]
        else:
            bet = q[s_m1.index(randi)]
        get_data = bet* p
        raw_data += get_data
        km += p*0.1
        log[bet] = log.setdefault(bet, 0) + 1
    log['re'] = km
    return km


df_data = {}
for i in range(10):
    result = []
    for ti in tqdm.tqdm(range(1000)):
        log = get()
        result.append(log)
    df_data['re_{}'.format(i)] = result[:]
df = pd.DataFrame(df_data)
try:
    df.to_csv('lottery_data/ll.csv')
except:
    df.to_csv('lottery_data/ll{}.csv'.format(random.randint(10000)))

