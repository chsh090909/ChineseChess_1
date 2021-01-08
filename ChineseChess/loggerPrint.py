#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  loggerPrint.py
@time:  2020/3/7 12:02
@title:日志模块
@content:
"""
import logging, sys, time

class LoggerPrint(object):
    def __init__(self, setting):
        # 定义日志
        self.logger = logging.getLogger('main')
        self.logger.setLevel(level=logging.DEBUG)
        self.logger.propagate = False
        #
        self.setting = setting

    # 打印日志到系统控制台上
    def printLogToSystem(self, is_out_file=True):
        """
        :param is_out_file: True or False,定义是否同时写入日志文件，默认False
        :return: 返回logger
        """
        # 避免重复的创建handlers,导致打印重复的日志内容
        if not self.logger.handlers:
            # 打印到控制台
            stream_handler = logging.StreamHandler(sys.stdout)
            # 日志级别
            stream_handler.setLevel(self.setting.sysout_level.upper())
            # 日志格式
            sysout_format = logging.Formatter(self.setting.sysout_format)
            stream_handler.setFormatter(sysout_format)
            self.logger.addHandler(stream_handler)
            # 定义写入到日志文件
            if is_out_file is True:
                self.printLogToFile()
        # 返回logger
        return self.logger

    # 写日志到日志文件中
    def printLogToFile(self):
        """
        :return: 返回logger
        """
        # 避免重复的创建handlers,导致写入重复的日志内容
        # if not self.logger.handlers:
        # 将时间戳组合到log的文件名中
        filename = self.setting.log_file_name
        filename_list = filename.split('.')
        ntime = time.strftime('_%Y_%m_%d_%H_%M_%S')
        filename = f"{filename_list[0]}{ntime}.{filename_list[1]}"
        # 写入到日志文件
        file_handler = logging.FileHandler(filename=filename, encoding='utf-8')
        # 日志级别
        file_handler.setLevel(self.setting.file_write_level.upper())
        # 设置日志格式
        filewrite_format = logging.Formatter(self.setting.file_write_format)
        file_handler.setFormatter(filewrite_format)
        self.logger.addHandler(file_handler)
