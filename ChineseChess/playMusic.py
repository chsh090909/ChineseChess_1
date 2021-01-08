#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  playMusic.py
@time:  2020/3/20 16:21
@title:
@content:
"""
import pygame
import random
import threading
from loggerPrint import LoggerPrint

class PlayMusic():
    # 设置音乐播放标志：0表示自动播放，1表示手动介入
    _MUSIC_PLAY_FLAG = 0

    def __init__(self, setting):
        self.setting = setting
        self.logger = LoggerPrint(self.setting)
        self.log = self.logger.printLogToSystem()
        # 初始化混音器
        pygame.mixer.init()

        self.log.info("初始化混音器成功！")

    # 播放背景音乐
    def play_bg_music(self, music_file=None):
        # 如果music_file有值，则播放选中的音乐
        if music_file:
            pygame.mixer.music.stop()
            self.log.info(f"切换的背景音乐为: {music_file}")
        # 没有值则随机播放
        else:
            music_list = self.setting.music_list
            music_file = random.sample(music_list, 1)
            music_file = music_file[0]
            self.log.info(f"随机播放的音乐为: {music_file}")
        pygame.mixer.music.load(f'mids/{music_file}')
        pygame.mixer.music.play()
        PlayMusic._MUSIC_PLAY_FLAG = 0
        self.is_not_busy()

    # 播放一首音乐完成之后，自动随机播放下一首
    def is_not_busy(self):
        mixer_state = pygame.mixer.get_init()
        if mixer_state:
            # 如果播放器没有工作，则调用播放背景音乐功能方法
            if pygame.mixer.music.get_busy() == False and PlayMusic._MUSIC_PLAY_FLAG == 0:
                self.play_bg_music()
            else:
                if PlayMusic._MUSIC_PLAY_FLAG == 0:
                    # 定时器，没隔1s检查一次播放器是否有在播放
                    t = threading.Timer(1, self.is_not_busy)
                    t.start()
        else:
            pass

    # 手动停止背景音乐播放
    def stop_bg_music(self):
        mixer_state = pygame.mixer.get_init()
        if mixer_state:
            pygame.mixer.music.stop()
            self.log.info('背景音乐播放停止！')
            PlayMusic._MUSIC_PLAY_FLAG = 1

    # 加载操作棋子时的音效
    def load_play_sound(self, sound):
        soundobj = pygame.mixer.Sound(sound)
        soundobj.play()

    # 退出游戏的时候，需要先退出pygame和mixer播放器
    def quit_music(self):
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.quit()
        pygame.quit()
        self.log.info("混音器销毁成功！pygame退出！")
