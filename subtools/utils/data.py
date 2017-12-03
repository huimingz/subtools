#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

import os
import re
import chardet
# import codecs
from subtools import exceptions




def get_encoding(content, *args, **kwargs):
    """从unicode内容中获取编码"""
    from chardet.universaldetector import UniversalDetector

    # 创建一个检测对象
    detector = UniversalDetector()
    for line in content.splitlines():
        # 分块进行测试，直到达到阈值
        detector.feed(line)
        if detector.done: break
    # 关闭检测对象
    detector.close()
    return detector.result.get("encoding")

def from_bin(content, encoding, *args, **kwargs):
    """从二进制中获取字幕文本内容"""
    if isinstance(content, bytes):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            return content.decode(encoding=get_encoding(content[:10000]))
    return content

def from_file(path, encoding, *args, **kwargs):
    """从文件中获取字幕文本内容"""
    if os.path.isfile(path):
        f = open(path, 'rb')
        content = f.read()
        f.close()
        # content = open(path, "rb").read()
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            # 如果指定编码无法解码文件内容，则尝试自动获取编码
            return content.decode(encoding=get_encoding(content[:10000]))
    else:
        raise exceptions.AssFilePathError("路径不存在，无法读取文件内容")

def clear_bom(text):
    """清理文件头的bom"""
    return text.lstrip("\ufeff")








