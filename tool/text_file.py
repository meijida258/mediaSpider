import re

with open('C:/Users\Administrator\Desktop/新建文本文档 (2).txt', 'r') as fl:
    content = fl.readlines()
    result = []
    for i in content:
        if re.findall(r'[a-z]', i):
            result.append(i)
    fl.close()

with open('C:/Users\Administrator\Desktop/lemon.txt', 'w') as fl1:
    for i in result:
        fl1.write(i + '\n')
    fl1.close()