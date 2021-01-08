#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  gameFunction.py
@time:  2020/3/18 20:05
@title:
@content:
"""
import random
from math import fabs
from loggerPrint import LoggerPrint

class GameFunction():
    """
    游戏逻辑的所有方法，不涉及到界面显示内容
    """
    def __init__(self, setting):
        self.setting = setting
        self.logger = LoggerPrint(self.setting).printLogToSystem()

    # 将红黑棋子对应的图片，关联起来，存放在字典中
    def _get_all_pieces(self, piece_flag):
        pieces = []
        for piece in self.setting.pieces_list:
            # value = f"{self.setting.pieces_front}{piece_flag}_{piece}{self.setting.pieces_noun}"
            if piece in ['shi', 'xiang', 'ma', 'ju', 'pao']:
                for i in range(1, 3):
                    pieces.append(f"{piece_flag}_{piece}{str(i)}")
            elif piece == 'zu':
                for i in range(1, 6):
                    pieces.append(f"{piece_flag}_{piece}{str(i)}")
            else:
                pieces.append(f"{piece_flag}_{piece}1")
        return pieces

    # 初始化棋子配置
    def box_pieces(self):
        # 获得所有的红黑棋子的dict
        pieces = self._get_all_pieces('red')
        pieces_black = self._get_all_pieces('black')
        pieces += pieces_black
        all_pieces = {}
        for i in range(8):
            for j in range(4):
                # 随机抽取key放入boxid中，并初始化box的状态为False
                random_key = random.choice(pieces)
                all_pieces[f"box_{i}_{j}"] = {'box_key': random_key, 'state': False}
                pieces.remove(random_key)
        return all_pieces

    # 获取鼠标位置所对应的方格id
    def get_box_xy(self, event_x, event_y):
        # 确定鼠标的有效矩形位置
        min_area_x = self.setting.piece_first_x
        min_area_y = self.setting.piece_first_y
        max_area_x = min_area_x + 8 * self.setting.piece_size
        max_area_y = min_area_y + 4 * self.setting.piece_size
        # 确认鼠标是在棋盘上有效的矩形范围之内
        if (min_area_x < event_x < max_area_x) and (min_area_y < event_y < max_area_y):
            mouse_x_not = (i * 100 + min_area_x for i in range(1, 9))
            mouse_y_not = (i * 100 + min_area_y for i in range(1, 5))
            # 鼠标不能在棋盘线上
            if (event_x not in mouse_x_not) and (event_y not in mouse_y_not):
                # 计算当前鼠标坐标所在的方格坐标
                box_x = int((event_x - min_area_x) / 100)
                box_y = int((event_y - min_area_y) / 100)
                return (box_x, box_y)

    # 获取棋子所在方格左上角的坐标
    # def get_box_local_xy(self, box_x, box_y):
    #     box_local_x = box_x * self.setting.piece_size + self.setting.piece_first_x
    #     box_local_y = box_y * self.setting.piece_size + self.setting.piece_first_y

    # 加载棋子对应的图片
    def get_piece_image(self):
        pieces_dict = {}
        for piece_name in self.setting.pieces_list:
            pieces_dict[f"red_{piece_name}"] = f"{self.setting.pieces_front}red_{piece_name}{self.setting.pieces_noun}"
            pieces_dict[f"black_{piece_name}"] = f"{self.setting.pieces_front}black_{piece_name}{self.setting.pieces_noun}"
        return pieces_dict

    # 两个棋子之间的比较
    def piece_VS_piece(self, box1_xy, box2_xy, all_pieces):
        '''
        :param box1_xy:
        :param box2_xy:
        :param all_pieces:
        :return: [True|False|None, '原因', True|False]
                True|False|None：表示box1和box2的比较结果
                '原因'：表示原因，便于提示失败的原因，也可指示成功的提示
                True|False：表示对于该原因，对后续AI走棋获取该走棋步骤时，是否为需要添加的走棋步骤
        '''
        value_list = self.setting.pieces_list
        box1_x = int(box1_xy.split('_')[1])
        box1_y = int(box1_xy.split('_')[2])
        box2_x = int(box2_xy.split('_')[1])
        box2_y = int(box2_xy.split('_')[2])
        box1_name = all_pieces[box1_xy]['box_key']
        box2_name = all_pieces[box2_xy]['box_key']
        box1_color = box1_name.split('_')[0]
        box1_value = box1_name.split('_')[1]
        box1_value = box1_value[:-1]
        box1_value_index = value_list.index(box1_value)
        # 如果box1的位置比box2的位置大，则交换他们的值
        if box1_y > box2_y:
            box1_y, box2_y = box2_y, box1_y
        if box1_x > box2_x:
            box1_x, box2_x = box2_x, box1_x
        # box2如果为空，则认为第二次选择了棋盘空格，不为空则需要取box2的值与box1比较
        if box2_name is not None:
            box2_color = box2_name.split('_')[0]
            if box2_color == box1_color:
                # self.logger.info("false原因：两个棋子在同一个方阵")
                return [False, 'color', False]
            box2_value = box2_name.split('_')[1]
            box2_value = box2_value[:-1]
            box2_value_index = value_list.index(box2_value)
        else:
            return self._other_vs_piece(box1_x, box1_y, box2_x, box2_y, piece_equal=False)
        # 如果两个棋子相同
        if box1_value_index == box2_value_index:
            if box1_value == 'pao':
                # '炮'相同时的吃法：
                # 中间有且只有一个棋子，中间棋子不论打没打开都可以，没有距离限制
                return self._pao_vs_piece(box1_x, box1_y, box2_x, box2_y, all_pieces, piece_equal=False)
            else:
                # 其他相同棋子的吃法：
                # 只能相邻位置两个棋子，最后也是两个棋子同时失去
                return self._other_vs_piece(box1_x, box1_y, box2_x, box2_y, piece_equal=True)
        # 如果两个棋子不相同
        else:
            if box1_value == 'pao':
                # '炮'的吃法：
                # 1、中间必须有且只有一个棋子，才能吃到对方棋子，没有距离限制；
                # 2、炮没有大小吃法限制，上到将，下到卒都可以吃；
                # 3、炮移动只能相邻的格子移动，不能跳着移动；
                return self._pao_vs_piece(box1_x, box1_y, box2_x, box2_y, all_pieces, piece_equal=False)
            else:
                # 其他的棋子的吃法：
                # 1、大吃小（将（帅）>士>（象）相>马>车>炮和卒（兵）），两两相同则一起吃掉；
                # 2、炮和卒（兵）、炮和将（帅）相互不能吃，任何棋子都可以吃炮，除了卒（兵）、将（帅）外；
                # 3、任何棋子都可以吃卒（兵），而卒（兵）只吃对方的帅（将）；
                # 4、棋子只能相邻的吃，而且一次只能走一步，吃一个棋子，炮除外
                if box1_value_index < box2_value_index:
                    # 大吃小，除非jiang和zu或pao同时出现
                    if box1_value == 'jiang' and box2_value == 'zu':
                        # self.logger.info("false原因：jiang在和zu比较")
                        return [False, 'jiang_zu', True]
                    elif box1_value == 'jiang' and box2_value == 'pao':
                        # self.logger.info("false原因：jiang在和pao比较")
                        return [False, 'jiang_pao', False]
                    else:
                        return self._other_vs_piece(box1_x, box1_y, box2_x, box2_y, piece_equal=False)
                elif box1_value_index > box2_value_index:
                    # 最后一种情况：zu只能吃jiang
                    if box1_value == 'zu' and box2_value == 'jiang':
                        return self._other_vs_piece(box1_x, box1_y, box2_x, box2_y, piece_equal=False)
                    elif box1_value == 'zu' and box2_value == 'pao':
                        # self.logger.info("false原因：zu在和pao比较")
                        return [False, 'zu_pao', False]
                    else:
                        # self.logger.info("false原因：box1比box2还小")
                        return [False, 'box1<box2', True]

    # pao的比较
    def _pao_vs_piece(self, box1_x, box1_y, box2_x, box2_y, all_pieces, piece_equal=True):
        if box1_x == box2_x and box2_y - box1_y > 1:
            between_state_have = 0
            for i in range(box1_y + 1, box2_y):
                if all_pieces[f"box_{box1_x}_{i}"]['state'] is not None:
                    between_state_have += 1
                if between_state_have > 1:
                    break
            if between_state_have == 1:
                if piece_equal is True:
                    # self.logger.info("None：box1和box2相同，都是pao")
                    return [None, 'box1=box2', True]
                else:
                    return [True, 'success', True]
            else:
                # self.logger.info("false原因：box1和box2之间，在y轴上没有棋子，或者有大于2个的棋子")
                return [False, 'pao_between', False]
        elif box1_y == box2_y and box2_x - box1_x > 1:
            between_state_have = 0
            for i in range(box1_x + 1, box2_x):
                if all_pieces[f"box_{i}_{box1_y}"]['state'] is not None:
                    between_state_have += 1
                if between_state_have > 1:
                    break
            if between_state_have == 1:
                if piece_equal is True:
                    # self.logger.info("None：box1和box2相同，都是pao")
                    return [None, 'box1=box2', True]
                else:
                    return [True, 'success', True]
            else:
                # self.logger.info("false原因：box1和box2之间，在x轴上没有棋子，或者有大于2个的棋子")
                return [False, 'pao_between', False]
        else:
            # self.logger.info("false原因：box1和box2不在同一条x轴或y轴上")
            return [False, 'box1_noline_box2', False]

    # 其他棋子的比较
    def _other_vs_piece(self, box1_x, box1_y, box2_x, box2_y, piece_equal=True):
        if (box1_x == box2_x and box2_y - box1_y == 1) or (box1_y == box2_y and box2_x - box1_x == 1):
            if piece_equal is True:
                # self.logger.info("None：box1和box2相同")
                return [None, 'box1=box2', True]
            else:
                return [True, 'success', True]
        else:
            # self.logger.info("false原因：box1和box2不在同一条x轴或y轴上")
            return [False, 'box1_noline_box2', False]

    # 游戏结束判断
    def is_game_over(self, all_pieces, nowPlayer, player1Color):
        # 循环all_pieces中的state得到棋子状态
        true_count = 0
        none_count = 0
        new_pieces = {}
        for key, value in all_pieces.items():
            for key1, value1 in value.items():
                if key1 == 'state':
                    if value1 is True:
                        true_count += 1
                        new_pieces[all_pieces[key]['box_key']] = key
                    elif value1 is False:
                        # 如果查到state的状态为false，立即return
                        return 'none'
                    elif value1 is None:
                        none_count += 1
        self.logger.info(f"true_count: {true_count}")
        self.logger.info(f"none_count: {none_count}")
        self.logger.info(f"new_pieces: {new_pieces}")
        # 如果allpieces全部为none，则为平局
        if none_count == 32:
            return 'tie'
        else:
            # 只有一个棋子，则取棋子的颜色return
            if true_count == 1:
                key_list = list(new_pieces.keys())
                box_color = key_list[0].split('_')[0]
                return box_color
            # 有多个棋子，则要分开判断
            else:
                # 取红黑棋子分别占有多少
                value_list = self.setting.pieces_list
                red_count, black_count = 0, 0
                box_count = len(new_pieces)
                for key, value in new_pieces.items():
                    box_color = key.split('_')[0]
                    if box_color == 'red':
                        red_count += 1
                    else:
                        black_count += 1
                self.logger.info(f"red_count: {red_count}")
                self.logger.info(f"black_count: {black_count}")
                self.logger.info(f"box_count: {box_count}")
                # 如果全部为红色或者黑色，则return
                if red_count == box_count:
                    return 'red'
                elif black_count == box_count:
                    return 'black'
                # 总数为2，红黑棋子各占1个
                elif box_count == 2 and red_count == 1:
                    red_x = 0
                    red_y = 0
                    red_value = ''
                    black_x = 0
                    black_y = 0
                    black_value = ''
                    for key, value in new_pieces.items():
                        box_color = key.split('_')[0]
                        box_value = key.split('_')[1]
                        if box_color == 'red':
                            red_x = int(value.split('_')[1])
                            red_y = int(value.split('_')[2])
                            red_value = box_value[:-1]
                        else:
                            black_x = int(value.split('_')[1])
                            black_y = int(value.split('_')[2])
                            black_value = box_value[:-1]
                    red_value_index = value_list.index(red_value)
                    black_value_index = value_list.index(black_value)
                    # 如果红黑双方棋子相同或者是不能相互吃掉的棋子，则为平局
                    if red_value == black_value or \
                            (red_value in ['jiang', 'pao'] and black_value in ['jiang', 'pao']) or \
                            (red_value in ['pao', 'zu'] and black_value in ['pao', 'zu']):
                        return 'tie'
                    # 当前玩家和玩家方阵为红方，且红方的棋子比黑方的棋子大，则他们相邻比较的时候就会是平局，红方无法吃掉黑方
                    if (nowPlayer == self.setting.player1_name and player1Color == 'red') or \
                            (nowPlayer == self.setting.player2_name and player1Color == 'black'):
                        if red_value_index > black_value_index:
                            if (red_x == black_x and fabs(red_y - black_y) == 1) or (
                                    red_y == black_y and fabs(red_x - black_x) == 1):
                                return 'tie'
                    # 黑方也是一样
                    elif (nowPlayer == self.setting.player1_name and player1Color == 'black') or \
                            (nowPlayer == self.setting.player2_name and player1Color == 'red'):
                        if red_value_index < black_value_index:
                            if (red_x == black_x and fabs(red_y - black_y) == 1) or (
                                    red_y == black_y and fabs(red_x - black_x) == 1):
                                return 'tie'
                # 总数>2，只判断一方只为1个的情况
                elif box_count > 2:
                    # 红方只有一个棋子，如果这个棋子在棋盘上黑方有其他棋子能吃掉它，则红方就一定会输
                    # 相反如果红方的这个棋子在棋盘上黑方没有棋子能吃掉它，那么就只能是平局了
                    if red_count == 1:
                        return self._one_vs_more(new_pieces, 'red', value_list)
                    elif black_count == 1:
                        return self._one_vs_more(new_pieces, 'black', value_list)
                    else:
                        return 'none'
        # return 'none'

    # 判断某一方只有一个棋子时
    def _one_vs_more(self, new_pieces, one_color, value_list):
        index_list = []
        for key, value in new_pieces.items():
            box_color = key.split('_')[0]
            box_value = key.split('_')[1]
            if box_color == one_color:
                one_value = box_value[:-1]
                one_index = value_list.index(one_value)
            else:
                more_value = box_value[:-1]
                index_list.append(value_list.index(more_value))
        # 红方只有一个pao，黑方也只有pao和zu，则为平局
        if one_index == 5 and [0, 1, 2, 3, 4] not in index_list and len(index_list) < 4:
            return 'tie'
        count = 0
        for index in index_list:
            if one_index < index:
                # 要排除jiang和zu同时存在的情况
                if one_index == 0 and index == 6:
                    return 'none'
                count += 1
            else:
                return 'none'
        # 如果对方所有的棋子都比这一个棋子小，则为平局
        if count == len(index_list):
            return 'tie'

if __name__ == '__main__':
    from ChineseChess.settings import Settings
    setting = Settings()
    gf = GameFunction(setting)

    pieces = gf.box_pieces()
    print(pieces)
