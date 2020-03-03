import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

import pickle
import random

df = pd.read_csv('final.csv')

def cosine_similarity(data_name):
    from sklearn.metrics.pairwise import cosine_distances
    similarity = 1 - cosine_distances(data_name)    # sklearn은 정의와 반대이므로 1에서 빼준다.
    return similarity


def evaluation(neigh_num):
    from sklearn.metrics import mean_squared_error

    neigh_num = neigh_num
    rmse = 0
    user_num_list = list(df['name'].unique())

    for user_num in user_num_list:
        cal = Calculation_rating(user_num, neigh_num)
        predict_list = cal.predict_rating()
        original_list = cal.original_rating()
        rmse_onebyone = mean_squared_error(original_list, predict_list)

        rmse += rmse_onebyone

    rmse = rmse / len(user_num_list)

    return print('이웃의 수가 {}일때, MSE 값은 {}입니다.'.format(neigh_num - 1, rmse))


class Basic(object):

    def __init__(self, user_num, neigh_num):
        self.user_num = user_num
        self.neigh_num = neigh_num

    """유저의 이름이 들어오면 유저 번호로 변환"""


    """target 유저와 유사한 유저 K명을 찾고, cosine 유사도를 이용하여 거리를 구한다"""

    def find_near_neighbor(self):

        from sklearn.neighbors import NearestNeighbors

        user_num = self

        KNN = NearestNeighbors(n_neighbors=self.neigh_num, metric='cosine')  # n_neighbors에는 본인이 포함되기 때문에 +1을 해준다.
        KNN.fit(df)  # data set은 utility matrix인 df를 사용
        similar_distance, similar_users = KNN.kneighbors(df)

        similars = {}  # 유사한 유저와 거리를 dict형식으로 저장

        # 유사한 유저
        similar_users = similar_users[user_num][1:]
        similars['sim_users'] = list(similar_users)

        # 유사한 유저들과의 거리
        similar_distance = similar_distance[user_num][1:]
        similars['sim_distance'] = similar_distance

        return similars

    """target유저 + 유사한 유저 K명으로 이루어진 새로운 data frame 형성하고, narray 형식으로 반환"""

    def near_neighbors_narray(self):

        similars = Basic.find_near_neighbor(self)
        similiar_users_list = similars['sim_users']
        similiar_distances = similars['sim_distance']

        columns = list(df.columns)
        new_df = pd.DataFrame(columns=columns)

        for i in range(len(similiar_users_list)):
            def concat_row(i):
                neighbor_df = df[df['name'] == similiar_users_list[i]]
                return neighbor_df

            neighbor_df = pd.concat([new_df, concat_row(i)])
            new_df = neighbor_df

        narray = new_df.values
        narray = narray[:, 1:]

        return narray


class Calculation_rating(Basic):

    def __init__(self, user_num, neigh_num):
        Basic.__init__(self, user_num, neigh_num)

    """가중평균 값으로 아이템에 대한 target 유저의 평점을 예측"""

    def predict_rating(self):

        narray = Basic.near_neighbors_narray(self)  # narray 받음
        similars = Basic.find_near_neighbor(self)

        similiar_distances = similars['sim_distance']

        rating_list = []  # 가중평균값을 담는 리스트

        # 범위 0 ~ K-1
        for col_num in range(narray.shape[1]):

            sum = 0
            rating = 0
            for i in range(1, len(narray[:, col_num])):
                sum += float(narray[:, col_num][i]) * float(similiar_distances[i])
            rating = sum / similiar_distances.sum()

            # if rating < 0:
            #     rating = 0  # 만약 가중평균값이 0보다 작으면 0점으로 함
            # elif rating > 10:
            #     rating = 10  # 만약 가중평균값이 10보다 크면 10점으로 함
            # else:
            #     rating = int(rating)  # 평점은 정수형

            rating_list.append(rating)

        return rating_list

    """target 유저의 평점을 리스트로 변환하는 함수"""

    def original_rating(self):

        user_num = self

        # target 유저의 평점을 narray로 변환
        target_df = df[df['name'] == user_num]
        target_narray = target_df.values
        target_narray = target_narray[:, 1:]  # user column 삭제

        # narray로 변환된 target 유저의 평점을 리스트로 변환
        target_user_rating_list = []
        for i in range(target_narray.shape[1]):
            raw_rating = int(target_narray[0][i])
            target_user_rating_list.append(raw_rating)

        return target_user_rating_list


class UBCF(Calculation_rating):

    def __init__(self, user_num, neigh_num):
        Basic.__init__(self, user_num, neigh_num)
        Calculation_rating.__init__(self, user_num, neigh_num)

    def recommen_movie_list(self):

        user_num = self
        predict_list = Calculation_rating.predict_rating(self)
        original_list = Calculation_rating.original_rating(self)
        all_movie_list = list(df.columns)[1:]  # 전체 영화 리스트

        """
        target 유저가 이미 평가했던 영화 외의 영화를 추천받기 위해
        target 유저의 평점이 0이면, 가중평균값을 넣고 그렇지 않으면 0을 넣는다
        """
        temp_list = []
        for i in range(len(predict_list)):
            if int(original_list[i]) != 0:
                temp_list.append(0)
            else:
                temp_list.append(int(predict_list[i]))

        # 4점 이상인 영화들만 선택하여 index를 추천 리스트에 담는다.
        recommen_list_index = []
        for i in range(len(temp_list)):
            if temp_list[i] >= 5:
                recommen_list_index.append(i)

        # recommen_list_index로 부터 영화 제목을 str로 저장
        recommen_list_str = []
        for i in recommen_list_index:
            recommen_list_str.append(all_movie_list[i])

        """전체 영화 리스트에서 target 유저가 이미 평가한 영화를 제거"""
        already_rating_movie_num = [i for i in range(len(temp_list)) if temp_list[i] == 0]
        user_movie_list = [all_movie_list[i] for i in range(len(all_movie_list)) if i not in already_rating_movie_num]

        final_dict = {}
        final_dict['by_rating'] = recommen_list_str
        final_dict['by_delete'] = user_movie_list

        return final_dict

    """영화 추천 실행 함수"""

    def recommendation(self):

        user_number = self
        movie_dict = UBCF.recommen_movie_list(self)

        by_rating_list = movie_dict['by_rating']
        by_delete_list = movie_dict['by_delete']

        # 만약 추천 리스트가 3개 이상이라면 가중평균 리스트에서 3편의 영화를 추천리스트에서 추천
        # 그렇지 않으면 유저가 이미 평가했던 영화를 제외한 영화 리스트에서 추천
        if len(by_rating_list) >= 3:
            recommendation_selection = random.sample(by_rating_list, 3)
        else:
            if len(by_delete_list) >= 3:
                recommendation_selection = random.sample(by_delete_list, 3)
            else:
                recommendation_selection = random.sample(by_delete_list, 1)

          # user number를 user의 아이디로 변경

        print('{}님을 위한 추천 영화 입니다.'.format(user_number))
        return print(recommendation_selection)


neigh_num = [6, 8, 11]    # 이웃의 수가 5명, 7명, 10명이 됨
for num in neigh_num:
    evaluation(num)