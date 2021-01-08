#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  moves.py
@time:  2020/6/15 17:03
@title:
@content: 获取AI的可走棋内容
"""
from gameFunction import GameFunction
from settings import Settings
from algorithm.scores import Scores
from math import fabs
from loggerPrint import LoggerPrint

class MoveNodes():
    def __init__(self, box_name_from, box_from, box_action, box_name_to, box_to, box_res, score=10):
        self.box_name_from = box_name_from
        self.box_action = box_action
        self.box_from = box_from
        self.box_to = box_to
        self.box_name_to = box_name_to
        self.box_res = box_res
        self.score = score

class Moves():
    def __init__(self, all_pieces, player1Color):
        self.all_pieces = all_pieces
        self.player1_color = player1Color
        #
        self.settings = Settings()
        self.game_func = GameFunction(self.settings)
        self.log = LoggerPrint(self.settings).printLogToSystem(False)

    # 判断双方的jiang是否都还存在，取吃zu的得分
    def get_score_for_zu_by_jiang(self, box_color, box_name):
        # 先判断双方的jiang是否都还存在
        red_jiang_is_true, black_jiang_is_true = False, False
        for _, piece in self.all_pieces.items():
            if piece['box_key'] == 'red_jiang1':
                red_jiang_is_true = True
            elif piece['box_key'] == 'black_jiang1':
                black_jiang_is_true = True
        # 再对吃zu的得分进行判断：基于jiang是否存在，来判断吃对方zu的得分
        if box_color == 'red':
            if red_jiang_is_true is True:
                score = Scores.eat_score(f"{box_name}_zu")
            else:
                score = Scores.eat_score(f"{box_name}_zu_no_jiang")
        else:
            if black_jiang_is_true is True:
                score = Scores.eat_score(f"{box_name}_zu")
            else:
                score = Scores.eat_score(f"{box_name}_zu_no_jiang")
        #
        return score

    # 获得所有棋子可能的走棋内容（省略了很多不关联的走棋内容，比如不关联的打开棋子，走动棋子等等）
    def generate_all_moves(self):
        moves = []
        for box_xy, value in self.all_pieces.items():
            # 根据打开的棋子，列举棋子的所有走法
            if value['state'] is True:
                box_key = value['box_key']
                box_color, box_name = box_key.split('_')
                box_name = box_name[:-1]
                # 这是一个player2方阵的棋子
                if box_color != self.player1_color:
                    # 不等于'pao'，而且棋子偏大，可以翻开临近的棋子或者移动到临近的空格中
                    if box_name in ['shi', 'xiang', 'ma']:
                        # 取box的临近方格坐标
                        moves_1 = self._box_near_yes_or_no(box_xy, box_name, box_color, box_key)
                        moves += moves_1
                    # 不等于'pao'，而且棋子偏小，可以翻开斜角的棋子来保护，也可以移动到临近的棋子
                    elif box_name in ['jiang', 'ju', 'zu']:
                        # 取box的斜角方格坐标
                        box_open_corner = self._open_piece_for_corner(box_xy)
                        for box1 in box_open_corner:
                            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                            # 斜角方格坐标中，方格状态为False才有效
                            if box1_state is False:
                                score = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color, box1_state=False)
                                if score is not None:
                                    moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=score))
                        # 取box的临近方格坐标
                        moves_1 = self._box_near_yes_or_no(box_xy, box_name, box_color, box_key)
                        moves += moves_1
                    # 等于'pao'分两种情况：吃棋要跳着吃，走棋只能移动
                    elif box_name == 'pao':
                        # 取pao路上能吃棋的方格坐标
                        box_open_pao = self._open_piece_for_pao(box_xy)
                        for box1 in box_open_pao:
                            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                            # 方格状态为True，表示有吃棋的可能
                            if box1_state is True:
                                result = self.game_func.piece_VS_piece(box_xy, box1_xy, self.all_pieces)
                                if result[2] is True:
                                    # 判断box1不存在威胁
                                    score = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color)
                                    if score is not None:
                                        if box1_name == 'zu':
                                            move_score = self.get_score_for_zu_by_jiang(box_color, box_name)
                                        else:
                                            move_score = Scores.eat_score(f"{box_name}_{box1_name}")
                                        moves.append(MoveNodes(box_key, box_xy, '吃棋', box1_key, box1_xy, result[1], score=move_score))
                            # 方格状态为False，可以翻开再吃棋
                            elif box1_state is False:
                                # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                                score = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color, box1_state=False)
                                if score is not None:
                                    score += int(Scores.piece_score(box_name) / 100)
                                    moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=score))
                        # 移动的情况:取pao临近的方格坐标
                        moves_1 = self._box_near_yes_or_no(box_xy, box_name, box_color, box_key)
                        moves += moves_1
                # 这里表示当前的棋子是player1方阵的棋子
                else:
                    box_open = []
                    # 如果该棋子为"ma\ju\pao\zu",就可以在其旁边位置翻开棋子，有几率翻开电脑的棋子比它大（冒险一点的走法）
                    # 保守一点的走法就是该棋子为"ju\pao\zu",棋子偏小可以打开临近棋子，也可以打开寻找pao
                    if box_name in ['jiang', 'pao', 'zu', 'ju']:
                        box_open = self._open_piece_for_near(box_xy)
                    # 如果棋子偏大，就去翻开棋子找'pao'，这样'pao'就可以直接吃掉这个棋子
                    if box_name != 'pao':
                        box_open += self._open_piece_for_pao(box_xy)
                    for box1 in box_open:
                        box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                        if box1_state is False:
                            # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                            score = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color, box1_state=False)
                            if score is not None:
                                if box_name in ['jiang', 'shi', 'xiang', 'ma']:
                                    score += int(Scores.piece_score(box_name) / 100)
                                moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=score))
        return moves

    # 对当前棋子临近的方格做判断
    def _box_near_yes_or_no(self, box_xy, box_name, box_color, box_key):
        moves = []
        # 取临近的方格坐标
        box_open_near = self._open_piece_for_near(box_xy)
        for box1 in box_open_near:
            danger_score, score = 0, 0
            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
            # 临近的棋子为True，判断是否可以吃棋，不可以吃棋的话有没有威胁
            if box1_state is True:
                # box不为pao才能临近吃棋
                if box_name != 'pao':
                    # 对比两个棋子的大小
                    result = self.game_func.piece_VS_piece(box_xy, box1_xy, self.all_pieces)
                    # 对比结果有效
                    if result[2] is True:
                        # 临近的棋子比当前棋子大，有威胁:计算威胁的分值
                        if result[1] in ['jiang_zu', 'box1<box2']:
                            danger_score = self._danger_box_yes_or_no(box_name, box1_name, box1_color)
                            # 因为有danger_score，未避免danger_score前有box的'移动'行棋已经完成，因此需要修改box的'移动'行棋的move.score
                            for move in moves:
                                if move.box_name_from == box_key and move.box_from == box_xy and move.box_action == '移动':
                                    move.score += danger_score
                        # 临近的棋子等于当前棋子，则可以吃棋
                        elif result[1] == 'box1=box2':
                            if box1_name == 'zu':
                                move_score = self.get_score_for_zu_by_jiang(box_color, box_name)
                            else:
                                move_score = Scores.eat_score(f"{box_name}_{box1_name}")
                            score += move_score
                            moves.append(MoveNodes(box_key, box_xy, '吃棋', box1_key, box1_xy, result[1], score=score))
                        # 临近的棋子比当前棋子小，则可以吃棋
                        else:
                            # 判断box1不存在威胁
                            score_1 = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color)
                            if score_1 is not None:
                                if box1_name == 'zu':
                                    move_score = self.get_score_for_zu_by_jiang(box_color, box_name)
                                else:
                                    move_score = Scores.eat_score(f"{box_name}_{box1_name}")
                                score += score_1
                                score += move_score
                                moves.append(MoveNodes(box_key, box_xy, '吃棋', box1_key, box1_xy, result[1], score=score))
                # box为pao只能获取威胁分值
                else:
                    # 对比两个棋子的大小，反过来对比
                    result = self.game_func.piece_VS_piece(box1_xy, box_xy, self.all_pieces)
                    # 对比结果有效,得到反过来的结论才能得出威胁的分值
                    if result[2] is True and result[1] == 'success':
                        danger_score = self._danger_box_yes_or_no(box_name, box1_name, box1_color)
                        # danger_score的处理
                        for move in moves:
                            if move.box_name_from == box_name and move.box_from == box_xy and move.box_action == '移动':
                                move.score += danger_score
            # 临近的棋子为None或False
            else:
                # 临近的棋子为None，移动到该空格位上
                if box1_state is None:
                    score_1 = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color)
                    if score_1 is not None:
                        score += score_1
                        if danger_score != 0:
                            score += danger_score
                        moves.append(MoveNodes(box_key, box_xy, '移动', None, box1_xy, None, score=score))
                # 临近的棋子为False
                else:
                    # 棋子比较大，打开棋子
                    if box_name in ['shi', 'xiang', 'ma']:
                        score_1 = self._box_open_yes_or_no(box1_xy, box1_name, box1_color, box_xy, box_name, box_color, box1_state=False)
                        if score_1 is not None:
                            score += int(Scores.piece_score(box_name) / 100)
                            score += score_1
                            moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=score))
                    # 棋子比较小，以及打开斜角保护棋子，就不打开附近棋子了
                    elif box_name in ['jiang', 'ju', 'zu', 'pao']:
                        pass
        return moves

    # 对受威胁的棋子计算棋子的分值
    def _danger_box_yes_or_no(self, box_name, danger_box_name, danger_box_color):
        if box_name == 'zu':
            return int(self.get_score_for_zu_by_jiang(danger_box_color, danger_box_name) / 1000)
        else:
            return int(Scores.eat_score(f"{danger_box_name}_{box_name}") / 1000)

    # 判断当前的box可否打开，可否移动
    def _box_open_yes_or_no(self, box1_xy, box1_name, box1_color, box_xy, box_name, box_color, box1_state=None):
        # pao_flag为False表示该棋子不在pao路上，需要继续判断相邻的棋子是否有威胁
        pao_flag = False
        box_open_pao = self._open_piece_for_pao(box1_xy)
        # 是否在对方的pao路上
        for box2 in box_open_pao:
            box2_xy, box2_key, box2_state, box2_color, box2_name = self._get_box(box2)
            # 在对方pao的进攻路上，没有移动到box2的必要了
            if box2_xy != box_xy and box2_state is True and box2_color != box_color and box2_name == 'pao':
                pao_flag = True
                break
        # 判断临近的棋子是否会对该空格产生威胁
        if pao_flag is False:
            box_open_near = self._open_piece_for_near(box1_xy)
            for i, box3 in enumerate(box_open_near, 1):
                score = 10
                box3_xy, box3_key, box3_state, box3_color, box3_name = self._get_box(box3)
                if box3_xy != box_xy:
                    # box3为True，要判断box3是否能对box构成威胁
                    if box3_state is True:
                        # box3和box不在同一方阵颜色
                        if box3_color != box_color:
                            box3_index = self.settings.pieces_list.index(box3_name)
                            box_index = self.settings.pieces_list.index(box_name)
                            # 而且box3的棋子比box的小才行
                            if box_index <= box3_index or (box_name == 'zu' and box3_name == 'jiang'):
                                score_eat = 10
                                # 特殊情况：zu比jiang的index大，但zu是吃jiang的，只能break
                                if box_name == 'jiang' and box3_name == 'zu':
                                    break
                                # 特殊情况：pao和zu在一起以及jiang和pao在一起都是没影响的
                                elif (box_name == 'pao' and box3_name == 'zu') or (box_name == 'jiang' and box3_name == 'pao'):
                                    score_eat = 10
                                else:
                                    # 判断两个棋子是否在对角线上，而且田字格里没有其他的棋子
                                    box_x = int(box_xy.split('_')[1])
                                    box_y = int(box_xy.split('_')[-1])
                                    box3_x, box3_y = box3
                                    if (box3_x-box_x == 1 and box3_y-box_y == 1) or (box3_x-box_x == -1 and box3_y-box_y == 1):
                                        box4_x, box4_y = box3_x, box_y
                                        box5_x, box5_y = box_x, box3_y
                                        box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box((box4_x, box4_y))
                                        box5_xy, box5_key, box5_state, box5_color, box5_name = self._get_box((box5_x, box5_y))
                                        if box4_state is None and box5_state is None:
                                            score_eat = 10
                                    elif (box3_x-box_x == -1 and box3_y-box_y == -1) or (box3_x-box_x == 1 and box3_y-box_y == -1):
                                        box4_x, box4_y = box_x, box3_y
                                        box5_x, box5_y = box3_x, box_y
                                        box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box((box4_x, box4_y))
                                        box5_xy, box5_key, box5_state, box5_color, box5_name = self._get_box((box5_x, box5_y))
                                        if box4_state is None and box5_state is None:
                                            score_eat = 10
                                    else:
                                        score_eat = int(Scores.eat_score(f"{box_name}_{box3_name}") / 1000)
                                        score_eat += score
                                # 对同一个box1而言，box3的得分取最大就可以了
                                if score == 10 or score_eat >= score:
                                    score = score_eat
                            # box3的棋子比box的大，一般的情况是不能吃box1或者移动到box1
                            else:
                                # 特殊情况：pao或zu在ma或ju旁边时，应优先吃棋
                                if box_name in ['ma', 'ju'] and box1_name in ['pao', 'zu'] and box_color != box1_color:
                                    if box1_name == 'zu':
                                        score_eat = self.get_score_for_zu_by_jiang(box_color, box_name)
                                    else:
                                        score_eat = Scores.eat_score(f"{box_name}_{box1_name}")
                                    score += int(score_eat / 1000)
                                # 特殊情况：对方jiang在zu旁边，必须吃掉
                                if box_name == 'zu' and box1_name == 'jiang' and box_color != box1_color:
                                    if box1_name == 'zu':
                                        score_eat = self.get_score_for_zu_by_jiang(box_color, box_name)
                                    else:
                                        score_eat = Scores.eat_score(f"{box_name}_{box1_name}")
                                    score += int(score_eat / 1000)
                                else:
                                    break
                        # box3和box在同一方阵颜色，而且都为player1的方阵，取box1的状态，得到特殊得分
                        elif box3_color == box_color and box_color == self.player1_color and box1_state is False:
                            if (box_name == 'zu' and box3_name == 'ju') or (box3_name == 'zu' and box_name == 'ju'):
                                score = Scores.other_pieces_score('zu_ju')
                            elif (box_name == 'zu' and box3_name == 'pao') or (box3_name == 'zu' and box_name == 'pao'):
                                score = Scores.other_pieces_score('zu_pao')
                            elif (box_name == 'pao' and box3_name  == 'jiang') or (box3_name == 'pao' and box_name  == 'jiang'):
                                score = Scores.other_pieces_score('pao_jiang')
                            elif (box_name == 'pao' and box3_name == 'ju') or (box3_name == 'pao' and box_name == 'ju'):
                                score = Scores.other_pieces_score('pao_ju')
                    # box1有效，可以移动到该空格
                    else:
                        pass
                # 遍历box1附近的所有方格，如果都没有威胁则可返回
                if i == len(box_open_near):
                    return score
        return None

    # 根据getallmoves返回的box，找到box对应的box_key, box_state, box_color, box_name
    def _get_box(self, box):
        box_x, box_y = box
        box_xy = f'box_{box_x}_{box_y}'
        box_state = self.all_pieces[box_xy]['state']
        if box_state is True:
            box_key = self.all_pieces[box_xy]['box_key']
            box_value = box_key.split('_')
            box_color, box_name = box_value
            box_name = box_name[:-1]
        else:
            box_key, box_color, box_name = None, None, None
        return (box_xy, box_key, box_state, box_color, box_name)

    # 走棋内容为打开相邻位置的任意一个棋子
    def _open_piece_for_near(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # 计算box相邻的四个方向是否能打开
        # box位于棋盘的4个角上，则只能打开两个相邻位置的棋子
        if box_x == 0 and box_y == 0:
            box_open.append((box_x, box_y+1))
            box_open.append((box_x+1, box_y))
        elif box_x == 0 and box_y == 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
        elif box_x == 7 and box_y == 0:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
        elif box_x == 7 and box_y == 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x-1, box_y))
        # box位于棋盘的4条边线上，则可以打开3个相邻位置的棋子
        elif box_x == 0 and 0 < box_y < 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
            box_open.append((box_x, box_y+1))
        elif box_x == 7 and 0 < box_y < 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
        elif 0 < box_x < 7 and box_y == 0:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
            box_open.append((box_x+1, box_y))
        elif 0 < box_x < 7 and box_y == 3:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
        # box位于棋盘中间，则可以打开4个相邻位置的棋子
        else:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
            box_open.append((box_x, box_y+1))
        return box_open

    # 走棋内容为打开隔一个棋子的棋子，即假设翻开的棋子为'pao'就可以吃掉当前这个棋子
    def _open_piece_for_pao(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # box位于棋盘的第1，2纵列，则只能打开两个隔开的棋子
        if (box_x in [0, 1]) and (box_y in [0, 1]):
            for i in range(box_x+1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i+1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y+1, 4):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k+1, 4):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        elif (box_x in [0, 1]) and (box_y in [2, 3]):
            for i in range(box_x + 1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i + 1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y - 1, -1, -1):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        # box位于棋盘的第7，8纵列，则只能打开两个隔开的棋子
        elif (box_x in [6, 7]) and (box_y in [0, 1]):
            for i in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i - 1, -1, -1):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y+1, 4):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k+1, 4):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        elif (box_x in [6, 7]) and (box_y in [2, 3]):
            for i in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i - 1, -1, -1):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y-1, -1, -1):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        #
        else:
            for i in range(box_x + 1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i + 1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{k}_{box_y}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{m}_{box_y}']['state'] is not None:
                            box_open.append((m, box_y))
                            break
                    break
            if box_y in [0, 1]:
                for p in range(box_y + 1, 4):
                    if self.all_pieces[f'box_{box_x}_{p}']['state'] is not None:
                        for q in range(p + 1, 4):
                            if self.all_pieces[f'box_{box_x}_{q}']['state'] is not None:
                                box_open.append((box_x, q))
                                break
                        break
            elif box_y in [2, 3]:
                for r in range(box_y-1, -1, -1):
                    if self.all_pieces[f'box_{box_x}_{r}']['state'] is not None:
                        for s in range(r - 1, -1, -1):
                            if self.all_pieces[f'box_{box_x}_{s}']['state'] is not None:
                                box_open.append((box_x, s))
                                break
                        break
        return box_open

    # 走棋内容为打开斜角上的棋子，起到保护本方棋子的作用
    def _open_piece_for_corner(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # box位于4个角上，只有1个斜角棋子可用
        if box_x == 0 and box_y == 0:
            box_open.append((1, 1))
        elif box_x == 0 and box_y == 3:
            box_open.append((1, 2))
        elif box_x == 7 and box_y == 0:
            box_open.append((6, 1))
        elif box_x == 7 and box_y == 3:
            box_open.append((6, 2))
        # box位于第1列上，有2个斜角可用
        elif box_x == 0 and box_y in [1, 2]:
            box_open.append((1, box_y-1))
            box_open.append((1, box_y+1))
        # box位于第8列上，有2个斜角可用
        elif box_x == 7 and box_y in [1, 2]:
            box_open.append((6, box_y-1))
            box_open.append((6, box_y+1))
        # box位于第1行上，有2个斜角可用
        elif (0 < box_x < 7) and box_y == 0:
            box_open.append((box_x-1, 1))
            box_open.append((box_x+1, 1))
        # box位于第4行上，有2个斜角可用
        elif (0 < box_x < 7) and box_y == 3:
            box_open.append((box_x-1, 2))
            box_open.append((box_x+1, 2))
        # 其他位置上都有4个斜角可用
        else:
            box_open.append((box_x-1, box_y-1))
            box_open.append((box_x+1, box_y-1))
            box_open.append((box_x-1, box_y+1))
            box_open.append((box_x+1, box_y+1))
        return box_open

if __name__ == '__main__':
    all_pieces = {'box_0_0': {'box_key': 'red_pao2', 'state': False},
                  'box_0_1': {'box_key': 'red_ma2', 'state': False},
                  'box_0_2': {'box_key': 'red_xiang2', 'state': False},
                 'box_0_3': {'box_key': 'black_zu3', 'state': None},
                 'box_1_0': {'box_key': 'black_pao2', 'state': False},
                 'box_1_1': {'box_key': 'black_shi1', 'state': False},
                 'box_1_2': {'box_key': 'black_xiang2', 'state': False},
                 'box_1_3': {'box_key': 'black_xiang1', 'state': None},
                 'box_2_0': {'box_key': 'black_zu5', 'state': False},
                 'box_2_1': {'box_key': 'black_shi2', 'state': False},
                 'box_2_2': {'box_key': 'red_zu3', 'state': False},
                  'box_2_3': {'box_key': 'red_shi2', 'state': False},
                 'box_3_0': {'box_key': 'black_zu2', 'state': False},
                 'box_3_1': {'box_key': 'black_ma2', 'state': False},
                 'box_3_2': {'box_key': 'red_jiang1', 'state': False},
                  'box_3_3': {'box_key': 'red_zu1', 'state': False},
                 'box_4_0': {'box_key': 'red_zu4', 'state': False},
                  'box_4_1': {'box_key': 'red_ju1', 'state': False},
                 'box_4_2': {'box_key': 'red_pao1', 'state': True},
                 'box_4_3': {'box_key': 'black_zu4', 'state': None},
                 'box_5_0': {'box_key': 'black_zu1', 'state': False},
                 'box_5_1': {'box_key': 'black_ju2', 'state': False},
                 'box_5_2': {'box_key': 'red_xiang1', 'state': False},
                 'box_5_3': {'box_key': 'black_pao1', 'state': None},
                 'box_6_0': {'box_key': 'black_ma1', 'state': False},
                 'box_6_1': {'box_key': 'black_ju1', 'state': False},
                  'box_6_2': {'box_key': 'red_zu5', 'state': True},
                 'box_6_3': {'box_key': 'black_jiang1', 'state': True},
                 'box_7_0': {'box_key': 'red_ma1', 'state': False},
                  'box_7_1': {'box_key': 'red_ju2', 'state': False},
                 'box_7_2': {'box_key': 'red_zu2', 'state': False},
                  'box_7_3': {'box_key': 'red_shi1', 'state': False}}
    moves = Moves(all_pieces, 'red')
    get_moves = moves.generate_all_moves()
    for i, move in enumerate(get_moves, 1):
        logg.info(f"{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")


