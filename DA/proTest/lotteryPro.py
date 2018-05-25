import random, time

file_content = []
with open('proList.txt', 'r', encoding='utf-8') as pro_file:
    content = pro_file.readlines()
    for i in content:
        file_content.append(i.encode('utf-8').decode('utf-8-sig').strip().split('\t'))
    pro_file.close()

pro_list = [float(i[1]) for i in file_content]

pro_list.append(1-sum(pro_list))
pro_list_ = [i+sum(pro_list[:pro_list.index(i)]) for i in pro_list]

bet_list = [int(i[0]) for i in file_content]
bet_list.append(0)

run_time = 10000
per_count = 100

result = []

st = time.clock()
while run_time > 0:
    per_result = list()
    for rand in (random.uniform(0,1) for i in range(per_count)):
        pro_list_.append(rand)
        pro_list_ = sorted(pro_list_)
        per_result.append(bet_list[pro_list_.index(rand)])
        pro_list_.remove(rand)
    result.append(per_result)
    run_time -= 1

print(result)
print(time.clock() - st)