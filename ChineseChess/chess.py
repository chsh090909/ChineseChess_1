#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  chess.py
@time:  2020/3/8 16:37
@title:
@content:
"""
import os
import threading
import json
import timeit
from datetime import datetime
from tkinter import *
from tkinter import dialog
from tkinter import messagebox
from settings import Settings
from gameFunction import GameFunction
from customDialog import MyDialog
from playMusic import PlayMusic
from common import Commmon
from loggerPrint import LoggerPrint
# from algorithm.MinMax import MinMax
from algorithm.seachMove import SeachMove


# 导入settings配置文件
setting = Settings()
# 加载公共模块方法
common = Commmon(setting)
# 加载日志功能
logger = LoggerPrint(setting)
# 加载游戏逻辑方法
game = GameFunction(setting)
# 加载音乐播放模块
play_music = PlayMusic(setting)
# 加载AI模块
seach_move = SeachMove(setting)


class Chess(object):
    def __init__(self, master):
        self.master = master
        # 获取系统信息，mac系统flag=1，windows系统flag=2
        self.system_flag = common.get_system_name()
        # 打印日志到控制台
        self.log = logger.printLogToSystem(is_out_file=True)
        # 初始化所有棋子
        self.all_pieces = game.box_pieces()
        self.log.info(f"all_pieces: {self.all_pieces}")
        # 初始化走棋步骤相关参数
        self.first_selected_img = None
        self.first_selected_value = None
        self.put_selected_value = None
        self.box_img_dict = {}
        # 初始化玩家消息参数
        self.player1 = setting.player1_name
        self.player2 = setting.player2_name
        self.nowPlayer = self.player1
        self.player1Color = None
        self.player2Color = None
        self.totalCount = 0
        self.Player1WonCount = 0
        self.Player2WonCount = 0
        self.tieCount = 0
        # 记录行棋总步数
        self.numCount = 0
        # 完成一局的最小步数为48步(打开所有棋子需要32步，彼此都吃掉对方需要16步)
        # allCount只在走棋（非吃棋和打开棋子）的时候增加
        self.allCount = 48
        # 定义是否悔棋的标识
        self.isBreak = False
        # 游戏开始，写入游戏开始信息
        self.game_begin_time = datetime.now()
        self.begin_str = "*" * 20 + '人机对战模式' + "*" * 20 + '\n'
        self.begin_str += "*" * 20 + setting.begin_str + "*" * 20
        self.write_str = ''
        # 定义需要写入的文件为info文件，info文件拼接时间作为文件名
        self.info_file = setting.info_file_name
        filename_list = self.info_file.split('.')
        ntime = common.format_now_time()
        self.info_file = f"{filename_list[0]}{ntime}.{filename_list[1]}"
        # 写入info文件
        common.write_file(filename=self.info_file, write_value=self.begin_str)
        common.write_file(filename=self.info_file, write_value=json.dumps(self.all_pieces))
        # 设置走棋音效是否播放开关
        self.is_play = True
        # 设置游戏模式为人机还是双人对战，开局默认为人机对战模式
        self.is_player_vs_computer = True
        # 设置AI走棋的深度
        self.depth = 1
        # 设置锁定玩家1的开关，默认不锁定，当开启玩家2的AI且玩家2走棋时锁定
        self.lock_player1 = False
        # 加载目录菜单
        self.init_menu()
        # 加载窗体内容
        self.init_widgets()

    # 初始化菜单栏
    def init_menu(self):
        menubar = Menu(self.master)
        # 添加菜单条
        self.master['menu'] = menubar
        # 创建顶级菜单
        server_menu = Menu(menubar, tearoff=0)
        operation_menu = Menu(menubar, tearoff=0)
        help_menu = Menu(menubar, tearoff=0)
        # 添加顶级菜单
        menubar.add_cascade(label='游戏', menu=server_menu)
        menubar.add_cascade(label='操作', menu=operation_menu)
        menubar.add_cascade(label='帮助', menu=help_menu)
        # 为server_menu添加菜单项
        mode_menu = Menu(server_menu, tearoff=0)
        server_menu.add_cascade(label='模式', menu=mode_menu)
        server_menu.add_command(label='打开', command=None, compound=LEFT)
        # 此处要判断一下操作系统类型：mac系统自带菜单退出系统功能，windows系统则需要添加
        if self.system_flag == 2:
            # 添加菜单分割条
            server_menu.add_separator()
            # 为windows系统添加退出游戏菜单
            server_menu.add_command(label='退出游戏', command=self.close_window, compound=LEFT)
        # 为模式功能添加模式列表
        self.mode_var = IntVar()
        # 设置单选按钮默认选择第一个
        self.mode_var.set(1)
        mode_menu.add_radiobutton(label='人机对战', command=self.play_mode, variable=self.mode_var, value=1)
        mode_menu.add_radiobutton(label='双人对战', command=self.play_mode, variable=self.mode_var, value=2)
        # 为operation_menu添加菜单项
        operation_menu.add_command(label='悔棋', command=self.break_piece, compound=LEFT)
        # 加分割条
        operation_menu.add_separator()
        # 为背景音乐子菜单创建目录
        operation_menu.add_command(label='音乐音效全关/开', command=self.change_all_sound, compound=LEFT)
        operation_menu.add_command(label='关闭背景音乐', command=play_music.stop_bg_music, compound=LEFT)
        bg_music_menu = Menu(operation_menu, tearoff=0)
        operation_menu.add_cascade(label='切换背景音乐', menu=bg_music_menu)
        # 加载背景音乐列表
        bg_music_menu.add_radiobutton(label='随机下一首', command=play_music.play_bg_music, compound=LEFT)
        self.bg_music_var = IntVar()
        for i, music_list in enumerate(setting.music_list):
            bg_music_menu.add_radiobutton(label=music_list, command=self.change_bg_music, variable=self.bg_music_var, value=i)
        # 为help_menu添加菜单项
        help_menu.add_command(label='如何玩?', command=self.how_play, compound=LEFT)
        help_menu.add_command(label='关于...', command=self.about_dialog, compound=LEFT)

    # 为模式菜单，添加功能
    def play_mode(self):
        # 获得玩家选择的对战模式
        mode_id = self.mode_var.get()
        mode_value = '双人' if mode_id == 2 else '人机'
        # 当前为人机模式，玩家切换为双人模式，或者当前为双人模式，玩家切换为人机模式
        if (self.is_player_vs_computer is True and mode_id == 2) or (
                self.is_player_vs_computer is False and mode_id == 1):
            # 弹框提示
            dialog_value = {
                'title': '切换游戏模式',
                'text': f"切换游戏模式则当前正在进行的游戏将不能保存，确定要切换到{mode_value}对战模式吗？",
                'bitmap': 'warning',
                'default': 1,
                'strings': ('确定', '取消')
            }
            d = dialog.Dialog(self.master, dialog_value)
            # 选择确定按钮
            if d.num == 0:
                # 重新开始游戏
                self.reset_game_start(write_won='', is_normal_over=False)
                # 更改对战模式的状态
                if mode_id == 1:
                    self.is_player_vs_computer = True
                    self.begin_str = "*" * 20 + '人机对战模式' + "*" * 20 + '\n'
                    self.log.info('切换人机对战模式！！')
                else:
                    self.is_player_vs_computer = False
                    self.begin_str = "*" * 20 + '双人对战模式' + "*" * 20 + '\n'
                    self.log.info('切换双人对战模式！！')
                # 写入info文件
                self.begin_str += "*" * 20 + setting.begin_str + "*" * 20
                common.write_file(filename=self.info_file, write_value=self.begin_str)

    # 为关于菜单，打开自定义对话框展示版本信息等
    def about_dialog(self):
        MyDialog(self.master, widget='about', title='关于游戏', img=red_jiang_img, systemFlag=self.system_flag)

    # 为如何玩菜单，打开pdf文件
    def how_play(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        help_file_path = base_dir + setting.help_file
        # mac系统
        if self.system_flag == 1:
            os.system(f'open {help_file_path}')
        # windows系统
        elif self.system_flag == 2:
            os.system('chcp 65001')
            full_path = '"' + help_file_path + '"'
            os.system('"' + full_path + '"')

    # 为子菜单背景音乐菜单，切换背景音乐功能
    def change_bg_music(self):
        music_id = self.bg_music_var.get()
        music_list = setting.music_list
        play_music.play_bg_music(music_file=music_list[music_id])

    # 为音乐音效全关/开菜单，设置循环功能
    def change_all_sound(self):
        if self.is_play is True:
            # 关闭背景音乐
            play_music.stop_bg_music()
            # 将走棋音效是否播放开关置为false
            self.is_play = False
            self.log.info("走棋音效关闭！")
        else:
            # 打开随机播放背景音乐
            play_music.play_bg_music()
            # 将走棋音效是否播放开关置为True
            self.is_play = True
            self.log.info("走棋音效打开！")

    # 为悔棋菜单，设置功能
    def break_piece(self):
        if self.numCount <= 1:
            pass
        else:
            # 取info文件的走棋内容
            info_list = common.read_file(filename=self.info_file, flag='info')
            # 删除lastline最后一步的内容(倒数三行)
            break_player = self.nowPlayer
            self.log.info(f"玩家: {break_player} 点击悔棋===>开始")
            break_value = info_list[len(info_list) - 3].strip()
            self.log.info(f"悔棋需要还原的内容==>{break_value}")
            self.log.info(f"悔棋需要丢掉的allpieces值==>{info_list[len(info_list) - 2].strip()}")
            self.log.info(f"悔棋需要丢掉的box_img_dict值==>{info_list[len(info_list) - 1].strip()}")
            info_list.pop()
            info_list.pop()
            info_list.pop()
            # 还原上一步的内容
            break_value = break_value.split('|')[-1]
            self.numCount -= 1
            # 根据行棋内容，还原之前的内容
            if '打开棋子' in break_value:
                break_value = break_value.split(':')[-1]
                box_xy = break_value.split(',')[0].lstrip('[')
                box_x = int(box_xy.split('_')[1])
                box_y = int(box_xy.split('_')[-1])
                # 删除现在打开的棋子图片
                self.cv.delete(self.box_img_dict[f"box_{box_x}_{box_y}"])
                # 重新创建棋子背面图片在box上
                piece_local_x = setting.piece_first_x + box_x * setting.piece_size
                piece_local_y = setting.piece_first_y + box_y * setting.piece_size
                back_img = self.cv.create_image(piece_local_x, piece_local_y, image=pieces_back_img, anchor=NW)
                self.box_img_dict[f"box_{box_x}_{box_y}"] = back_img
            elif '吃棋' in break_value:
                break_value = break_value.split(':')
                box1 = break_value[-2]
                box2 = break_value[-1]
                box1_xy = box1.split(',')[0].lstrip('[')
                box2_xy = box2.split(',')[0].lstrip('[')
                box1_value = box1.split(',')[1].rstrip(']')
                box2_value = box2.split(',')[1].rstrip(']')
                box1_value = box1_value[:-1]
                box2_value = box2_value[:-1]
                box1_name = box1_value.split('_')[-1]
                box2_name = box2_value.split('_')[-1]
                box1_local_x = int(box1_xy.split('_')[1]) * setting.piece_size + setting.piece_first_x
                box1_local_y = int(box1_xy.split('_')[-1]) * setting.piece_size + setting.piece_first_y
                box2_local_x = int(box2_xy.split('_')[1]) * setting.piece_size + setting.piece_first_x
                box2_local_y = int(box2_xy.split('_')[-1]) * setting.piece_size + setting.piece_first_y
                # 判断两个棋子是否相同
                if box1_name != box2_name:
                    # 两个不同，box2先delete
                    self.cv.delete(self.box_img_dict[box2_xy])
                # box1和box2都create回来
                box1_img = self.cv.create_image(box1_local_x, box1_local_y, image=pieces_img[box1_value], anchor=NW)
                box2_img = self.cv.create_image(box2_local_x, box2_local_y, image=pieces_img[box2_value], anchor=NW)
                self.box_img_dict[box1_xy] = box1_img
                self.box_img_dict[box2_xy] = box2_img
            elif '移动' in break_value:
                break_value = break_value.split(':')
                box1 = break_value[-2]
                box2 = break_value[-1]
                box1_xy = box1.split(',')[0].lstrip('[')
                box2_xy = box2.split(',')[0].lstrip('[')
                box1_local_x = int(box1_xy.split('_')[1]) * setting.piece_size + setting.piece_first_x
                box1_local_y = int(box1_xy.split('_')[-1]) * setting.piece_size + setting.piece_first_y
                # 将box2上的图片重新移回到box1的位置上
                self.cv.coords(self.box_img_dict[box2_xy], box1_local_x, box1_local_y)
                self.box_img_dict[box1_xy] = self.box_img_dict[box2_xy]
                self.box_img_dict[box2_xy] = None
                # 只有移动的时候allcount才会增加1，所以这里悔棋的时候allcount要减1
                self.allCount -= 1
            # 还原all_pieces，box_img_dict不能用原来的了，里面的值在create图片的时候已经发生改变了
            break_all_pieces = info_list[len(info_list) - 2].strip()
            break_all_pieces = json.loads(break_all_pieces)
            self.all_pieces = break_all_pieces
            # 还原玩家和玩家状态信息
            if self.nowPlayer == self.player1:
                self.nowPlayer = self.player2
                self.cv.itemconfig(self.player1_state, text=f'状态：走棋完毕！', fill=setting.font_color)
                self.cv.itemconfig(self.player2_state, text=f'状态：正在走棋。。。', fill='#006400')
            else:
                self.nowPlayer = self.player1
                self.cv.itemconfig(self.player1_state, text=f'状态：正在走棋。。。', fill='#006400')
                self.cv.itemconfig(self.player2_state, text=f'状态：走棋完毕！', fill=setting.font_color)
            # 悔棋标识置为True
            self.isBreak = True
            # 播放悔棋的音效
            if self.is_play is True:
                play_music.load_play_sound(setting.hq)
            # 将infolist重新写回info文件
            common.write_file(self.info_file, write_value=info_list)
            #
            self.log.info(f"self.numCount: {self.numCount}")
            self.log.info(f"self.allCount: {self.allCount}")
            self.log.info(f"玩家: {break_player} 点击悔棋===>结束")

    # 初始化窗体内容
    def init_widgets(self):
        # 加载游戏模式界面
        # MyDialog(self.master, widget='start', title='开始游戏', img=red_jiang_img)
        # 设置画布
        self.cv = Canvas(self.master, bg=setting.bg_color)
        self.cv.pack(fill=BOTH, expand=YES)
        # 使画布得到焦点
        self.cv.focus_set()
        # 加载棋盘图片
        self.load_chess_board()
        # 加载棋子背面图片
        self.load_pieces_back()
        # 加载玩家信息内容
        self.load_player_info()
        # 加载鼠标悬停棋子的选中效果
        self.piece_selected = self.load_piece_selected()
        # 鼠标按住并移动
        self.cv.bind('<B1-Motion>', self.b1_move_handler)
        # 鼠标释放
        self.cv.bind('<ButtonRelease-1>', self.b1_release_handler)
        # 鼠标悬停
        self.cv.bind('<Motion>', self.move_handler)
        # 鼠标按下
        self.cv.bind('<Button-1>', self.click_handler)

    # 加载棋盘图片
    def load_chess_board(self):
        self.cv.create_image(setting.chess_board_localx, setting.chess_board_localy, image=board_img, anchor=NW)

    # 加载棋子背面，循环加载
    def load_pieces_back(self):
        for i in range(8):
            for j in range(4):
                piece_local_x = setting.piece_first_x + i * setting.piece_size
                piece_local_y = setting.piece_first_y + j * setting.piece_size
                back_img = self.cv.create_image(piece_local_x, piece_local_y, image=pieces_back_img, anchor=NW)
                self.box_img_dict[f"box_{i}_{j}"] = back_img

    # 加载选中棋子的图片
    def load_piece_selected(self):
        piece_selected = self.cv.create_image(-100, -100, image=piece_selected_img)
        return piece_selected

    # 初始化玩家信息部分的内容
    def load_player_info(self, layout='default'):
        self.cv.create_rectangle(0, 495, 1030, 500, fill='red', outline='red')
        self.cv.create_image(515, 590, image=vs_img)
        if layout == 'default':
            # 定义字体(根据系统类型设置字体字号)
            player_name_font = ('STXingkaiTC-Bold', 44) if self.system_flag == 1 else (setting.font_style, 30)
            player_info_font = ('STXingkaiTC-Bold', 28) if self.system_flag == 1 else (setting.font_style, 19)
            font_color = setting.font_color
            # 玩家一
            self.player1_name = self.cv.create_text(184, 525, text=self.player1, font=player_name_font, fill=None)
            self.player1_img = self.cv.create_image(413, 565, image=None)
            self.player1_color = self.cv.create_text(413, 625, text=f' ', font=player_name_font, fill=None)
            self.player1_state = self.cv.create_text(35, 560, text=f'状态：正在走棋。。。', fill='#006400', font=player_info_font, anchor=NW)
            self.player1_won = self.cv.create_text(35, 595, text=f'胜利：0 局', fill=font_color, font=player_info_font, anchor=NW)
            self.player1_tie = self.cv.create_text(35, 630, text=f'打平：0 局', fill=font_color, font=player_info_font, anchor=NW)
            # 玩家二
            self.player2_name = self.cv.create_text(842, 525, text=self.player2, font=player_name_font, fill=None)
            self.player2_img = self.cv.create_image(620, 565, image=None)
            self.player2_color = self.cv.create_text(620, 625, text=f' ', font=player_name_font, fill=None)
            self.player2_state = self.cv.create_text(710, 560, text=f'状态：走棋完成！', fill=font_color, font=player_info_font, anchor=NW)
            self.player2_won = self.cv.create_text(710, 595, text=f'胜利：0 局', fill=font_color, font=player_info_font, anchor=NW)
            self.player2_tie = self.cv.create_text(710, 630, text=f'打平：0 局', fill=font_color, font=player_info_font, anchor=NW)
        else:
            pass

    # 更新玩家信息部分的内容
    def upd_player_info(self, box_key):
        self.numCount += 1
        if self.numCount == 1:
            self.player1Color = box_key.split('_')[0]
            if self.player1Color == 'red':
                self.cv.itemconfig(self.player1_name, fill='red')
                self.cv.itemconfig(self.player2_name, fill='black')
                self.cv.itemconfig(self.player1_img, image=red_jiang_img)
                self.cv.itemconfig(self.player2_img, image=black_jiang_img)
                self.cv.itemconfig(self.player1_color, text=f'红方', fill='red')
                self.cv.itemconfig(self.player2_color, text=f'黑方', fill='black')
                self.player2Color = 'black'
            else:
                self.cv.itemconfig(self.player1_name, fill='black')
                self.cv.itemconfig(self.player2_name, fill='red')
                self.cv.itemconfig(self.player1_img, image=black_jiang_img)
                self.cv.itemconfig(self.player2_img, image=red_jiang_img)
                self.cv.itemconfig(self.player1_color, text=f'黑方', fill='black')
                self.cv.itemconfig(self.player2_color, text=f'红方', fill='red')
                self.player2Color = 'red'
        # 根据当前的总走棋步数更新玩家状态信息
        if self.numCount % 2 == 1:
            self.cv.itemconfig(self.player1_state, text=f'状态：走棋完毕！', fill=setting.font_color)
            self.cv.itemconfig(self.player2_state, text=f'状态：正在走棋。。。', fill='#006400')
            self.nowPlayer = self.player2
        else:
            self.cv.itemconfig(self.player1_state, text=f'状态：正在走棋。。。', fill='#006400')
            self.cv.itemconfig(self.player2_state, text=f'状态：走棋完毕！', fill=setting.font_color)
            self.nowPlayer = self.player1

    # 重置部分参数状态
    def reset_first_state(self):
        # 删除第一次选中的图片
        self.cv.delete(self.first_selected_img)
        # 重置状态为初始状态
        self.first_selected_img = None
        self.first_selected_value = None
        self.put_selected_value = None

    # 重置游戏开始状态
    def reset_game_start(self, write_won, is_normal_over=True):
        if is_normal_over:
            # 加载游戏胜利对话框
            MyDialog(self.master, widget='over', title=f'第{self.totalCount}局游戏结束', img=win_img,
                     totalCount=self.totalCount, writeWin=write_won, systemFlag=self.system_flag)
        # 清空棋盘
        for i in range(8):
            for j in range(4):
                if self.box_img_dict[f"box_{i}_{j}"] is not None:
                    self.cv.delete(self.box_img_dict[f"box_{i}_{j}"])
        # 重新加载棋子背面图片
        self.box_img_dict = {}
        self.load_pieces_back()
        # 加载初始的玩家信息
        self.cv.itemconfig(self.player1_name, fill=None)
        self.cv.delete(self.player1_img)
        self.player1_img = self.cv.create_image(413, 565, image=None)
        self.cv.itemconfig(self.player2_name, fill=None)
        self.cv.delete(self.player2_img)
        self.player2_img = self.cv.create_image(620, 565, image=None)
        self.cv.itemconfig(self.player1_color, text=' ')
        self.cv.itemconfig(self.player2_color, text=' ')
        self.cv.itemconfig(self.player1_state, text=f'状态：正在走棋。。。', fill='#006400')
        self.cv.itemconfig(self.player2_state, text=f'状态：走棋完成！', fill=setting.font_color)
        if write_won == f"恭喜玩家：{setting.player1_name} 胜利!":
            self.cv.itemconfig(self.player1_won, text=f'胜利：{self.Player1WonCount} 局')
        elif write_won == f"恭喜玩家：{setting.player2_name} 胜利!":
            self.cv.itemconfig(self.player2_won, text=f'胜利：{self.Player2WonCount} 局')
        elif write_won == "本局游戏为平局!":
            self.cv.itemconfig(self.player1_tie, text=f'打平：{self.tieCount} 局')
            self.cv.itemconfig(self.player2_tie, text=f'打平：{self.tieCount} 局')
        elif write_won == '':
            # 重置玩家状态信息
            self.cv.itemconfig(self.player1_won, text=f'胜利：0 局')
            self.cv.itemconfig(self.player1_tie, text=f'打平：0 局')
            self.cv.itemconfig(self.player2_won, text=f'胜利：0 局')
            self.cv.itemconfig(self.player2_tie, text=f'打平：0 局')
        # 初始化所有棋子
        self.log.info("游戏结束：初始化各个参数==>开始")
        self.all_pieces = game.box_pieces()
        # 重置参数值
        self.reset_first_state()
        # 初始化玩家消息参数
        self.nowPlayer = self.player1
        self.player1Color = None
        self.player2Color = None
        self.numCount = 0
        self.allCount = 48
        self.log.info("游戏结束：初始化各个参数==>结束")
        self.log.info(f"游戏重新开始后all_pieces: {self.all_pieces}")

    # 打印各个参数的值
    def print_log(self):
        self.log.info(f"打印参数值==>开始")
        self.log.info(f"all_pieces: {self.all_pieces}")
        self.log.info(f"self.is_player_vs_computer: {self.is_player_vs_computer}")
        self.log.info(f"self.first_selected_img: {self.first_selected_img}")
        self.log.info(f"self.first_selected_value: {self.first_selected_value}")
        self.log.info(f"self.nowPlayer: {self.nowPlayer}")
        self.log.info(f"self.player1Color: {self.player1Color}")
        self.log.info(f"self.player2Color: {self.player2Color}")
        self.log.info(f"self.numCount: {self.numCount}")
        self.log.info(f"self.allCount: {self.allCount}")
        self.log.info(f"self.box_img_dict: {self.box_img_dict}")
        self.log.info(f"打印参数值==>结束")
        self.log.info("=" * 50)

    # 鼠标移动悬停事件：获取鼠标坐标，画一个高亮的圆，表示当前鼠标在这个棋子上
    def move_handler(self, event):
        if game.get_box_xy(event.x, event.y) and self.lock_player1 is False:
            box_x, box_y = game.get_box_xy(event.x, event.y)
            box_center_x = box_x * setting.piece_size + setting.piece_first_x + setting.piece_size / 2
            box_center_y = box_y * setting.piece_size + setting.piece_first_y + setting.piece_size / 2
            if self.all_pieces[f"box_{box_x}_{box_y}"]['state'] is not None:
                # 将create_image之后选中的图片，叠加到鼠标对应的棋子上
                self.cv.coords(self.piece_selected, box_center_x, box_center_y)

    # 鼠标左键按下事件：
    def click_handler(self, event):
        if game.get_box_xy(event.x, event.y) and self.lock_player1 is False:
            box_x, box_y = game.get_box_xy(event.x, event.y)
            box_xy = f'box_{box_x}_{box_y}'
            # 获取按下时的box坐标
            self.put_selected_value = box_xy

    # 鼠标左键拖动事件：
    def b1_move_handler(self, event):
        if self.lock_player1 is False and self.put_selected_value is not None:
            box_xy = self.put_selected_value
            # 当前棋子必须为True的状态，而且还必须是自己方阵的棋子才允许拖动
            if self.all_pieces[box_xy]['state'] is True:
                # 判断棋子方阵
                box_color = self.all_pieces[box_xy]['box_key'].split('_')[0]
                if (self.player1Color == box_color and self.nowPlayer == self.player1) or \
                        (self.player2Color == box_color and self.nowPlayer == self.player2):
                    # 确定鼠标的有效矩形位置
                    min_area_x = setting.piece_first_x
                    min_area_y = setting.piece_first_y
                    max_area_x = min_area_x + 8 * setting.piece_size
                    max_area_y = min_area_y + 4 * setting.piece_size
                    # 确认鼠标是在棋盘上有效的矩形范围之内
                    if (min_area_x < event.x < max_area_x) and (min_area_y < event.y < max_area_y):
                        mouse_x_not = [i * 100 + min_area_x for i in range(1, 9)]
                        mouse_y_not = [i * 100 + min_area_y for i in range(1, 5)]
                        # 鼠标不能在棋盘线上
                        if (event.x not in mouse_x_not) and (event.y not in mouse_y_not):
                            # 拖动棋子到鼠标位置
                            self.cv.coords(self.box_img_dict[box_xy], event.x - setting.piece_size / 2,
                                           event.y - setting.piece_size / 2)

    # 鼠标左键释放事件：
    def b1_release_handler(self, event):
        if game.get_box_xy(event.x, event.y) and self.lock_player1 is False:
            box2_x, box2_y = game.get_box_xy(event.x, event.y)
            # box2_xy = f"box_{box2_x}_{box2_y}"
            # 调用棋子操作
            self.pieces_action(box2_x, box2_y)

    # 为棋子状态做对应的棋子操作
    def pieces_action(self, box2_x, box2_y, box_from=None):
        if self.lock_player1 is False:
            #
            box2_xy = f"box_{box2_x}_{box2_y}"
            box2_piece = self.all_pieces[box2_xy]
            box2_state = box2_piece['state']
            box2_local_x = int(box2_x) * setting.piece_size + setting.piece_first_x
            box2_local_y = int(box2_y) * setting.piece_size + setting.piece_first_y
            # 对box_from判断，box_from在电脑行棋时有效
            if box_from is not None:
                self.put_selected_value = box2_xy
                self.first_selected_value = box_from
            # 棋子状态为True
            if box2_state is True:
                # 按下和释放在同一个方格
                if self.put_selected_value == box2_xy:
                    # 第一次选择没有值，赋值并选中该棋子
                    if self.first_selected_value is None:
                        box2_color = box2_piece['box_key'].split('_')[0]
                        # 当前玩家选择了当前玩家方阵的棋子
                        if (self.player1Color == box2_color and self.nowPlayer == self.player1) or \
                                (self.player2Color == box2_color and self.nowPlayer == self.player2):
                            # 第一次选择棋子，加载选中框
                            self.first_selected_img = self.cv.create_image(box2_local_x, box2_local_y, image=piece_selected_img, anchor=NW)
                            # 第一次选择的棋子
                            self.first_selected_value = box2_xy
                            # 重新创建这个图片，存放在box_img_dict中
                            box2_key = box2_piece['box_key']
                            box2_key = box2_key[:-1]
                            piece_img = pieces_img[box2_key]
                            self.cv.delete(self.box_img_dict[box2_xy])
                            self.box_img_dict[box2_xy] = self.cv.create_image(box2_local_x, box2_local_y, image=piece_img, anchor=NW)
                            # 播放选择棋子的音效
                            if self.is_play is True:
                                play_music.load_play_sound(setting.xz)
                            self.log.info(f"第一次选择的内容：{self.all_pieces[box2_xy]}")
                            self.print_log()
                    # 第一次选择有值，则认为这是第二次选择，需要判断走棋或吃棋
                    else:
                        # 获取第一次选择的值
                        box1_xy = self.first_selected_value
                        box1_name = self.all_pieces[box1_xy]['box_key']
                        box2_name = box2_piece['box_key']
                        self.log.info("=====两个棋子开始比较=====")
                        self.log.info(f"box1_xy(box1_name) : box2_xy(box2_name) ==> {box1_xy}({box1_name}) : {box2_xy}({box2_name})")
                        # 获取比较的结果
                        vs_res = game.piece_VS_piece(box1_xy, box2_xy, self.all_pieces)
                        self.log.info(f"比较之后的结果: {vs_res}")
                        if vs_res[0] is False:
                            # 播放走棋错误的音效
                            if self.is_play is True:
                                play_music.load_play_sound(setting.cw)
                        self.log.info("=====两个棋子比较结束=====")
                        # 更新棋盘信息以及玩家状态
                        self.vs_result(vs_res[0], box1_xy, box2_xy, box1_name, box2_name)
                # 按下和释放不在同一个方格，表示鼠标有拖动
                else:
                    # 判断鼠标按下时的方格状态
                    box_put_piece = self.all_pieces[self.put_selected_value]
                    box_put_state = box_put_piece['state']
                    if box_put_state is True:
                        # 取按下时方格中棋子的颜色方阵
                        box_put_color = box_put_piece['box_key'].split('_')[0]
                        # 必须为自己方阵颜色的棋子才允许拖动
                        if (self.player1Color == box_put_color and self.nowPlayer == self.player1) or \
                                (self.player2Color == box_put_color and self.nowPlayer == self.player2):
                            # 将按下时的方格坐标给第一次的选择
                            self.first_selected_value = self.put_selected_value
                            box1_name = self.all_pieces[self.first_selected_value]['box_key']
                            box2_name = box2_piece['box_key']
                            self.log.info("=====两个棋子开始比较=====")
                            self.log.info(f"box1_xy(box1_name) : box2_xy(box2_name) ==> {self.first_selected_value}({box1_name}) : {box2_xy}({box2_name})")
                            # 获取比较的结果
                            vs_res = game.piece_VS_piece(self.first_selected_value, box2_xy, self.all_pieces)
                            self.log.info(f"比较之后的结果: {vs_res}")
                            if vs_res[0] is False:
                                # 播放走棋错误的音效
                                if self.is_play is True:
                                    play_music.load_play_sound(setting.cw)
                                # 将拖动的棋子还原
                                box1_x = self.first_selected_value.split('_')[1]
                                box1_y = self.first_selected_value.split('_')[-1]
                                box1_local_x = int(box1_x) * setting.piece_size + setting.piece_first_x
                                box1_local_y = int(box1_y) * setting.piece_size + setting.piece_first_y
                                self.cv.coords(self.box_img_dict[self.first_selected_value], box1_local_x, box1_local_y)
                            self.log.info("=====两个棋子比较结束=====")
                            # 更新棋盘信息以及玩家状态
                            self.vs_result(vs_res[0], self.first_selected_value, box2_xy, box1_name, box2_name)
            # 棋子状态为False
            elif box2_state is False:
                # 按下和释放在同一个方格，打开当前方格的棋子
                if self.put_selected_value == box2_xy:
                    # 如果第一次的选择有值则清空，认为当前用户选择打开当前棋子
                    if self.first_selected_value is not None:
                        # 恢复第一次选择的状态
                        self.reset_first_state()
                    # 删除棋子背面图片
                    self.cv.delete(self.box_img_dict[box2_xy])
                    # 更新all_pieces中当前棋子的状态
                    self.all_pieces[box2_xy]['state'] = True
                    # 取得当前棋子的名称
                    box_key = box2_piece['box_key']
                    box_key = box_key[:-1]
                    piece_img = pieces_img[box_key]
                    # 显示当前棋子
                    piece_open = self.cv.create_image(box2_local_x, box2_local_y, image=piece_img, anchor=NW)
                    self.box_img_dict[box2_xy] = piece_open
                    # 播放选择棋子的音效
                    if self.is_play is True:
                        play_music.load_play_sound(setting.xz)
                    # 行棋完成，写入info文件
                    if self.isBreak is True:
                        self.write_str = "悔棋后行棋==>>"
                        self.isBreak = False
                    else:
                        self.write_str = "正常行棋==>>"
                    self.write_str += f"时间:{common.get_now_time()}|步数:{self.numCount}|总步数:{self.allCount}|"
                    self.write_str += f"行棋玩家:{self.nowPlayer}|行棋内容:"
                    self.write_str += f"打开棋子:[{box2_xy},{self.all_pieces[box2_xy]['box_key']}]"
                    common.write_file(filename=self.info_file, write_value=self.write_str)
                    common.write_file(filename=self.info_file, write_value=json.dumps(self.all_pieces))
                    common.write_file(filename=self.info_file, write_value=json.dumps(self.box_img_dict))
                    #
                    self.log.info(self.write_str)
                    # 行棋完成，更新界面玩家展示信息
                    self.upd_player_info(box_key)
                    self.log.info("打开棋子，更新玩家信息")
                    self.print_log()
                # 按下和释放不在同一个方格，该操作违规
                else:
                    # 播放走棋错误的音效
                    if self.is_play is True:
                        play_music.load_play_sound(setting.cw)
                    # 将拖动的棋子还原
                    box_put_state = self.all_pieces[self.put_selected_value]['state']
                    if box_put_state is True:
                        box1_x = self.put_selected_value.split('_')[1]
                        box1_y = self.put_selected_value.split('_')[-1]
                        box1_local_x = int(box1_x) * setting.piece_size + setting.piece_first_x
                        box1_local_y = int(box1_y) * setting.piece_size + setting.piece_first_y
                        self.cv.coords(self.box_img_dict[self.put_selected_value], box1_local_x, box1_local_y)
            # 棋子状态为None
            else:
                # 按下和释放在同一个方格，第一次的选择必须有值，才能走棋
                if self.put_selected_value == box2_xy and self.first_selected_value is not None:
                    # 赋值
                    box1_xy = self.first_selected_value
                    box1_name = self.all_pieces[box1_xy]['box_key']
                    box2_name = None
                    self.log.info("=====两个棋子开始比较=====")
                    self.log.info(
                        f"box1_xy(box1_name) : box2_xy(box2_name) ==> {box1_xy}({box1_name}) : {box2_xy}({box2_name})")
                    # 获取比较的结果
                    vs_res = game.piece_VS_piece(box1_xy, box2_xy, self.all_pieces)
                    self.log.info(f"比较之后的结果: {vs_res}")
                    if vs_res[0] is False:
                        # 播放走棋错误的音效
                        if self.is_play is True:
                            play_music.load_play_sound(setting.cw)
                    self.log.info("=====两个棋子比较结束=====")
                    # 更新棋盘信息以及玩家状态
                    self.vs_result(vs_res[0], box1_xy, box2_xy, box1_name, box2_name)
                # 按下和释放不在同一个方格，表示鼠标有拖动
                else:
                    # 判断鼠标按下时的方格状态
                    box_put_piece = self.all_pieces[self.put_selected_value]
                    box_put_state = box_put_piece['state']
                    # 按下时的状态为True，才能把按下时的方格坐标给第一次选择
                    if box_put_state is True:
                        # 取按下时方格中棋子的颜色方阵
                        box_put_color = box_put_piece['box_key'].split('_')[0]
                        # 必须为自己方阵颜色的棋子才允许拖动
                        if (self.player1Color == box_put_color and self.nowPlayer == self.player1) or \
                                (self.player2Color == box_put_color and self.nowPlayer == self.player2):
                            # 将按下时的方格坐标给第一次的选择
                            self.first_selected_value = self.put_selected_value
                            box1_name = self.all_pieces[self.first_selected_value]['box_key']
                            box2_name = box2_piece['box_key']
                            self.log.info("=====两个棋子开始比较=====")
                            self.log.info(
                                f"box1_xy(box1_name) : box2_xy(box2_name) ==> {self.first_selected_value}({box1_name}) : {box2_xy}({box2_name})")
                            # 获取比较的结果
                            vs_res = game.piece_VS_piece(self.first_selected_value, box2_xy, self.all_pieces)
                            self.log.info(f"比较之后的结果: {vs_res}")
                            if vs_res[0] is False:
                                # 播放走棋错误的音效
                                if self.is_play is True:
                                    play_music.load_play_sound(setting.cw)
                                # 将拖动的棋子还原
                                box1_x = self.first_selected_value.split('_')[1]
                                box1_y = self.first_selected_value.split('_')[-1]
                                box1_local_x = int(box1_x) * setting.piece_size + setting.piece_first_x
                                box1_local_y = int(box1_y) * setting.piece_size + setting.piece_first_y
                                self.cv.coords(self.box_img_dict[self.first_selected_value], box1_local_x, box1_local_y)
                            self.log.info("=====两个棋子比较结束=====")
                            # 更新棋盘信息以及玩家状态
                            self.vs_result(vs_res[0], self.first_selected_value, box2_xy, box1_name, box2_name)
            # 判断游戏是否结束
            self.game_over()
            # 使用player2的AI功能
            self.player2_ai(depth=self.depth)

    # 处理棋子对比结果，更改棋盘上的棋子格局
    def vs_result(self, vs_res, box1_xy, box2_xy, box1_name, box2_name):
        if vs_res is False:
            # 恢复第一次选择的状态
            self.reset_first_state()
            return False
        else:
            if vs_res is True:
                # 更新图片
                if box2_name is not None:
                    self.cv.delete(self.box_img_dict[box2_xy])
                #
                box_local_x = int(box2_xy.split('_')[1]) * setting.piece_size + setting.piece_first_x
                box_local_y = int(box2_xy.split('_')[-1]) * setting.piece_size + setting.piece_first_y
                self.box_img_dict[box2_xy] = self.box_img_dict[box1_xy]
                self.cv.coords(self.box_img_dict[box1_xy], box_local_x, box_local_y)
                self.box_img_dict[box1_xy] = None
                # 更新all_pieces
                self.all_pieces[box1_xy]['box_key'] = None
                self.all_pieces[box1_xy]['state'] = None
                self.all_pieces[box2_xy]['box_key'] = box1_name
                self.all_pieces[box2_xy]['state'] = True
            elif vs_res is None:
                # 更新图片
                self.cv.delete(self.box_img_dict[box1_xy])
                self.cv.delete(self.box_img_dict[box2_xy])
                self.box_img_dict[box1_xy] = None
                self.box_img_dict[box2_xy] = None
                # 更新all_pieces
                self.all_pieces[box1_xy]['box_key'] = None
                self.all_pieces[box1_xy]['state'] = None
                self.all_pieces[box2_xy]['box_key'] = None
                self.all_pieces[box2_xy]['state'] = None
            # 加载吃棋音效
            if self.is_play is True:
                if box2_name is not None:
                    play_music.load_play_sound(setting.cq)
                else:
                    play_music.load_play_sound(setting.zqwc)
            # 棋子走到方格代表走动了一步，则allCount则要加1
            str1 = '吃棋'
            if box2_name is None:
                self.allCount += 1
                str1 = '移动'
            # 走棋成功，写入info文件
            if self.isBreak is True:
                self.write_str = "悔棋后行棋==>>"
                self.isBreak = False
            else:
                self.write_str = "正常行棋==>>"
            self.write_str += f"时间:{common.get_now_time()}|步数:{self.numCount}|总步数:{self.allCount}|"
            self.write_str += f"行棋玩家:{self.nowPlayer}|行棋内容:"
            self.write_str += f"{str1}:[{box1_xy},{box1_name}]:[{box2_xy},{box2_name}]"
            common.write_file(filename=self.info_file, write_value=self.write_str)
            common.write_file(filename=self.info_file, write_value=json.dumps(self.all_pieces))
            common.write_file(filename=self.info_file, write_value=json.dumps(self.box_img_dict))
            self.log.info(self.write_str)
            # 恢复第一次选择的状态
            self.reset_first_state()
            # 更新playerinfo
            self.upd_player_info(f"{self.player1Color}_{self.player2Color}")
            self.log.info(f"{str1}:两个棋子对比结束，恢复第一次状态，更新玩家信息")
            self.print_log()
            return True

    # 为游戏结束处理玩家信息展示
    def game_over(self, is_ai_lost=False):
        # 用numCount和allCount比较，num比all大的时候才会进入判断是否游戏结束
        if self.numCount >= self.allCount:
            if is_ai_lost is True:
                is_over = self.player1Color
            else:
                is_over = game.is_game_over(self.all_pieces, self.nowPlayer, self.player1Color)
            # is_over的结果为'red', 'black', 'none', 'tie'
            self.log.info(f"游戏结束判断结果: {is_over}")
            if is_over == 'none':
                pass
            else:
                write_won = ''
                if is_over == 'red' or is_over == 'black':
                    if self.player1Color == is_over:
                        self.log.info(f"本局游戏结束！！玩家1：{setting.player1_name} {is_over}  胜利!")
                        self.totalCount += 1
                        self.Player1WonCount += 1
                        write_won += f"恭喜玩家：{setting.player1_name} 胜利!"
                    else:
                        self.log.info(f"本局游戏结束！！玩家2：{setting.player2_name} {is_over} 胜利!")
                        self.totalCount += 1
                        self.Player2WonCount += 1
                        write_won += f"恭喜玩家：{setting.player2_name} 胜利!"
                elif is_over == 'tie':
                    self.log.info(f"本局游戏结束！！本局游戏为平局!")
                    self.totalCount += 1
                    self.tieCount += 1
                    write_won += f"本局游戏为平局!"
                # 走棋成功，写入info文件
                self.write_str = f"正常行棋==>>时间:{common.get_now_time()}|步数:{self.numCount}|总步数:{self.allCount}|"
                self.write_str += f"当前第{self.totalCount}局游戏结束！{write_won}"
                end_str = "*" * 20 + f"第{self.totalCount + 1}局游戏开始！！" + "*" * 20
                common.write_file(filename=self.info_file, write_value=self.write_str)
                common.write_file(filename=self.info_file, write_value=end_str)
                self.log.info(self.write_str)
                # 重新开始游戏，重置各个参数
                self.reset_game_start(write_won)

    # 为player2添加AI智能走棋
    def player2_ai(self, depth):
        if self.nowPlayer == self.player2 and self.is_player_vs_computer is True:
            is_ai_lost = False
            # 玩家2正在走棋时禁止玩家1在棋盘上操作，锁定玩家1
            self.lock_player1 = True
            # 计算AI走棋消耗的时间
            t_start = timeit.default_timer()
            best_move = seach_move.search_next_move(self.all_pieces, self.player1Color, depth)
            t_time = timeit.default_timer() - t_start
            # 对AI的最佳走棋步骤判断
            if best_move is not None:
                self.log.info(f'系统player2的选择是：{best_move.box_from}==>>{best_move.box_action}==>>{best_move.box_to}')
                box_xy = best_move.box_to.split('_')
                box_x = box_xy[1]
                box_y = box_xy[-1]
                # 设置定时器对player2走棋设置延迟时间，默认2s
                if t_time <= setting.player2_thinktime:
                    t_time = setting.player2_thinktime
                timer = threading.Timer(t_time, self.pieces_action, (box_x, box_y, best_move.box_from))
                timer.start()
            else:
                msg = '玩家2（电脑）已无棋子可走，自动认输！\n点击确定按钮开始下一局游戏！'
                messagebox.showinfo(title='游戏结束', message=msg)
                is_ai_lost = True
                self.log.info('玩家2（电脑）已无棋子可走，自动认输！')
            # 判断游戏是否结束
            self.game_over(is_ai_lost)
            # 释放玩家1的锁定
            self.lock_player1 = False

    # 关闭窗口事件
    def close_window(self):
        dialog_value = {
            'title': '退出游戏',
            'text': '游戏正在进行中，确定要退出吗？',
            'bitmap': 'question',
            'default': 0,
            'strings': ('确定', '取消')
        }
        d = dialog.Dialog(self.master, dialog_value)
        if d.num == 0:
            # 退出系统之前记录本轮游戏的结果
            game_end_time = datetime.now()
            # 游戏共经历了多少时长
            how_long = common.how_long_time(self.game_begin_time, game_end_time)
            # 记录游戏局数和胜利的玩家信息
            game_over_str = "*" * 20
            game_over_str += f"本轮游戏时长为{how_long}，总共完成{self.totalCount}局"
            if self.totalCount != 0:
                if self.Player1WonCount > self.Player2WonCount:
                    game_over_str += f"，其中[{setting.player1_name}]技高一筹，胜 {self.Player1WonCount} 局"
                elif self.Player1WonCount < self.Player2WonCount:
                    game_over_str += f"，其中[{setting.player2_name}]技高一筹，胜 {self.Player2WonCount} 局"
                else:
                    game_over_str += f"，两位玩家旗鼓相当，均胜 {self.Player1WonCount} 局"
                if self.tieCount != 0:
                    game_over_str += f"，打平 {self.tieCount} 局"
            game_over_str += "*" * 20
            common.write_file(filename=self.info_file, write_value=game_over_str)
            self.log.info(game_over_str)
            #
            play_music.quit_music()
            self.log.info("游戏退出！")
            self.master.destroy()

if __name__ == '__main__':
    # 整个游戏的入口
    root = Tk()
    # 设置标题
    root.title(setting.game_title)
    # 设置图标
    root.iconbitmap(setting.favicon)
    # 设置窗体固定大小，并设置不能改变大小
    root.geometry(f"{setting.screen_width}x{setting.screen_height}+{setting.window_start_x}+{setting.window_start_y}")
    root.resizable(width=False, height=False)
    # 加载棋盘图片（Canvas的bug，PhotoImage只能和mainloop放一起，不然加载不出图片）
    board_img = PhotoImage(file=setting.chess_board)
    # 加载棋子背面图片，需要改变一下棋子的大小，使用了pil里面的Image和ImageTk
    pieces_back_img = common.change_img(setting.pieces_back)
    # 加载棋子选中时的颜色图片
    piece_selected_img = PhotoImage(file=setting.piece_selected)
    # 加载关于窗体中的favicon图标
    red_jiang_img = common.change_img('images/piece_red_jiang.gif', width=80, height=80)
    black_jiang_img = common.change_img('images/piece_black_jiang.gif', width=80, height=80)
    # 加载所有棋子图片
    pieces_dict = game.get_piece_image()
    pieces_img = common.change_img(img=pieces_dict)
    # 加载vs图片
    vs_img = common.change_img(setting.vs_image, width=80, height=80)
    # 加载win图片
    win_img = common.change_img(setting.win_image, width=145, height=145)
    # 加载背景音乐
    play_music.is_not_busy()
    #
    chess = Chess(master=root)
    root.protocol('WM_DELETE_WINDOW', chess.close_window)
    root.mainloop()
