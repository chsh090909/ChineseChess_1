#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  dataPercent.py
@time:  2020/9/25 14:50
@title:
@content: 对棋子的数量、棋子的价值以及整个棋局评分
"""

class DataPercent():
    def __init__(self, all_pieces):
        self.all_pieces = all_pieces

    # 棋子的数量计算百分比
    def pieces_perc(self):
        red_num, black_num = 0, 0
        for _, piece in self.all_pieces.items():
            if piece['box_key'] is not None:
                box_color, box_name = piece['box_key'].split('_')
                if box_color == 'red':
                    red_num += 1
                else:
                    black_num += 1
        # print(f"red_num : {red_num}, black_num : {black_num}")
        # red_percent = red_num / 16
        # black_percent = black_num / 16
        return (red_num, black_num)

    # 计算棋子的价值比例
    def piece_value(self):
        piece_value_dict = {}
        # 定义各个棋子能吃多少个棋子
        eat_dict = {'jiang': 9, 'shi': 15, 'xiang': 13, 'ma': 11, 'ju': 9, 'pao': 16, 'zu': 1}
        # 定义各个棋子能被多少个棋子吃掉
        eated_dict = {'jiang': 8, 'shi': 5, 'xiang': 7, 'ma': 9, 'ju': 11, 'pao': 10, 'zu': 15}
        #
        for _, piece in self.all_pieces.items():
            if piece['box_key'] is not None:
                box_name = piece['box_key'].split('_')[-1]
                box_name = box_name[:-1]
        #
        return piece_value_dict


if __name__ == '__main__':
    all_pieces = {'box_0_0': {'box_key': 'black_pao2', 'state': True},
                  'box_0_1': {'box_key': 'black_xiang2', 'state': True},
                  'box_0_2': {'box_key': None, 'state': None},
                  'box_0_3': {'box_key': 'black_zu3', 'state': True},
                  'box_1_0': {'box_key': 'black_shi1', 'state': True},
                  'box_1_1': {'box_key': None, 'state': None},
                  'box_1_2': {'box_key': None, 'state': None},
                  'box_1_3': {'box_key': None, 'state': None},
                  'box_2_0': {'box_key': None, 'state': None},
                  'box_2_1': {'box_key': None, 'state': None},
                  'box_2_2': {'box_key': None, 'state': None},
                  'box_2_3': {'box_key': 'black_xiang1', 'state': True},
                  'box_3_0': {'box_key': None, 'state': None},
                  'box_3_1': {'box_key': None, 'state': None},
                  'box_3_2': {'box_key': 'red_ju1', 'state': True},
                  'box_3_3': {'box_key': None, 'state': None},
                  'box_4_0': {'box_key': None, 'state': None},
                  'box_4_1': {'box_key': 'black_ma2', 'state': True},
                  'box_4_2': {'box_key': None, 'state': None},
                  'box_4_3': {'box_key': 'black_zu4', 'state': True},
                  'box_5_0': {'box_key': 'black_zu1', 'state': True},
                  'box_5_1': {'box_key': 'black_ju2', 'state': True},
                  'box_5_2': {'box_key': 'red_xiang1', 'state': True},
                  'box_5_3': {'box_key': 'black_pao1', 'state': True},
                  'box_6_0': {'box_key': 'black_ma1', 'state': True},
                  'box_6_1': {'box_key': 'black_ju1', 'state': False},
                  'box_6_2': {'box_key': None, 'state': None},
                  'box_6_3': {'box_key': None, 'state': None},
                  'box_7_0': {'box_key': 'red_ma1', 'state': False},
                  'box_7_1': {'box_key': 'red_ju2', 'state': True},
                  'box_7_2': {'box_key': 'red_zu2', 'state': False},
                  'box_7_3': {'box_key': 'red_zu5', 'state': True}
                  }
    dp = DataPercent(all_pieces)
    print(dp.pieces_perc())
