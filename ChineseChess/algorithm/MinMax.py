#!/usr/bin/python3
# encoding: utf-8

from random import randint
from copy import deepcopy
from ChineseChess.algorithm.Timer import clock
from ChineseChess.algorithm.moves import Moves, MoveNodes
from ChineseChess.algorithm.scores import Scores
from ChineseChess.algorithm.dataPercent import DataPercent
from ChineseChess.loggerPrint import LoggerPrint
from ChineseChess.settings import Settings

logg = LoggerPrint(Settings()).printLogToSystem(False)

class MinMax():
    @staticmethod
    @clock
    def search_next_move(all_pieces, player1Color, depth=1):
        # 取得当前player2的所有走棋步骤内容
        moves = Moves(all_pieces, player1Color)
        all_moves = moves.generate_all_moves()
        # 定义极大极小值
        best_move = None
        is_max = False
        alpha = -100000000000
        beta = 100000000000
        # allmoves为空，表明要么无棋子可走（输了），要么打开的棋子上没有合适的棋子可走
        if len(all_moves) == 0:
            logg.info('当前的allmoves为None！！')
            # 获得双方剩余棋子的数量
            dp = DataPercent(all_pieces)
            red_count, black_count = dp.pieces_perc()
            # 根据剩余棋子数量判断是否为0
            if red_count == 0 or black_count == 0:
                logg.info(f"一方棋子数量为0，best_move为None！！")
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
                    logg.info(f"打开循环到的第一个未打开的棋子best_move： {box_to}")
                # box_to为空，表示所有棋子都已打开而且没有合适棋子可走，玩家2自动认输
                else:
                    pass
        else:
            logg.info(f"当player1color为 [{player1Color}] 时， allmove的值：")
            for move in all_moves:
                # 基于当前的move计算下一步的走棋，并返回最高得分
                move.score = MinMax._min_max(depth, alpha, beta, all_pieces, player1Color, move, is_max)
                logg.info(f"{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")
                # 把得分最高的走棋给best_move
                if best_move is None or move.score >= best_move.score:
                    best_move = move
        return best_move

    @staticmethod
    def _min_max(depth, alpha, beta, all_pieces, player1Color, move, is_max):
        # 设置一个all_pieces的替身，好还原all_pieces的值
        all_pieces_1 = deepcopy(all_pieces)
        # 取得吃棋的得分
        if move.box_action == '吃棋':
            box_from_color = move.box_name_from.split('_')[0]
            box_name_from = move.box_name_from.split('_')[-1]
            box_name_from = box_name_from[:-1]
            box_name_to = move.box_name_to.split('_')[-1]
            box_name_to = box_name_to[:-1]
            #
            if move.box_res in ['jiang_zu', 'box1<box2']:
                # box1的棋子正在受到box2棋子的威胁，需要消灭box2或者避开box2
                # move.score -= Scores.eat_score(f"{box_name_to}_{box_name_from}")
                pass
            else:
                # 更新all_pieces_1的值，传入下一个循环中计算下一步走棋
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
                # 对吃zu有特殊的判断：基于jiang是否存在，来判断吃对方zu的得分
                moves = Moves(all_pieces, player1Color)
                score = moves.get_score_for_zu_by_jiang(box_from_color, box_name_from, box_name_to)
                move.score += score
            # 吃棋的得分加上下一步的得分
            # move.score += MinMax._min_max(depth-1, alpha, beta, all_pieces_1, player1Color, move, is_max)
        elif move.box_action == '移动':
            all_pieces_1[move.box_to]['box_key'] = all_pieces_1[move.box_from]['box_key']
            all_pieces_1[move.box_to]['state'] = True
            all_pieces_1[move.box_from]['box_key'] = None
            all_pieces_1[move.box_from]['state'] = None
        elif move.box_action == '打开':
            # box_action == '打开' 时，不能给出打开这个棋子的信息，只能给出打开当前棋子的价值（计算它周围的威胁值），同时将depth=0，给出得分
            depth = 0
        #
        if depth == 0:
            if move.box_action == '吃棋':
                if move.box_res in ['box1=box2', 'success']:
                    box_name_from = move.box_name_from.split('_')[1]
                    box_name_from = box_name_from[:-1]
                    box_name_to = move.box_name_to.split('_')[1]
                    box_name_to = box_name_to[:-1]
                    move.score += Scores.eat_score(f"{box_name_from}_{box_name_to}")
                else:
                    pass
            return move.score
        # 更换player1Color的颜色方阵，反过来计算如果player1是player2的话，走棋都有哪些内容
        player1Color = 'black' if player1Color == 'red' else 'red'
        #
        moves = Moves(all_pieces_1, player1Color)
        all_moves = moves.generate_all_moves()
        for move_1 in all_moves:
            if is_max:
                alpha = max(alpha, MinMax._min_max(depth-1, alpha, beta, all_pieces, player1Color, move_1, False))
                alpha += move.score
            else:
                beta = min(beta, MinMax._min_max(depth-1, alpha, beta, all_pieces, player1Color, move_1, True))
                beta += move.score
        # 还原all_pieces的值，保证下一个循环用到的值还是原来的all_pieces
        all_pieces_1 = deepcopy(all_pieces)
        return alpha if is_max else beta


if __name__ == '__main__':
    # zu追着jiang跑的问题
    # all_pieces = {'box_0_0': {'box_key': None, 'state': None},
    #                 'box_0_1': {'box_key': 'red_shi2', 'state': False},
    #                 'box_0_2': {'box_key': None, 'state': None},
    #                 'box_0_3': {'box_key': 'black_jiang1', 'state': False},
    #                 'box_1_0': {'box_key': 'red_ma2', 'state': True},
    #                 'box_1_1': {'box_key': None, 'state': None},
    #                 'box_1_2': {'box_key': None, 'state': None},
    #                 'box_1_3': {'box_key': 'red_jiang1', 'state': True},
    #                 'box_2_0': {'box_key': 'red_zu3', 'state': False},
    #                 'box_2_1': {'box_key': None, 'state': None},
    #                 'box_2_2': {'box_key': 'black_zu1', 'state': True},
    #                 'box_2_3': {'box_key': None, 'state': None},
    #                 'box_3_0': {'box_key': 'black_xiang2', 'state': False},
    #                 'box_3_1': {'box_key': None, 'state': None},
    #                 'box_3_2': {'box_key': None, 'state': None},
    #                 'box_3_3': {'box_key': None, 'state': None},
    #                 'box_4_0': {'box_key': 'red_ju1', 'state': False},
    #                 'box_4_1': {'box_key': 'red_zu2', 'state': True},
    #                 'box_4_2': {'box_key': None, 'state': None},
    #                 'box_4_3': {'box_key': None, 'state': None},
    #                 'box_5_0': {'box_key': 'black_ma2', 'state': False},
    #                 'box_5_1': {'box_key': None, 'state': None},
    #                 'box_5_2': {'box_key': None, 'state': None},
    #                 'box_5_3': {'box_key': None, 'state': None},
    #                 'box_6_0': {'box_key': 'black_shi1', 'state': False},
    #                 'box_6_1': {'box_key': 'black_zu3', 'state': False},
    #                 'box_6_2': {'box_key': 'red_zu5', 'state': False},
    #                 'box_6_3': {'box_key': 'red_pao1', 'state': False},
    #                 'box_7_0': {'box_key': 'black_zu4', 'state': False},
    #                 'box_7_1': {'box_key': 'black_pao1', 'state': False},
    #                 'box_7_2': {'box_key': 'black_ju2', 'state': False},
    #                 'box_7_3': {'box_key': 'red_pao2', 'state': False}}
    a = 1
    # 无合适打开的棋子，但实际上还有棋子未打开，而best move为none的问题：
    # all_pieces = {'box_0_0': {'box_key': None, 'state': None},
    #                 'box_0_1': {'box_key': None, 'state': None},
    #                 'box_0_2': {'box_key': None, 'state': None},
    #                 'box_0_3': {'box_key': None, 'state': None},
    #                 'box_1_0': {'box_key': None, 'state': None},
    #                 'box_1_1': {'box_key': None, 'state': None},
    #                 'box_1_2': {'box_key': None, 'state': None},
    #                 'box_1_3': {'box_key': 'red_zu1', 'state': True},
    #                 'box_2_0': {'box_key': None, 'state': None},
    #                 'box_2_1': {'box_key': None, 'state': None},
    #                 'box_2_2': {'box_key': None, 'state': None},
    #                 'box_2_3': {'box_key': None, 'state': None},
    #                 'box_3_0': {'box_key': None, 'state': None},
    #                 'box_3_1': {'box_key': None, 'state': None},
    #                 'box_3_2': {'box_key': None, 'state': None},
    #                 'box_3_3': {'box_key': 'red_jiang1', 'state': True},
    #                 'box_4_0': {'box_key': 'red_ju1', 'state': True},
    #                 'box_4_1': {'box_key': 'black_zu2', 'state': False},
    #                 'box_4_2': {'box_key': 'red_ju2', 'state': True},
    #                 'box_4_3': {'box_key': 'red_pao1', 'state': True},
    #                 'box_5_0': {'box_key': None, 'state': None},
    #                 'box_5_1': {'box_key': None, 'state': None},
    #                 'box_5_2': {'box_key': None, 'state': None},
    #                 'box_5_3': {'box_key': 'red_shi1', 'state': True},
    #                 'box_6_0': {'box_key': 'black_shi1', 'state': False},
    #                 'box_6_1': {'box_key': None, 'state': None},
    #                 'box_6_2': {'box_key': None, 'state': None},
    #                 'box_6_3': {'box_key': None, 'state': None},
    #                 'box_7_0': {'box_key': 'black_jiang1', 'state': False},
    #                 'box_7_1': {'box_key': 'red_xiang1', 'state': True},
    #                 'box_7_2': {'box_key': None, 'state': None},
    #                 'box_7_3': {'box_key': None, 'state': None}}
    a = 2
    # 明知要被吃掉还要去吃对方棋子的问题：
#     all_pieces = {'box_0_0': {'box_key': None, 'state': None},
# 'box_0_1': {'box_key': None, 'state': None},
# 'box_0_2': {'box_key': None, 'state': None},
# 'box_0_3': {'box_key': None, 'state': None},
# 'box_1_0': {'box_key': None, 'state': None},
# 'box_1_1': {'box_key': None, 'state': None},
# 'box_1_2': {'box_key': None, 'state': None},
# 'box_1_3': {'box_key': None, 'state': None},
# 'box_2_0': {'box_key': None, 'state': None},
# 'box_2_1': {'box_key': None, 'state': None},
# 'box_2_2': {'box_key': 'red_pao1', 'state': True},
# 'box_2_3': {'box_key': None, 'state': None},
# 'box_3_0': {'box_key': None, 'state': None},
# 'box_3_1': {'box_key': None, 'state': None},
# 'box_3_2': {'box_key': 'red_ju1', 'state': True},
# 'box_3_3': {'box_key': 'black_xiang2', 'state': True},
# 'box_4_0': {'box_key': None, 'state': None},
# 'box_4_1': {'box_key': 'black_shi2', 'state': True},
# 'box_4_2': {'box_key': None, 'state': None},
# 'box_4_3': {'box_key': None, 'state': None},
# 'box_5_0': {'box_key': None, 'state': None},
# 'box_5_1': {'box_key': None, 'state': None},
# 'box_5_2': {'box_key': None, 'state': None},
# 'box_5_3': {'box_key': None, 'state': None},
# 'box_6_0': {'box_key': None, 'state': None},
# 'box_6_1': {'box_key': None, 'state': None},
# 'box_6_2': {'box_key': None, 'state': None},
# 'box_6_3': {'box_key': None, 'state': None},
# 'box_7_0': {'box_key': 'black_jiang1', 'state': True},
# 'box_7_1': {'box_key': None, 'state': None},
# 'box_7_2': {'box_key': None, 'state': None},
# 'box_7_3': {'box_key': None, 'state': None}}
    all_pieces = {'box_0_0': {'box_key': None, 'state': None},
                  'box_0_1': {'box_key': 'red_zu3', 'state': False},
                  'box_0_2': {'box_key': None, 'state': None},
                  'box_0_3': {'box_key': 'black_zu3', 'state': False},
                  'box_1_0': {'box_key': None, 'state': None},
                  'box_1_1': {'box_key': None, 'state': None},
                  'box_1_2': {'box_key': 'black_zu5', 'state': True},
                  'box_1_3': {'box_key': 'red_jiang1', 'state': True},
                  'box_2_0': {'box_key': 'red_zu4', 'state': False},
                  'box_2_1': {'box_key': None, 'state': None},
                  'box_2_2': {'box_key': None, 'state': None},
                  'box_2_3': {'box_key': None, 'state': None},
                  'box_3_0': {'box_key': 'black_zu2', 'state': False},
                  'box_3_1': {'box_key': 'black_pao1', 'state': False},
                  'box_3_2': {'box_key': 'black_ju1', 'state': False},
                  'box_3_3': {'box_key': 'red_ma2', 'state': True},
                  'box_4_0': {'box_key': 'black_jiang1', 'state': False},
                  'box_4_1': {'box_key': 'red_zu1', 'state': False},
                  'box_4_2': {'box_key': 'black_zu4', 'state': False},
                  'box_4_3': {'box_key': 'red_xiang1', 'state': False},
                  'box_5_0': {'box_key': 'red_shi1', 'state': False},
                  'box_5_1': {'box_key': 'red_pao1', 'state': False},
                  'box_5_2': {'box_key': 'black_ju2', 'state': False},
                  'box_5_3': {'box_key': 'black_ma1', 'state': True},
                  'box_6_0': {'box_key': 'red_zu5', 'state': False},
                  'box_6_1': {'box_key': 'red_xiang2', 'state': False},
                  'box_6_2': {'box_key': 'black_xiang1', 'state': False},
                  'box_6_3': {'box_key': 'red_pao2', 'state': False},
                  'box_7_0': {'box_key': 'red_ma1', 'state': False},
                  'box_7_1': {'box_key': 'red_ju1', 'state': False},
                  'box_7_2': {'box_key': 'black_pao2', 'state': False},
                  'box_7_3': {'box_key': 'red_ju2', 'state': False}}
    move = MinMax.search_next_move(all_pieces, 'red', depth=1)
    logg.info(f"best_move:{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")
