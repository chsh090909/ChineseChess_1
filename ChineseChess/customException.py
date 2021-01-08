#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  customException.py
@time:  2020/3/25 14:59
@title:
@content:
"""

class ImgNotFound(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class FileNotFound(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
