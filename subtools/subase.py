#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"


class Sub(object):
    def __init__(self):
        self.text = ""

    def from_file(self, path, encoding="utf-8", format=None, *args, **kwargs):
        """从文件中读取字幕内容"""
        pass

    def from_str(self, text, format=None, *args, **kwargs):
        """从字符串中读取字幕内容"""
        pass

    def from_bin(self, content, encoding="utf-8", format=None, *args, **kwargs):
        """从二进制中获取字幕内容"""
        pass

    def as_json(self):
        """返回json序列号数据"""
        pass

    def as_pickle(self):
        """返回pickle序列号数据"""
        pass

    def as_str(self):
        """返回str字幕内容"""
        pass

    def as_bin(self):
        """返回二进制字幕内容"""
        pass






