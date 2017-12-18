#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

import re
import json
import pickle
from . import exceptions
from .parselib import AssParse
from .subase import Sub
from .utils import rubi
from .utils import data as data_utils
from .utils import validators


VERSION = (0, 1, 1)
__version__ = ".".join(map(str, VERSION))


class Ass(Sub):
    """Ass Subtitle base class"""
    __script_header = "Script Info"
    __garbage_header = "Aegisub Project Garbage"
    __style_header = "V4+ Styles"
    __event_header = "Events"

    __format = "Format"
    __version = "v4.00+"
    VERSION = __version__  # 解析器版本

    def __init__(self):
        super(Ass, self).__init__()
        # 整个内容的字典
        self.text_dict = {
            self.__script_header: None,
            self.__garbage_header: None,
            self.__style_header: None,
            self.__event_header: None,
            "furigana": 0,
            "apires_count": 0,
            "version": self.VERSION,
        }
        self.__text_list = []  # 文本列表

    def reset(self):
        """重置数据"""
        self.text = ''
        self.__text_list = []
        self.text_dict = {
            self.__script_header: None,
            self.__garbage_header: None,
            self.__style_header: None,
            self.__event_header: None,
            "furigana": 0,
            "version": self.VERSION,
        }

    @property
    def scripts(self):
        """脚本信息（dict）"""
        return self.text_dict[self.__script_header]

    @property
    def styles(self):
        """字幕样式信息（dict）"""
        return self.text_dict[self.__style_header]

    @property
    def garbages(self):
        """字幕非重要脚本信息（dict）"""
        return self.text_dict[self.__garbage_header]

    @property
    def events(self):
        """字幕事件信息（dict）"""
        return self.text_dict[self.__event_header]

    @property
    def default_script_order(self):
        """字幕默认脚本标题顺序（list）"""
        return AssParse.SCRIPT_DEFAULT_ORDER

    @property
    def default_garbage_order(self):
        """字幕默认非重要脚本标题顺序（list）"""
        return AssParse.GARBAGE_DEFAULT_ORDER

    @property
    def style_format(self):
        """字幕样式格式（list）"""
        return self.text_dict[self.__style_header].get("format")

    @property
    def style_names(self):
        """字幕所有样式名称(list)"""
        return self.text_dict[self.__style_header].get("style_name")

    @property
    def style_(self):
        """字幕脚本样式内容（dict）"""
        return self.text_dict[self.__style_header].get("style")

    @property
    def style_uid(self):
        """字幕脚本样式uid，用于排序（list）"""
        return self.text_dict[self.__style_header].get("order")

    @property
    def event_format(self):
        """字幕事件格式（list）"""
        return self.text_dict[self.__event_header].get("format")

    @property
    def event_(self):
        """字幕事件内容（dict）"""
        return self.text_dict[self.__event_header].get("event")

    @property
    def event_uid(self):
        """字幕事件uid，用于排序（list）"""
        return self.text_dict[self.__event_header].get("order")

    @property
    def event_line_num(self):
        """字幕事件行数（int）"""
        return len(self.text_dict[self.__event_header].get("order"))

    @property
    def apires_count(self):
        """使用假名标注时调用yahoo api的次数（int）"""
        return self.text_dict["apires_count"]

    @property
    def is_furigana(self):
        """是否进行过假名标注（boolean）"""
        return bool(self.text_dict["furigana"])

    @property
    def verison(self):
        """解析器当前版本号"""
        return self.VERSION

    def from_file(self, path, encoding="utf-8", format=None, *args, **kwargs):
        """从文件中读取字幕内容"""
        self.text = data_utils.from_file(path, encoding)
        # 清理文件bom
        self.text = data_utils.clear_bom(self.text)
        # 验证字幕类型
        self.__format_validator()
        self.__split()

    def from_str(self, text, format=None, *args, **kwargs):
        """从字符串中读取字幕内容"""
        # 清理文件bom
        self.text = data_utils.clear_bom(text)
        # 验证字幕类型
        self.__format_validator()
        self.__split()

    def from_bytes(self, content, encoding="utf-8", format=None, *args, **kwargs):
        """从二进制中获取字幕内容"""
        self.text = data_utils.from_bin(content, encoding)
        # 清理文件bom
        self.text = data_utils.clear_bom(self.text)
        # 验证字幕类型
        self.__format_validator()
        self.__split()

    def from_json(self, data, *args, **kwargs):
        """导入json数据"""
        self.text_dict = json.loads(data)

    def from_pickle(self, data, *args, **kwargs):
        """导入pickle数据"""
        self.text_dict = pickle.loads(data)

    def parse_all(self, *args, **kwargs):
        """解析全部"""
        head_act_dict = {
            self.__script_header: AssParse.script,
            self.__garbage_header: AssParse.garbage,
            self.__style_header: AssParse.style,
            self.__event_header: AssParse.event,
        }
        start_index = 0
        import time
        while True:
            ts = self.__get_start_index(start_index)
            if not ts: break  # 如果找不到标题，说明已经全部解析完毕
            self.text_dict[ts[0]], start_index = head_act_dict[ts[0]](self.__text_list, ts[1])

    def parse_script(self, *args, **kwargs):
        """解析Script Info"""
        # 获取起始下标
        ts = self.__get_start_index(obj_title=self.__script_header)
        if not ts: return

        self.text_dict[self.__script_header], end_index = AssParse.script(self.__text_list, ts[1])
        return end_index

    def parse_garbages(self, *args, **kwargs):
        """解析garbages"""
        ts = self.__get_start_index(obj_title=self.__garbage_header)
        if not ts: return

        self.text_dict[self.__garbage_header], end_index = AssParse.garbage(self.__text_list, ts[1])
        return end_index

    def parse_style(self, *args, **kwargs):
        """解析style"""
        ts = self.__get_start_index(obj_title=self.__style_header)
        if not ts: return

        self.text_dict[self.__style_header], end_index = AssParse.style(self.__text_list, ts[1])
        return end_index

    def parse_event(self, *args, **kwargs):
        """解析event"""
        ts = self.__get_start_index(obj_title=self.__event_header)
        if not ts: return

        self.text_dict[self.__event_header], end_index = AssParse.event(self.__text_list, ts[1])
        return end_index

    def furigana(self, style_name, appid=None, garde=1, *args, **kwargs):
        """进行假名标注"""
        # 验证是否已经存在已经解析完成的style和event内容
        if not self.styles or not self.events:
            raise exceptions.NoExists("无法进行假名标注，原因：没有找到styles和events")
        # 验证目标样式
        style_name = validators.style_name_validator(style_name, self.style_names)
        rubi.furigana(ass=self, appid=appid, style_name=style_name, garde=garde)
        pass

    def as_json(self, *args, **kwargs):
        """返回json序列号数据"""
        return json.dumps(self.text_dict)

    def as_pickle(self, *args, **kwargs):
        """返回pickle序列号数据"""
        return pickle.dumps(self.text_dict)

    def as_str(self, furigana=False, *args, **kwargs):
        """返回str字幕内容"""
        return "\n".join(self.as_textlines(furigana))

    def as_textlines(self, furigana=False, *args, **kwargs):
        """返回列表形式的反解析结束的text"""
        textlines = []
        # 反解析Sript info
        textlines.extend(self.rev_script_lines())
        textlines.append("")
        # 反向解析Garbage
        textlines.extend(self.rev_garbage_lines())
        textlines.append("")
        # 反向解析Style
        textlines.extend(self.rev_style_lines())
        textlines.append("")
        # 反向解析event
        textlines.extend(self.rev_event_lines(furigana))
        return textlines

    def as_bin(self, encoding="utf-8", *args, **kwargs):
        """返回二进制字幕内容"""
        return self.as_str().encode(encoding)

    def save2file(self, path, furigana=False, encoding="utf-8", *args, **kwargs):
        """保存到文件中"""
        with open(path, 'w', encoding=encoding) as f:
            f.write(self.as_str(furigana))

    def rev_script_lines(self):
        """对script info进行逆向解析"""
        textlines = []
        if self.scripts:
            textlines.append("[%s]" % self.__script_header)

            for key in AssParse.SCRIPT_DEFAULT_ORDER:
                if key in self.scripts:
                    if key == ";":
                        textlines.extend(
                            ["; %s" % value for value in self.scripts[";"]["value"]])
                    else:
                        textlines.append("%s: %s" % (key, self.scripts[key]["value"]))
        return textlines

    def rev_garbage_lines(self):
        """对garbage进行逆向解析"""
        textlines = []
        if self.garbages:
            textlines.append("[%s]" % self.__garbage_header)

            for key in self.default_garbage_order:
                if key in self.garbages:
                    if key == ";":
                        textlines.append("; %s" % self.garbages[key]["value"])
                    else:
                        textlines.append("%s: %s" % (key, self.garbages[key]["value"]))
        return textlines

    def rev_style_lines(self):
        """对style进行逆向解析"""
        textlines = []
        if self.styles:
            textlines.append("[%s]" % self.__style_header)
            textlines.append("Format: %s" % ", ".join(self.style_format))

            for uid in self.style_uid:
                tmp = ",".join([self.style_[uid][k] for k in self.style_format])
                textlines.append("Style: %s" % tmp)
        return textlines

    def rev_event_lines(self, furigana=False):
        """对event进行逆向解析"""
        textlines = []  # 事件内容

        # 生成Format行内容
        textlines.append("[%s]" % self.__event_header)
        textlines.append("Format: %s" % ", ".join(self.event_format))

        # 检查是否生成furigana格式的文本内容
        if furigana and self.is_furigana:
            self.event_format[-1] = "furigana"

        if self.events:
            tmp = self.text_dict[self.__event_header]
            for uid in self.event_uid:
                txt = ",".join([self.event_[uid][k] for k in self.event_format[:-1]])
                if furigana and "furigana" in self.event_[uid]:
                    txt = "%s,%s" % (txt, self.event_[uid]["furigana"])
                else:
                    txt = "%s,%s" % (txt, self.event_[uid]["Text"])

                textlines.append("%s: %s" % (self.event_[uid]["Format"], txt))

        if furigana and self.is_furigana:
            self.event_format[-1] = "Text"
        return textlines

    def __format_validator(self, *args, **kwargs):
        """验证字幕内容是否是合法的ASS格式"""
        if not validators.ass_vali(self.text):
            raise exceptions.SubFormatError("非ASS字幕格式内容")

    def __split(self, *args, **kwargs):
        """将text转换为列表"""
        self.__text_list = self.text.splitlines()

    def __get_start_index(self, start_index=0, obj_title=None, *args, **kwargs):
        """获取内容的起始下标"""
        for num, line in enumerate(self.__text_list[start_index:], start=start_index):
            if obj_title:
                if obj_title == self.__style_header:
                    re_res = re.search(r"\A\[V4\+ Styles\]\Z", line)
                else:
                    re_res = re.search(r"\A\[%s\]\Z" % obj_title, line)
                if re_res:
                    return obj_title, num + 1
            else:
                re_res = re.search(r"\A\[(?P<title>[\w\s+]+)\]\Z", line)
                if re_res:
                    title = re_res.groupdict().get("title")
                    if title in self.text_dict:
                        return title, num + 1