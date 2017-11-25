#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

from .. import exceptions

formats = ("ASS", "SSA", "STR")

def ass_vali(text):
    """
    验证是否为合法ASS字幕内容

    :param text: 文本内容
    :return: True|False
    """
    if "V4+ Styles" in text:
        return True
    else:
        return False

def ssa_vali(text):
    """
    验证是否为合法SSA字幕内容

    :param text: 文本内容
    :return: True|False
    """
    if "V4 Styles" in text:
        return True
    else:
        return False

def get_format(text):
    """
    获取字幕格式

    :param text: 文本内容
    :return: ASS|SSA|None
    """
    if "V4+ Styles" in text:
        return "ASS"
    elif "V4 Styles" in text:
        return "SSA"

def style_name_validator(style_name, style_lib):
    """
    验证目标样式是否有效

    :param style_name: 目标样式（可迭代对象或者字符串格式）
    :param style_lib: 样式仓库
    :return: 一个包含有效样式的列表或者None
    """
    from collections import Iterable
    if isinstance(style_name, list):
        style_name = [name for name in style_name if name in style_lib]
        if not style_name:
            raise exceptions.NoExists("没有找到可匹配的样式名")
    elif isinstance(style_name, str):
        if style_name not in style_lib:
            raise exceptions.NoExists("没有找到可匹配的样式名")
        style_name = [style_name]
    else:
        raise exceptions.NoExists("没有找到可匹配的样式名")
    return style_name