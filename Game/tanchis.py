# -*- coding: UTF-8 -*-

import pygame, sys, random
import math, time
from operator import itemgetter

width = 300
length = 200
FPS = 15
pygame.init()

total_step = 0

fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((width, length), 0, 32)

pygame.display.set_caption('TCS')

# 加载头和身体的资源

head = pygame.image.load('resource/head.png')
body = pygame.image.load('resource/body.png')
tail = pygame.image.load('resource/tail.png')
apple_img = pygame.image.load('resource/mq1.png')
ONE_STEP = 20

total_snake = [head, body, tail]
total_pos = [(40,0),(20,0),(0,0)]
temp_total_pos = total_pos[:]
direction = "right"
apple = False
apple_pos = set()
temp_apple_pos = set()

def auto_move(new_direction=None,eat=False):
    global total_pos, virtual_total_pos
    if not new_direction:
        new_direction = direction
    total_pos = calculate_pos(new_direction, eat)
    virtual_total_pos = total_pos

def calculate_pos(direction, eat):
    global total_pos
    if direction == "right":
        if not eat:
            total_pos.pop()
        result = [(total_pos[0][0] + ONE_STEP, total_pos[0][1])] + total_pos
    elif direction == 'left':
        if not eat:
            total_pos.pop()
        result = [(total_pos[0][0] - ONE_STEP, total_pos[0][1])] + total_pos
    elif direction == 'up':
        if not eat:
            total_pos.pop()
        result = [(total_pos[0][0], total_pos[0][1] - ONE_STEP)] + total_pos
    elif direction == 'down':
        if not eat:
            total_pos.pop()
        result = [(total_pos[0][0], total_pos[0][1] + ONE_STEP)] + total_pos
    return result

def random_apple(total_pos): # 随机刷新苹果
    while True:
        x = random.randint(0, (width-ONE_STEP)/20)*20
        y = random.randint(0, (length-ONE_STEP)/20)*20
        # (x, y) = (random.randint(0, (width-ONE_STEP)/20)*20, 0)
        result = True
        for i in total_pos:
            if (x, y) == i:
                result = False
        if result:
            return (x, y)
        else:
            pass

def apple_appear_1st():# 第一次刷新苹果
    global screen, apple_pos, temp_apple_pos
    apple_pos = (80, 0)
    temp_apple_pos = (apple_pos[0], apple_pos[1])
    screen.blit(apple_img, (apple_pos[0], apple_pos[1]))
    print('画苹果--' + str(apple_pos))
    return

def eat_apple(total_pos, apple_pos):
    if total_pos[0] == apple_pos:
        return True
    else:
        return False

def is_dead(total_pos):
    # 判断是否碰壁
    if total_pos[0][0] > (width-ONE_STEP) or total_pos[0][1] > (length-ONE_STEP) or total_pos[0][1] < 0 or total_pos[0][0] < 0:
        return True
    # 判断是否吃到尾巴
    for i in total_pos[1:]:
        if i == total_pos[0]:
            return True
    return False

# 列出某个点周围的点， 去掉可能不能走的点

def find_target_around_safe_pos(test_pos, total_pos, from_pos=()):
    # global total_pos
    head_around_pos = [(test_pos[0] - ONE_STEP, test_pos[1]), (test_pos[0] + ONE_STEP, test_pos[1]),
                       (test_pos[0], test_pos[1] - ONE_STEP), (test_pos[0], test_pos[1] + ONE_STEP)]
    test_around_safe_pos = []
    for i in head_around_pos:
        # 检验蛇头周围每个可能可以走的点 i
        if (width-ONE_STEP) >= i[0] >= 0 and (length-ONE_STEP) >= i[1] >= 0:# 优先排除界面之外的点
            # 再判断蛇身的每一个点，看是否会撞到身体
            test_around_safe_pos.append(i) # 先把测试点加进去
            if total_pos[1:-1].count(i):
                test_around_safe_pos.remove(i)
            # for body in total_pos[1:-1]:
            #     if body == i:
            #         test_around_safe_pos.remove(i)# 遇到和身体一样的点，就删除
    for i in test_around_safe_pos:
        if i == from_pos:
            test_around_safe_pos.remove(i)
    return test_around_safe_pos # 返回可以走的点

def calculate_distance(pos1, pos2):
    dis = math.sqrt(pow(pos1[0]-pos2[0],2) + pow(pos1[1]-pos2[1], 2))
    return dis


def bfs(total_pos, target_pos):
    set_1 = set()
    step = -1
    set_1.add(total_pos[0]) # 初始点集合
    walked_pos_list = [] # 走过的点集合
    find_target = False
    can_walk_set = set()
    path = []
    final_step = []
    while not find_target:
        path_dict = {}
        for each_start_pos in set_1: # 遍历起始点，找下一步的点
            walked_pos_list.append(each_start_pos) # 保存访问过的点
            try:
                from_pos = find_from_pos(path[step], each_start_pos)
            except:
                from_pos = ()
            can_walk_pos = find_target_around_safe_pos(each_start_pos, total_pos, from_pos=from_pos)

            for each_can_walk_pos in can_walk_pos:
                if walked_pos_list.count(each_can_walk_pos) == 0: # 访问过的点不在访问
                    can_walk_set.add(each_can_walk_pos) # 记录下一步的点作为set_1
                    path_dict[each_can_walk_pos] = each_start_pos
                if each_can_walk_pos == target_pos:
                    if each_can_walk_pos in path_dict:
                        final_step.append(each_start_pos)
                    else:
                        path_dict[each_can_walk_pos] = each_start_pos
                    find_target = True
            if path.count(path_dict) == 0:
                path.append(path_dict)
        if find_target:
            break
        set_1.clear()
        set_1 = can_walk_set.copy()
        can_walk_set.clear()
        if not set_1:
            return False
        step += 1
    return {'path':path, 'final_step':final_step}

def find_from_pos(from_pos_dict, now_pos):
    for i in from_pos_dict.items():
        if now_pos == i[0]:
            return i[1]

def find_way(path_dict, target_pos):
    path = path_dict['path']
    final_step = path_dict['final_step']
    result = []
    for each_final_step in final_step:
        temp_path = path[:]
        temp_result = []
        temp_path[-1][target_pos] = each_final_step
        for i in temp_path[-1].items():
            if i[0] == target_pos:
                temp_result.append([i[0]])
                temp_result.append([i[1]])
        temp_path.pop(-1)
        for each_step in temp_path[::-1]:
            step = []
            for i in each_step.items():
                if temp_result[-1].count(i[0]) == 1:
                    step.append(i[1])
            temp_result.append(step)
        result.append(temp_result[:])
    return result

def AI_direction_set(total_pos, next_pos):
    if total_pos[0][0] - next_pos[0] == ONE_STEP:
        return 'left'
    elif next_pos[0] - total_pos[0][0] == ONE_STEP:
        return 'right'
    elif next_pos[1] - total_pos[0][1] == ONE_STEP:
        return 'down'
    elif total_pos[0][1] - next_pos[1] == ONE_STEP:
        return 'up'

def draw_reseau():# 画网格
    global screen
    color = (100,255,200)
    line_width = 1
    for i in range(1, int(length/20)):
        pygame.draw.line(screen, color, (0, i*20), (width, i*20), line_width)
    for i in range(1, int(width/20)):
        pygame.draw.line(screen, color, (i*20, 0), (i*20, length), line_width)

# def find_path_target(total_pos, target_pos):
#     # global total_pos
#     # 以给定的点找路
#     final_path_list = bfs(total_pos, target_pos)
#     # print(final_path_list)
#     if final_path_list:
#         return find_way(final_path_list, target_pos)
#         # return final_path
#     else:
#         print('bfs找不到从%s到%s的路' %(str(total_pos[0]), str(target_pos)))
#         return False

def find_path_main(total_pos, target_pos):
    bfs_result = bfs(total_pos, target_pos)
    if bfs_result:
        return find_way(bfs_result, target_pos)
    else:
        return bfs_result

def find_tail_longest_path(total_pos, target_pos):
    around_safe_pos = find_target_around_safe_pos(total_pos[0], total_pos)
    # 找出最远距离的走法
    result = []
    for safe_pos in around_safe_pos:
        result.append([calculate_distance(safe_pos, target_pos), safe_pos])
    if result:
        return sorted(result, key=itemgetter(0), reverse=True)
    else:
        return False



def auto_move_main(): # 真实行走
    global apple_pos, total_pos, total_snake
    weiba_pos = total_pos[-1]
    auto_move(direction)
    if eat_apple(total_pos, apple_pos):  # 吃到苹果
        total_pos.append(weiba_pos)  # 加尾巴坐标
        total_snake.append(tail)  # 加尾巴图片
        total_snake[-2] = body  # 替换原有尾巴
        # 吃了苹果， 立马随机一个
        apple_pos = random_apple(total_pos)
        print('吃苹果')
    # 画新苹果
    screen.blit(apple_img, (apple_pos[0], apple_pos[1]))


def auto_move_virtual(next_step): # 虚拟蛇按照路线虚拟行走
    global temp_apple_pos, temp_total_pos
    temp_total_pos.insert(0, next_step)
    if next_step != temp_apple_pos:
        temp_total_pos.pop()
        return False
    else:
        return True


def virtual_main(final_path): # 得到最终的行走路径
    global temp_apple_pos, temp_total_pos
    print('虚拟运行第一次得到的路线')
    temp_total_pos = total_pos[:]
    final_path.pop()
    for each_step in final_path[::-1]:
        auto_move_virtual(each_step[0]) # 虚拟行走
        # 得到最后的虚拟位置, 同时是否吃掉苹果
    print('当前虚拟位置：%s' % (str(temp_total_pos)))
    temp_final_path = find_path_main(temp_total_pos, temp_total_pos[-1])  # 再bfs一次，看是否可以得到路线
    if temp_final_path:
        return True
    else:
        return False

def virtual_tail_move(final_path):
    global temp_apple_pos, temp_total_pos
    temp_total_pos = total_pos[:]
    auto_move_virtual(final_path)
    print('当前虚拟位置：%s' % (str(temp_total_pos)))
    temp_final_path = find_path_main(temp_total_pos, temp_total_pos[-1])
    if temp_final_path:
        return True
    else:
        return False

def find_final_path_2():
    print('先找去苹果的路')

def find_final_path():
    print('先找去苹果的路')
    # 直接找安全的最短路径
    find_apple_result = find_path_main(total_pos, apple_pos)
    print(find_apple_result)
    # 找到后虚拟运行，吃完苹果后是否安全
    if find_apple_result:
        print('找到去苹果的路，虚拟运行看是否安全')
        for i in find_apple_result:
            if virtual_main(i):
                return i[-1][0]
    print('没有去苹果的路，或吃了苹果不安全，找去尾巴的路')
    # 找下一步离尾巴最远的距离，并判断走了之后，是否安全
    find_tail_result = find_tail_longest_path(total_pos, total_pos[-1])
    print(find_tail_result)
    if find_tail_result:
        print('找到去尾巴的路，并选走最远路径的路')
        if len(find_tail_result) == 1:
            return find_tail_result[0][1]
        for i in find_tail_result:
            if virtual_tail_move(i[1]):
                return i[1]
        print('没有去尾巴的路， 随机走一步安全的，并虚拟运行看看')
        next_step_list = find_target_around_safe_pos(total_pos[0], total_pos)
        for each_next_step in next_step_list:
            temp_total_pos.insert(0, each_next_step)
            temp_total_pos.pop()
            if find_path_main(temp_total_pos, temp_total_pos[-1]):
                return each_next_step
            else:
                return (total_pos[0][0], total_pos[0][1] + 20)

    else:
        print('没有去尾巴的路， 随机走一步安全的，并虚拟运行看看')
        next_step_list = find_target_around_safe_pos(total_pos[0], total_pos)
        for each_next_step in next_step_list:
            temp_total_pos.insert(0, each_next_step)
            temp_total_pos.pop()
            if find_path_main(temp_total_pos, temp_total_pos[-1]):
                return each_next_step
            else:
                return (total_pos[0][0], total_pos[0][1] + 20)

while True:
    temp_total_pos.clear()
    temp_total_pos = total_pos[:]
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # 随机刷新苹果
    if not apple:
        apple_appear_1st()
        apple = True

    # 先找一次路，以苹果为目标，有到苹果的路，返回结果;
    # 没有到苹果的路，以尾巴为目标，返回结果;
    final_path = find_final_path()
    print(final_path)
    temp_apple_pos = (apple_pos[0], apple_pos[1])
    print('最终确定路线：' + str( total_pos[0]) + '---->' + str(final_path) + '身体：' + str(total_pos[1]) + '苹果：' + str(apple_pos) + '尾巴：' + str(total_pos[-1]))
    direction = AI_direction_set(total_pos, final_path)

    # 移动/判断是否吃到苹果
    weiba_pos = total_pos[-1]
    auto_move(direction)
    if eat_apple(total_pos, apple_pos):# 吃到苹果
        total_pos.append(weiba_pos) # 加尾巴坐标
        total_snake.append(tail) # 加尾巴图片
        total_snake[-2] = body  # 替换原有尾巴
        #吃了苹果， 立马随机一个
        apple_pos = random_apple(total_pos)
    # 画新苹果
    screen.blit(apple_img, (apple_pos[0], apple_pos[1]))
    # pygame.draw.rect(screen, (255, 0, 0), (apple_pos[0], apple_pos[1], 20, 20))
    total_step += 1
    print('当前实际位置：%s' %(str(total_pos)))
    print('蛇长：%s，运行了%s步' % (str(len(total_pos)),str(total_step)))
    print('------------------------------------------------')
    # 判断是否死亡
    dead = is_dead(total_pos)
    if not dead:
        for i in range(0, len(total_snake)):
            screen.blit(total_snake[i], (total_pos[i][0]+1, total_pos[i][1]+1))
    else:
        pygame.quit()
        sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)