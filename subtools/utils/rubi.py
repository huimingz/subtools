#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

"""调用雅虎的API接口，对汉字进行假名标注"""

import json
import requests
import xmltodict
import copy
import uuid
import re
import urllib.request
from collections import OrderedDict
from subtools import exceptions


YAHOO_API_URL = "https://jlp.yahooapis.jp/FuriganaService/V1/furigana"
DATA_SIZE_LIMIT = 25 * 1024  # 单次上传最大20KB

# 标记每段文本的uid
# UID_SYMBOL = "{#uid-%(uid)s#}%(text)s"

# 各段文本内容的分割符
BREAK_SYMBOL = "{#br#}"
BREAK_SYMBOL_BYTES = b"{#br#}"

# 换行符
SP = {
    "{#sp1#}": " ",
    "{#sp2#}": "　",
    "{#sp3#}": "	",
    "{#sp4#}": "\u3000",
}

# 将会自动替换文本内的特殊字符，防止报错
CHAR_AMENT = {
    # "会报错的字符": "替换后的字符"
    "〝": '"',
    "〞": '"',
    "✕": "X",
}

# Aegisub自动注音卡拉OK脚本
FURI_EVENT =[
    {
        "Format": "Comment",
        "Layer": "0",
        "Start": "0:00:00.00",
        "End": "0:00:00.00",
        "Style": "Default",
        "Name": "",
        "MarginL": "0",
        "MarginR": "0",
        "MarginV": "0",
        "Effect": "template furi",
        "Text": r"{\pos(!line.left+syl.center!,!line.middle-line.height!)\an5\k!syl.start_time/10!\k$kdur}",
    },
    {
        "Format": "Comment",
        "Layer": "0",
        "Start": "0:00:00.00",
        "End": "0:00:00.00",
        "Style": "Default",
        "Name": "",
        "MarginL": "0",
        "MarginR": "0",
        "MarginV": "0",
        "Effect": "template syl",
        "Text": r"{\pos(!line.left+syl.center!,!line.middle!)\an5\k!syl.start_time/10!\k$kdur}",
    }
]


def add_furi_karacode(ass, style_name):
    """
    添加卡拉OK注音脚本

    :param ass:
    :param style_name:
    :return:
    """
    tmp = ass.text_dict[ass._Ass__event_header]
    # 添加所有目标样式的注音脚本
    for style in style_name:
        for event in FURI_EVENT:
            event["Style"] = style
            # 生成uid，并确保uid是在order里是唯一的
            while True:
                uid = uuid.uuid4().hex[-6:]
                if uid not in tmp["order"]: break
            # 添加uid
            tmp["order"].insert(0, uid)
            # 添加脚本事件
            tmp["event"][uid] = event

def yahoo_rubi(text, appid, grade=1, *args, **kwargs):
    """
    利用yahoo API进行假名标注

    :param text:
    :param appid:
    :param grade:
    :param args:
    :param kwargs:
    :return:
    """
    # print(len(text))
    data = {
        "appid": appid,  # APPID
        "grade": str(grade),  # 等级(1-8)
        "sentence": text,  # 对象文本
    }
    try:
        request = requests.post(YAHOO_API_URL, data=data)
    except Exception:
        return
    else:
        # 如果返回状态码非200，触发异常
        if request.status_code != 200:
            raise exceptions.RequestError("提交data到yahoo时发生错误，原因：%s" % request.reason)
        return xmltodict.parse(request.content.decode("utf-8"))

def parse_ord(xml_dict):
    """
    提取OrderedDict内的有效信息，并存放到列表内

    :param xml_dict:
    :return:
    """
    reversed_ = []
    for key in xml_dict["ResultSet"]["Result"]["WordList"]["Word"]:
        rubi = {"rubi": {}}
        if "Furigana" not in key:
            reversed_.append(key["Surface"])
            continue
        if "SubWordList" in key:
            for ckey in key["SubWordList"]["SubWord"]:
                if ckey.get("Furigana") and ckey["Surface"] != ckey["Furigana"]:
                    reversed_.append("{\k0}%s|%s{\k0}" % (ckey["Surface"], ckey["Furigana"]))
                    continue
                reversed_.append(ckey["Surface"])
        else:
            reversed_.append("{\k0}%s|%s{\k0}" % (key["Surface"], key["Furigana"]))
    return reversed_

def rev_ord2text(reverse_):
    """
    反向处理，获取每段内容的uid和Text

    :param reverse_:
    :return:
    """
    furi_list = []
    text = ""
    # 生成文本
    for t in reverse_:
        # 处理None类型
        while True:
            if None in t:
                t[t.index(None)] = " "
                continue
            break

        text = "%s%s" % (text, "".join(t))

    # 还原空格
    for k in SP:
        text = text.replace(k, SP[k])

    # 根据分隔符分割文本
    text_lines = text.split("{#br#}")
    # 解析每段内容，提取uid和Text
    for line in text_lines:
        if not line:
            continue
        res = re.search(r"^\{#uid-(?P<uid>[0-9a-fA-F]+)#\}(?P<furigana>.*)$", line)
        if not res:
            raise exceptions.AssParseError("反向解析时发生错误")
        res = res.groupdict()
        furi_list.append(res)

    return furi_list

def to_rubitext(ass, text_list, appid="", style_name=[], grade=1, *args, **kwargs):
    reversed_ = []
    for text in text_list:
        reversed_.append(parse_ord(yahoo_rubi(text, appid, grade)))
    # 逆向工程
    furi_list = rev_ord2text(reversed_)
    # 添加注音的文本
    for furi in furi_list:
        ass.event_[furi["uid"]]["furigana"] = furi["furigana"]
    # 添加注音提示
    ass.text_dict["furigana"] = 1
    # 添加Aegisub卡拉OK脚本
    add_furi_karacode(ass, style_name)

def get_event(ass, style_name):
    """
    提取文本内容，并根据内容大小进行分组，以便适应
    YAHOO API单次上传内容大小限制。

    :param ass: Ass实例化对象
    :param style_name: 目标样式（list）
    :return: 文本列表
    """
    # 目标事件
    obj_events = OrderedDict()
    for uid in ass.event_uid:
        # 只处理Dialogue，遇到其他Format则跳过
        if ass.event_[uid]["Format"] != "Dialogue":
            continue

        # 遍历event，如果Style在style_name里面，则添加到目标事件中
        if ass.event_[uid]["Style"] in style_name:
            # 拷贝目标内容
            obj_events[uid] = copy.deepcopy(ass.event_[uid])

    # 处理获取到的目标事件的文本内容
    text_list = []
    text_temp = []
    for uid in obj_events:
        text = "{#uid-%(uid)s#}%(text)s" % {"uid": uid, "text": obj_events[uid]["Text"]}
        # 替换空格，防止报错
        for k in SP:
            text = text.replace(SP[k], k)
        # 替换非法字符
        for char in CHAR_AMENT:
            text = text.replace(CHAR_AMENT[char], char)
        # print(text)
        # 提前转换为bytes内容，方便之后进行长度预测
        try:
            # text.encode("utf-8").decode("shift-JIS")
            text.encode("shift-JIS")
        except (UnicodeEncodeError, UnicodeDecodeError):
            # print("非法内容：", text)
            continue
        text_temp.append(text.encode("utf-8"))

    # 对文本进行分组，保证每组数据容量不会过大
    packet_text = b""
    for num, text in enumerate(text_temp, 1):
        if num == len(text_temp):
            # 如果是列表的最后一项，则不考虑在后面加入换行分割符号
            packet_text = b"%s%s" % (packet_text, text)
            continue
        packet_text = b"%s%s%s" % (packet_text, text, BREAK_SYMBOL_BYTES)

        if (len(packet_text)) >= DATA_SIZE_LIMIT:
            # 如果数据容量达到指定限额，则将该组内容加入到text_list中
            text_list.append(packet_text)
            packet_text = b""  # 清空packet text
    # 检查packet text内是否有残余内容
    if packet_text:
        text_list.append(packet_text)

    return text_list

def furigana(ass, appid="", style_name=[], grade=1, *args, **kwargs):
    """
    给字幕注音

    :param ass: Ass实例化对象
    :param style_name: 经过处理的目标样式名
    :param appid: 雅虎appid
    :param grade: 注音等级(1-8)
    :param args:
    :param kwargs:
    :return:
    """
    text_list = get_event(ass, style_name)
    to_rubitext(ass, text_list, appid, style_name, grade)