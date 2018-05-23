import random

file_content = []
with open('proList.txt', 'r', encoding='utf-8') as pro_file:
    content = pro_file.readlines()
    for i in content:
        file_content.append(i.encode('utf-8').decode('utf-8-sig').strip().split('\t'))
    pro_file.close()

pro_list = [i[1] for i in file_content]
pro_list.append(1-sum(pro_list))
bet_list = [i[0] for i in file_content]
bet_list.append(0)

run_times = 10000
per_count = 100

while run_times > 0:
