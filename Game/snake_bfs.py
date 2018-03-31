Width = 300
Length = 200
ONE_STEP = 20

total_pos = [(40,0),(20,0),(0,0)]
target_pos = (260, 160)

def find_target_around_safe_pos(test_pos, total_pos, from_pos=()):
    head_around_pos = [(test_pos[0] - ONE_STEP, test_pos[1]), (test_pos[0] + ONE_STEP, test_pos[1]),
                       (test_pos[0], test_pos[1] - ONE_STEP), (test_pos[0], test_pos[1] + ONE_STEP)]
    for i in head_around_pos:
        # 检验蛇头周围每个可能可以走的点 i
        if (Width-ONE_STEP) < i[0] or i[0] < 0 or (Length-ONE_STEP) < i[1] or i[1] < 0:# 优先排除界面之外的点
            head_around_pos.remove(i)
        if total_pos[1:-1].count(i) == 1:
            head_around_pos.remove(i)
        if from_pos and i == from_pos:
            head_around_pos.remove(i)
    return head_around_pos

def get_from_pos(step, )

def find_way(total_pos, target_pos):
    start_pos_list = [total_pos[0]]
    walked_pos_list = []
    step = -1
    find_target_pos = False
    next_step_list = []
    while not find_target_pos:
        for start_pos in start_pos_list:
            walked_pos_list.append(start_pos)

            try:
                from_pos =
            current_step = [] # 这一步可以走的列表，记录起点和下一步
            around_safe_pos = find_target_around_safe_pos(start_pos, total_pos)
            for each_safe_pos in around_safe_pos: # 所有下一步放入列表，等待再次循环
                current_step.append([start_pos, each_safe_pos])
                if next_step_list.count(each_safe_pos) == 0:
                    next_step_list.append(each_safe_pos)
