import numpy as np
import pandas as pd
import os

def compare_data_check(func):
    def inner(data, p1, p2):
        if p1 == p2:return 1 # 自己和自己比较时，结果为1
        data = data[[p1, p2]]
        data = data[(data[p1] > 0) & (data[p2] > 0)] # 过滤掉两个有米有都评论的项
        if data.shape[0] == 0: return 0 # 剩下的都评论过的项==0时，直接返回0
        result = func(data, p1, p2)
        return result
    return inner

@ compare_data_check
def sim_distance(data, p1,p2):
    dis = np.linalg.norm(data[p1] - data[p2])
    sim = 1/(1+dis)
    return sim

@ compare_data_check
def sim_vectorAngle(data, p1,p2):
    vectorAngle = data[p1].dot(data[p2])/(np.linalg.norm(data[p1]) * np.linalg.norm(data[p2]))
    sim = 0.5 + 0.5 * vectorAngle
    return sim

@ compare_data_check
def sim_pearson(data, p1,p2):
    match_matrix = np.corrcoef(data[p1],data[p2])
    sim = match_matrix[0,1]
    # print('{}和{}相似度：{}'.format(p1, p2, sim))
    return sim

def sim_tanimoto(array1,array2):
    num = (array1 * array2).sum()
    sim = num / (np.linalg.norm(array1) + np.linalg.norm(array2) - num)
    return sim

def top_matches(data, target, sim_method=sim_pearson,n=5): # 通过列数据，算出相关系数
    total_sim = [(sim_method(data,target, other), other) for other in data.columns if other != target]
    total_sim.sort()
    total_sim.reverse()
    return total_sim[:n]


def get_recommendations_user_based(data, target):
    data = data.T # 将数据集翻转
    total_sim = top_matches(data, target, n=data.shape[1],sim_method=sim_pearson)
    sim_person = np.array([i[1] for i in total_sim])
    simulates = [i[0] for i in total_sim]
    simulates = np.array([i if i > 0 else 0 for i in simulates])
    target_unwatched_mov = data[data[target] == 0].index
    sim_data = data.loc[target_unwatched_mov, sim_person].T
    # # 加权计算时的权重之和
    sim_sum = (sim_data/sim_data).fillna(0)
    sim_sum = sim_sum * np.hstack([simulates.reshape(len(simulates),1)] * sim_sum.shape[1])
    # 加权值的和
    total_sum = sim_data * np.hstack([simulates.reshape(len(simulates),1)] * sim_sum.shape[1])
    recommend_result_data = total_sum.sum()/sim_sum.sum()
    recommend_result = [(score, mov) for score, mov in zip(recommend_result_data.values, recommend_result_data.index) if score > 0]
    recommend_result.sort()
    recommend_result.reverse()
    return recommend_result[:5]

def cal_item_simulate(data, sim_method=sim_pearson):
    # 先生成一个全是1的标准矩阵
    ones = np.ones((data.shape[1], data.shape[1]))
    items = data.columns
    data_size = data.shape
    for i1 in range(data_size[1] - 1):
        for i2 in range(i1, data_size[1]):
            sim = sim_method(data, items[i1], items[i2])
            ones[i1, i2] = ones[i2,i1] = sim
    item_simulate = pd.DataFrame(data=ones, columns=items, index=items)
    return item_simulate


def get_recommendations_item_based(data, target):
    if not os.path.exists('ml-latest-small/item_simulate.csv'):
        print('没有比较数据集，开始生成...')
        item_simulate_data = cal_item_simulate(data)
        print('比较数据生成完成。')
        item_simulate_data.to_csv('ml-latest-small/item_simulate.csv')
    else:
        # 物品相似度的列表
        print('读取比较数据集')
        item_simulate_data = pd.read_csv('ml-latest-small/item_simulate.csv', index_col=0)
    #  target看过的和评分
    target_watched_data = data.loc[target,:][data.loc[target,:] > 0]
    target_watched_mov = target_watched_data.index
    target_watched_mov_score = target_watched_data.values
    target_watched_mov_size = len(target_watched_mov_score)
    # target没看过的
    target_unwatched_mov = data.loc[target,:][data.loc[target,:] == 0].index
    target_unwatched_mov_size = len(target_unwatched_mov)
    # 将没看过的列标签留下，看过的行标签留下
    target_item_simulate_data = item_simulate_data.loc[target_watched_mov, target_unwatched_mov]
    target_item_simulate_data.to_csv('ml-latest-small/item_simulate_target.csv')
    # 乘以评分前求一次相似度的和，用于加权计算时用做除数
    sum_target_item_simulate = target_item_simulate_data.sum()
    # 将相似度 的矩阵与评分矩阵相乘
    target_item_simulate_data_rid_score = target_item_simulate_data * np.hstack([target_watched_mov_score.reshape(target_watched_mov_size,1)] * target_unwatched_mov_size)
    # 然后再列求和，用做加权计算的被除数
    sum_target_item_score_simulate = target_item_simulate_data_rid_score.sum()

    # 求加权平均值
    average_weight_sim = sum_target_item_score_simulate / sum_target_item_simulate
    average_weight_sim_result = [(recommend_score, mov) for mov, recommend_score in zip(average_weight_sim.index, average_weight_sim.values) if recommend_score > 0]
    average_weight_sim_result.sort()
    average_weight_sim_result.reverse()
    return average_weight_sim_result[:5]

def transform_data(data):
    return data.T

def load_movie_lens():
    movies = pd.read_csv('ml-latest-small/movies.csv')[['movieId', 'title']]
    ratings = pd.read_csv('ml-latest-small/ratings.csv')[['movieId', 'userId','rating']]
    movie_ratings = ratings.merge(movies, on=['movieId']).drop(['movieId'],axis=1)
    total_users = list(set(movie_ratings.userId))
    total_movies = list(set(movie_ratings.title))
    print('总共评价的有{}人，{}部电影'.format(len(total_users), len(total_movies)))
    transformed_data = []
    for user in total_users:
        user_filter_data = movie_ratings[movie_ratings['userId']==user]
        user_eval = {mov:rat for mov, rat in zip(user_filter_data.title,user_filter_data.rating)}
        transformed_data.append(user_eval)
    movie_ratings_ = pd.DataFrame(data=transformed_data, index=total_users, columns=total_movies)
    movie_ratings_ = movie_ratings_.fillna(0)
    movie_ratings_.to_csv('ml-latest-small/movie_ratings.csv')

data = pd.read_csv('ml-latest-small/movie_ratings.csv', index_col=0)
print('基于用户的过滤结果:{}'.format(get_recommendations_user_based(data, 1)))
print('基于物品的过滤结果:{}'.format(get_recommendations_item_based(data, 1)))
# critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
#         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
#         'The Night Listener': 3.0},
#         'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
#         'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
#         'You, Me and Dupree': 3.5},
#         'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
#         'Superman Returns': 3.5, 'The Night Listener': 4.0},
#         'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
#         'The Night Listener': 4.5, 'Superman Returns': 4.0,
#         'You, Me and Dupree': 2.5},
#         'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
#         'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
#         'You, Me and Dupree': 2.0},
#         'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
#         'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
#         'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}
# data = pd.DataFrame(critics).fillna(0).T
str()