import time, datetime
import numpy, re, pandas, csv
import matplotlib.pyplot as plt

# time_today = time.time()
# st_year, st_month, st_day = int(time.strftime('%Y', time.localtime(time_today-86400*8))), int(time.strftime('%m', time.localtime(time_today-86400*8))), int(time.strftime('%d', time.localtime(time_today-86400*8)))
# end_year, end_month, end_day = int(time.strftime('%Y', time.localtime(time_today-86400))), int(time.strftime('%m', time.localtime(time_today-86400))), int(time.strftime('%d', time.localtime(time_today-86400)))
# save_date = time.strftime('%Y-%m-%d', time.localtime(time_today-86400))

# 最大最小奖
min_time, max_time = 10, 500
reward_list = [2, 6, 10, 20, 50, 100, 500]
fix_array = [1,2,3,4,5,4,3]
all_reward_list = reward_list[:]
all_reward_list.append(0)
reward_times = numpy.array(reward_list)

# 每隔10倍一个奖，总共奖数，0倍不算
reward_count = len(reward_list)
# 返奖率
total_reward_pro = 0.4
# print(reward_pro)
# print('中奖率：%s' % str(sum(reward_pro)))
# print('中奖频率：%s' % str(1/sum(reward_pro)))

def get_reward_pro_list():
    # 每个奖的返奖率
    reward_pro = total_reward_pro * len(reward_list)*numpy.array(fix_array)/(numpy.ones(len(reward_list))*sum(fix_array))/reward_list
    list1 = list(reward_pro)
    result = []
    for i in range(1, len(list1)+1):
        result.append(sum(list1[:i]))
    return result

def run(times):
    result = []
    count = 0
    while count < times:
        count += 1
        random_num = numpy.random.rand()
        reward_pro_list = get_reward_pro_list()
        reward_pro_list.append(random_num)
        reward_pro_list.sort()
        reward_index = reward_pro_list.index(random_num)
        result.append(all_reward_list[reward_index])
    return result

def count_reward(result):
    rewards = []
    for i in reward_list:
        rewards.append(result.count(i))
    rewards.append(len(result)-sum(rewards))
    return rewards

def draw(result, times):
    fig = plt.figure()
    fig.suptitle('模拟%s次'%str(times))

def write_csv(result):
    head = ['2倍', '6倍', '10倍', '20倍', '50倍', '100倍', '500倍', '0倍']
    with open('C:/Users\Administrator\Desktop/1.csv', 'w', newline='', encoding='utf-8') as fl:
        writer = csv.writer(fl, dialect='excel')
        writer.writerow(head)
        for each_data in result:
            writer.writerow(each_data)
    fl.close()
if __name__ == '__main__':
    all_rewards = []
    for i in range(0, 100):
        times = 10
        result = run(times)
        all_rewards.append(count_reward(result))
    write_csv(all_rewards)
    get_reward_pro_list()
