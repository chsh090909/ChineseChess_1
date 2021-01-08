#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Settings(object):
    """
    配置文档
    """
    def __init__(self):
        # 设置版本号
        self.version = ' V1.0.0'
        self.version_file = 'help/versioninfo.me'
        # 窗体设置：宽、高、背景颜色、窗体标题以及窗体图标
        self.screen_width = 1030
        self.screen_height = 680
        self.window_start_x = 110
        self.window_start_y = 0
        self.bg_color = '#EFD7BD'
        self.game_title = '中国象棋'
        self.favicon = 'images/favicon1.ico'
        # 设置棋盘背景图（2选1）和放置位置坐标
        self.chess_board = 'images/chessboard2.gif'
        self.chess_board_localx = 87
        self.chess_board_localy = 20
        # 设置棋子大小、（0，0）棋子的位置
        self.piece_size = 100
        self.piece_first_x = self.chess_board_localx + 28
        self.piece_first_y = self.chess_board_localy + 32
        # 设置棋子背面的图案
        self.pieces_back = 'images/pieces_back.gif'
        # 设置棋子选中时的图案
        self.piece_selected = 'images/piece_selected.gif'
        # 关联红黑棋子的棋面显示
        self.pieces_noun = '.gif'
        self.pieces_front = 'images/piece_'
        self.pieces_list = ['jiang', 'shi', 'xiang', 'ma', 'ju', 'pao', 'zu']
        # 设置玩家文字、字体和字号
        self.player1_name = '玩家A'
        self.player2_name = '玩家B'
        self.player2_thinktime = 2
        self.font_style = '经典繁毛楷'
        self.font_color = '#8B4513'
        # 设置背景音乐的音乐列表
        self.music_list = ['101.mid', '102.mid', '103.mid', '104.mid', '105.mid', '106.mid', '107.mid', '108.mid',
                           '109.mid', '111.mid', '112.mid', '113.mid', '114.mid', '115.mid', '116.mid', '117.mid']
        # 设置各种动作音效
        self.cq = 'mids/chiqi.wav'
        self.cw = 'mids/cuowu.wav'
        self.hq = 'mids/huiqi.wav'
        self.xz = 'mids/xuanzhong.wav'
        self.zqwc = 'mids/zouqiwancheng.wav'
        # 设置帮助文档位置和名称
        self.help_file = '/help/教你如何玩.pdf'
        # 设置棋子的移动速度
        self.piece_move_speed = 30
        # 设置vs图片
        self.vs_image = 'images/vs1.gif'
        # 设置游戏结束图片和大小
        self.win_image = 'images/win1.gif'
        self.font_win_size = 50
        # 设置走棋步骤记录的文件名称
        self.info_file_name = 'logs/chess.info'
        # 设置日志文件记录位置和名称
        self.log_file_name = 'logs/chess.log'
        # 设置日志记录的格式、日志等级等信息
        self.sysout_format = "%(levelname)s - %(filename)s:%(funcName)s[line:%(lineno)d] --> %(message)s"
        self.file_write_format = '%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s[line:%(lineno)d] --> %(message)s'
        self.sysout_level = 'debug'
        self.file_write_level = 'info'
        # 设置文件的游戏开头语
        self.begin_str = "本轮游戏开始！！！当前第1局！"
        # 设置文件的游戏结束语
        self.end_str = ""
