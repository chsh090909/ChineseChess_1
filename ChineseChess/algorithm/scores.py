#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  scores.py
@time:  2020/6/15 17:33
@title:
@content: 各棋子的价值以及棋子位置的价值得分
"""
class Scores():
    '''
    得分规则：
        1、吃棋得分为千位分数；
        2、棋子自身价值为百位分数；
        3、打开特殊棋子位置得分为十位分数（50，60，70，80）；
        4、打开一个棋子得分为10分；
        5、替换位得分为个位得分，是棋子自身价值得分/10000而来，便于区分打开棋子或移动棋子的不同得分来判断棋子的优先级；
    '''
    @staticmethod
    def piece_score(piece_name):
        # 棋子的自身价值得分为百位分数
        piece_score_dict = {
            'jiang': 900,
            'shi': 800,
            'xiang': 700,
            'ma': 400,
            'ju': 300,
            'pao': 600,
            'zu': 500,
            'zu_no_jiang': 200,
        }
        return piece_score_dict[piece_name]

    @staticmethod
    def eat_score(key):
        # 吃棋得分为千位分数
        eat_score_dict = {
            'jiang_jiang': 1000,
            'zu_jiang': 9000,
            'pao_jiang': 9000,
            'shi_shi': 1000,
            'jiang_shi': 8000,
            'pao_shi': 8000,
            'xiang_xiang': 1000,
            'jiang_xiang': 7000,
            'shi_xiang': 7000,
            'pao_xiang': 7000,
            'ma_ma': 1000,
            'jiang_ma': 4000,
            'shi_ma': 4000,
            'xiang_ma': 4000,
            'pao_ma': 4000,
            'ju_ju': 1000,
            'jiang_ju': 3000,
            'shi_ju': 3000,
            'xiang_ju': 3000,
            'ma_ju': 3000,
            'pao_ju': 3000,
            'pao_pao': 6000,
            'shi_pao': 6000,
            'xiang_pao': 6000,
            'ma_pao': 6000,
            'ju_pao': 6000,
            'zu_zu': 5000,
            'shi_zu': 5000,
            'xiang_zu': 5000,
            'ma_zu': 5000,
            'ju_zu': 5000,
            'pao_zu': 5000,
            'zu_zu_no_jiang': 2000,
            'shi_zu_no_jiang': 2000,
            'xiang_zu_no_jiang': 2000,
            'ma_zu_no_jiang': 2000,
            'ju_zu_no_jiang': 2000,
            'pao_zu_no_jiang': 2000,
        }
        return eat_score_dict[key]

    @staticmethod
    def other_pieces_score(key):
        # 棋盘特殊棋子位置得分十位分数
        other_score_dict = {
            'zu_ju': 20,
            'zu_pao': 22,
            'pao_jiang': 23,
            'pao_ju': 21
        }
        return other_score_dict[key]

