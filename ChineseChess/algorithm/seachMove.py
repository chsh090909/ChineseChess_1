#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  seachMove.py
@time:  2020/12/9 21:17
@title:
@content:
"""
from copy import deepcopy
from math import fabs
from algorithm.Timer import clock
from algorithm.moves import Moves, MoveNodes
from algorithm.scores import Scores
from algorithm.dataPercent import DataPercent
from loggerPrint import LoggerPrint

class SeachMove():
    def __init__(self, setting):
        self.setting = setting
        self.logg = LoggerPrint(self.setting).printLogToSystem(False)

    # 寻找AI的下一步走棋
    @clock
    def search_next_move(self, all_pieces, player1Color, depth=1):
        # 取得当前player2的所有走棋步骤内容
        all_moves = Moves(all_pieces, player1Color).generate_all_moves()
        #
        best_move = None
        # allmoves为空，表明要么无棋子可走（输了），要么打开的棋子上没有合适的棋子可走
        if len(all_moves) == 0:
            self.logg.info('当前的allmoves为None！！')
            # 获得双方剩余棋子的数量
            dp = DataPercent(all_pieces)
            red_count, black_count = dp.pieces_perc()
            # 根据剩余棋子数量判断是否为0
            if red_count == 0 or black_count == 0:
                self.logg.info(f"一方棋子数量为0，best_move为None！！")
            else:
                # 不为0还需判断是否有未打开棋子，如果当前还有棋子未打开，则打开循环到的第一个未打开的棋子
                box_to = None
                for key, value in all_pieces.items():
                    if value['state'] is False:
                        box_to = key
                        break
                # box_to不为空，将box_to传递给best_move
                if box_to is not None:
                    best_move = MoveNodes(None, box_to, '打开', None, box_to, None)
                    self.logg.info(f"打开循环到的第一个未打开的棋子best_move： {box_to}")
                # box_to为空，表示所有棋子都已打开而且没有合适棋子可走，玩家2自动认输
                else:
                    pass
        # allmoves不为空
        else:
            self.logg.info(f"当player1color为 [{player1Color}] 时， allmove的值：")
            for move in all_moves:
                # 基于当前的move计算下一步的走棋，并返回最高得分
                self.logg.info(
                    f"{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")
                move.score = self._seach_other_moves(all_pieces, player1Color, depth, move)
                self.logg.info(f"最终的score：{move.score}")
                # 把得分最高的走棋给best_move
                if best_move is None or move.score >= best_move.score:
                    best_move = move
        return best_move

    # 为下一个玩家寻找行棋内容
    def _seach_other_moves(self, all_pieces, player1Color, depth, move):
        # 设置一个all_pieces的替身，好还原all_pieces的值
        all_pieces_1 = deepcopy(all_pieces)
        # 根据行棋状态修改all_pieces_1的值
        if move.box_action == '吃棋':
            if move.box_res == 'box1=box2':
                all_pieces_1[move.box_from]['box_key'] = None
                all_pieces_1[move.box_from]['state'] = None
                all_pieces_1[move.box_to]['box_key'] = None
                all_pieces_1[move.box_to]['state'] = None
            elif move.box_res == 'success':
                all_pieces_1[move.box_to]['box_key'] = all_pieces_1[move.box_from]['box_key']
                all_pieces_1[move.box_to]['state'] = True
                all_pieces_1[move.box_from]['box_key'] = None
                all_pieces_1[move.box_from]['state'] = None
        elif move.box_action == '移动':
            all_pieces_1[move.box_to]['box_key'] = all_pieces_1[move.box_from]['box_key']
            all_pieces_1[move.box_to]['state'] = True
            all_pieces_1[move.box_from]['box_key'] = None
            all_pieces_1[move.box_from]['state'] = None
        elif move.box_action == '打开':
            # box_action == '打开' 时，不能给出打开这个棋子的信息，只能给出打开当前棋子的价值，同时将depth=0，给出得分
            depth = 0
        #
        if depth == 0:
            return move.score
        # depth不为0，更换player1Color的颜色方阵，反过来计算如果player1是player2的话，走棋都有哪些内容
        player1Color = 'black' if player1Color == 'red' else 'red'
        #
        score = 10
        moves = Moves(all_pieces_1, player1Color)
        all_moves = moves.generate_all_moves()
        self.logg.info(f"player2反置：当player1color为 [{player1Color}] 时， allmove的值：")
        for move_1 in all_moves:
            # 回调该函数自己，同时depth-1
            self.logg.info(
                f"player2反置：{move_1.box_name_from}===>>>{move_1.box_from}===>>>{move_1.box_action}===>>>"
                f"{move_1.box_name_to}===>>>{move_1.box_to}===>>>{move_1.box_res}===>>>{move_1.score}")
            score = max(score, self._seach_other_moves(all_pieces_1, player1Color, depth-1, move_1))
        if score >= 1000:
            score = 0
        move.score += score
        # 还原all_pieces的值，保证下一个循环用到的值还是原来的all_pieces
        all_pieces_1 = deepcopy(all_pieces)
        #
        return move.score

if __name__ == '__main__':
    all_pieces = {'box_0_0': {'box_key': None, 'state': None}, 'box_0_1': {'box_key': 'red_ju2', 'state': False}, 'box_0_2': {'box_key': 'black_xiang2', 'state': True}, 'box_0_3': {'box_key': 'black_zu1', 'state': False}, 'box_1_0': {'box_key': 'black_pao2', 'state': True}, 'box_1_1': {'box_key': 'black_zu5', 'state': False}, 'box_1_2': {'box_key': 'black_ma1', 'state': False}, 'box_1_3': {'box_key': 'red_ma2', 'state': False}, 'box_2_0': {'box_key': 'black_pao1', 'state': True}, 'box_2_1': {'box_key': 'red_pao1', 'state': False}, 'box_2_2': {'box_key': 'black_ma2', 'state': False}, 'box_2_3': {'box_key': 'black_ju2', 'state': False}, 'box_3_0': {'box_key': 'black_ju1', 'state': True}, 'box_3_1': {'box_key': 'red_jiang1', 'state': False}, 'box_3_2': {'box_key': 'black_xiang1', 'state': False}, 'box_3_3': {'box_key': 'black_jiang1', 'state': False}, 'box_4_0': {'box_key': 'red_ju1', 'state': True}, 'box_4_1': {'box_key': 'red_shi2', 'state': False}, 'box_4_2': {'box_key': 'red_pao2', 'state': False}, 'box_4_3': {'box_key': 'red_shi1', 'state': False}, 'box_5_0': {'box_key': 'red_zu2', 'state': False}, 'box_5_1': {'box_key': 'red_ma1', 'state': False}, 'box_5_2': {'box_key': 'red_xiang2', 'state': False}, 'box_5_3': {'box_key': 'black_zu2', 'state': False}, 'box_6_0': {'box_key': 'red_zu4', 'state': False}, 'box_6_1': {'box_key': 'black_shi2', 'state': False}, 'box_6_2': {'box_key': 'black_zu3', 'state': False}, 'box_6_3': {'box_key': 'red_zu5', 'state': False}, 'box_7_0': {'box_key': 'red_zu1', 'state': False}, 'box_7_1': {'box_key': 'red_zu3', 'state': False}, 'box_7_2': {'box_key': 'black_shi1', 'state': False}, 'box_7_3': {'box_key': 'black_zu4', 'state': False}}
    #
    from ChineseChess.settings import Settings
    sm = SeachMove(Settings())
    move = sm.search_next_move(all_pieces, 'black', depth=1)
    sm.logg.info(f"best_move:{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")
