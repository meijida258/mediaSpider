import matplotlib, random, re, time
from pymongo import MongoClient
import xlwt

class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Slot
        self.collection  = self.db.PlayRecord

    def insert(self, data):
        self.collection.insert(data)

    def get_data(self):
        data = self.collection.find()
        return data

    def write_data(self, data):
        workbook = xlwt.Workbook
        worksheet = workbook.add_sheet('zhuanzhuanle')
        for each_record in data:
            worksheet.write(1, 0, each_record['reward_1'])
            worksheet.write(1, 1, each_record['reward_2'])
            worksheet.write(1, 2, each_record['reward_3'])
            worksheet.write(1, 3, each_record['noreward'])
            worksheet.write(1, 4, each_record['user_money'])
            worksheet.write(1, 5, each_record['chip'])
            worksheet.write(1, 6, each_record['total_award'])
            worksheet.write(1, 7, each_record['result'])
            worksheet.write(1, 8, each_record['reward_money'])
        workbook.save('yayaya.xls')
    def control(self):
        data = self.get_data()
        self.write_data(data)

class JackPot:
    def __init__(self):
        # 创建奖池
        self.base_award = 400000
        self.add_award = 0
        # 下注、选线
        self.chips = [10, 100, 1000]
        self.lines = [3, 5, 7, 9]
        # 返奖率及金额
        self.return_chip = 0.95
        self.add_award_percent = 0.04
        # 三个奖的概率
        self.reward_prob = {'reward_3':[0.01, 0.1], 'reward_2':[0.01, 0.13], 'reward_1':[0.01, 0.16]}
        self.reward_name = {'reward_3':'超级大奖！！！','reward_2':'特大奖！！','reward_1':'大奖！'}

        # 用户消费
        self.user_money = 0

    def auto_play(self):
        #下注
        current_play_chip = random.choice(self.chips)
        current_play_line = random.choice(self.lines)
        # 更新奖池
        self.add_award += current_play_chip * current_play_line * self.add_award_percent
        total_award = self.base_award + self.add_award
        # 更新用户消费
        self.user_money -= current_play_chip * current_play_line * (1 - self.return_chip)
        # 出奖
        reward_list = self.get_reward_list(current_play_chip, total_award) # 获得每一个奖的奖金
        reward_prob = self.get_reward_prob_list(reward_list, current_play_chip) # 每一个奖的概率
        print(reward_prob)
        reward = self.judge_reward(reward_prob, reward_list, total_award)

        try:
            reward_name = self.reward_name[re.findall(r'\'(.*?)\'',reward.__str__())[0]] # 奖名)
        except:
            reward_name = "没中奖"
        reward_money = re.findall(r'\: (.*?)\}',reward.__str__())[0] # 奖金
        # 打印结果
        print("用户本金: %s,下注筹码：%s，下注线数：%s，总奖池：%s，本次——%s，奖金%s" %(str(self.user_money), str(current_play_chip), str(current_play_line), total_award.__str__(), reward_name,reward_money))
        # 存到mongo db里面
        play_record = {}
        play_record['reward_1'] = reward_prob['reward_1']
        play_record['reward_2'] = reward_prob['reward_2']
        play_record['reward_3'] = reward_prob['reward_3']
        play_record['noreward'] = 1 - reward_prob['reward_1'] - reward_prob['reward_2'] - reward_prob['reward_3']
        play_record['user_money'] = self.user_money
        play_record['chip'] = current_play_chip * current_play_line
        play_record['total_award'] = total_award
        play_record['result'] = reward_name
        play_record['reward_money'] = reward_money
        mon.insert(play_record)

    def get_reward_list(self, current_play_chip, total_award):
        result = {}
        result['reward_1'] = 50000 * current_play_chip / 1000
        result['reward_2'] = total_award * 0.25 / 1000 * current_play_chip
        result['reward_3'] = total_award * 0.5 / 1000 * current_play_chip
        return result

    def get_reward_prob_list(self, reward_list, current_play_chip): # 把筹码传进来，调整不同筹码出奖的概率
        # 概率的字典
        result = {}
        # 先判断是否有概率出奖
        for each_reward in reward_list.keys():
            if reward_list[each_reward] > self.add_award:
                result[each_reward] = 0
            else:
                result[each_reward] = 1

        for each_reward in result.keys():
            if result[each_reward] == 1:
                reward_prob_area = self.reward_prob[each_reward]
                # 将出奖概率分成5段，对应累积奖池与奖金的比例
                if self.add_award / reward_list[each_reward] <= 20:
                    reward_multiple = self.add_award / reward_list[each_reward]
                else:
                    reward_multiple = 20
                reward_prob = (reward_prob_area[1] - reward_prob_area[0])/20 * reward_multiple + reward_prob_area[0] - (self.chips.index(current_play_chip) + 2)* 0.03/1000*current_play_chip # 根据奖金的累积与奖池
                result[each_reward] = reward_prob
        return result

    # 决定是否有奖,返回一个字典{'奖名'：'奖金'}
    def judge_reward(self, reward_prob, reward_list, total_award):
        # 将不中奖添加到reward_prob中
        total_reward_prob = 0
        for a in reward_prob.values():
            total_reward_prob += a
        if 1 - total_reward_prob > 0:
            reward_prob['NoReward'] = 1 - total_reward_prob
        else:
            reward_prob['NoReward'] = 0
        reward_list['NoReward'] = 0
        random_num = random.uniform(0, 1)
        start = 0
        for each_reward in reward_prob.keys():
            if start + reward_prob[each_reward] >= random_num >= start:
                # 奖池与用户的钱的变化
                self.add_award -= reward_list[each_reward]
                self.user_money += reward_list[each_reward]
                return {each_reward : reward_list[each_reward]}
            start += reward_prob[each_reward]

if __name__ == '__main__':
    jp = JackPot()
    mon = MongoSet()
    while True:
        jp.auto_play()
        time.sleep(0.3)