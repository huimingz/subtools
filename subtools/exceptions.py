#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author: "Kairu"
# contact: 
# date: "2017/11/17"

class PySubError(Exception):
    """基本错误类型"""
    pass

class SubFormatError(PySubError):
    """字幕格式错误"""
    pass

class AssFilePathError(PySubError):
    """文件路径错误"""
    pass

class AssParseError(PySubError):
    """解析Ass内容时发生错误"""
    pass

class NoExists(PySubError):
    """没有找到目标对象"""
    pass

class RequestError(PySubError):
    """请求错误"""
    pass
