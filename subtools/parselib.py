#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

import re
import uuid
from .utils.field import Field
from . import exceptions

class AssParse(object):
    SCRIPT_DEFAULT_ORDER = (
        ";",
        "Title",
        "Original Script",
        "Original Translation",
        "Original Editing",
        "Original Timing",
        "Synch Point",
        "Script Updated By",
        "Update Details",
        "ScriptType",
        "PlayResX",
        "PlayResY",
        "PlayDepth",
        "Timer",
        "Video Zoom",
        "YCbCr Matrix",
        "Scroll Position",
        "Active Line",
        "Collisions",
        "WrapStyle",
        "ScaledBorderAndShadow",
        "Audio URI",
        "Audio File",
        "Video File",
        "Video Aspect Ratio",
        "Video Position",
        "Video Zoom Percent",
        "Last Style Storage",
        "Video AR Mode",
        "Video AR Value",
    )
    GARBAGE_DEFAULT_ORDER = SCRIPT_DEFAULT_ORDER

    def __init__(self):
        pass

    @staticmethod
    def script(textlist, start_index=0, set_default=True, *args, **kwargs):
        """
        解析Script的内容，不包含[Script Info]行。

        使用方法：
        你需要传入一个文本列表，已经指定一个起始的列表下标，方便解析。如
        果传入一个错误的列表下标，那么可能会返回一个期望以外的结果。

        将会将内容解析为键值对存放到字典内，考虑到";"键的特殊性，其内容为
        列表。

        如何判断该项内容结束：
        根据start_index开始循环textlist，直到遇到空行或者[xxx]内容
        行。

        :param textlist: 字幕文本列表
        :param start_index: 起始下标
        :param set_default: 是否设置默认值
        :param args:
        :param kwargs:
        :return: 解析到的该项数据和结束下标
        """
        SCRIPT_INFO = {
            ";": Field(r";\s?", r".*", "注释"),
            "Title": Field(r"[\w\s]+:\s?", r".*", "标题"),
            "Original Script": Field(r"[\w\s]+:\s?", r".*", "脚本原作"),
            "Original Translation": Field(r"[\w\s]+:\s?", r".*", "原译者"),
            "Original Editing": Field(r"[\w\s]+:\s?", r".*", "原编辑者"),
            "Original Timing": Field(r"[\w\s]+:\s?", r".*", "原时间轴作者"),
            "Synch Point": Field(r"[\w\s]+:\s?", r".*", "加载起始点"),
            "Script Updated By": Field(r"[\w\s]+:\s?", r".*", "更新人员"),
            "Update Details": Field(r"[\w\s]+:\s?", r".*", "更新摘要"),
            "ScriptType": Field(r"[\w\s]+:\s?", r"v4\.00+", "脚本类型"),
            "PlayResX": Field(r"[\w\s]+:\s?", r"\d{1,4}", "分辨率(宽)"),
            "PlayResY": Field(r"[\w\s]+:\s?", r"\d{1,4}", "分辨率(高)"),
            "PlayDepth": Field(r"[\w\s]+:\s?", r".*", "颜色深度"),
            "Timer": Field(r"[\w\s]+:\s?", r"[\d\.,]+", "加载速度"),
            "Video Zoom": Field(r"[\w\s]+:\s?", r"[\d\.,]+", "视频缩放"),
            "YCbCr Matrix": Field(r"[\w\s]+:\s?", r".*", "YCbCr矩阵"),
            "Scroll Position": Field(r"[\w\s]+:\s?", r".*", "滚动位置"),
            "Active Line": Field(r"[\w\s]+:\s?", r"\d*", "活跃行"),
            "Collisions": Field(r"[\w\s]+:\s?", r"Normal|Reverse", "字幕重叠方式"),
            "WrapStyle": Field(r"[\w\s]+:\s?", r"[0-3]{1}", "换行方式"),
            "ScaledBorderAndShadow": Field(r"[\w\s]+:\s?", r"yes|no", "同比例缩放"),
            "Audio URI": Field(r"[\w\s]+:\s?", r".*", "音频路径"),
            "Audio File": Field(r"[\w\s]+:\s?", r".*", "音频文件"),
            "Video File": Field(r"[\w\s]+:\s?", r".*", "视频文件"),
            "Video Aspect Ratio": Field(r"[\w\s]+:\s?", r"\d+", "视频纵横比"),
            "Video Position": Field(r"[\w\s]+:\s?", r".*", "视频位置"),
            "Video Zoom Percent": Field(r"[\w\s]+:\s?", r"[\d\.]*", "视频缩放比例"),
            "Last Style Storage": Field(r"[\w\s]+:\s?", r".*", "Last Style Storage"),
            "Video AR Mode":  Field(r"[\w\s]+:\s?", r".*", "AR模式"),
            "Video AR Value": Field(r"[\w\s]+:\s?", r".*", "AR值"),
            }

        # 脚本信息，包含必要信息
        SCRIPT_REQUIRED = {
            "Title": "<untitled>",
            "Original Script": "<unknown>",
            "ScriptType": "v4.00+",
            "PlayResX": 640,
            "PlayResY": 480,
            "ScaledBorderAndShadow": "yes",
        }

        script_body = {";": {"value": []}} if set_default else {}

        end_index = -1  # 读取到下一个标题时的下标
        order = -1  # 序号
        for num, line in enumerate(textlist[start_index:], start=start_index):
            if (line.startswith("[") and line.endswith("]")) or not line:
                # 如果读取到空行或者下一个标题时，说明这部分内容以及解析结束
                end_index = num
                break
            # 检查标题是否是合法标题
            re_res = re.search(r"^(?P<key>;)\s?.*$", line) \
                if line.startswith(";") \
                else re.search(r"^(?P<key>[\w\s]+):\s?.*$", line)
            if not re_res:
                continue

            key = re_res.groupdict().get("key")
            # 检查Key值是否合法
            if key not in SCRIPT_INFO:
                continue

            re_res = re.search(r"^%s(?P<value>%s)$" % (SCRIPT_INFO[key].re_key,SCRIPT_INFO[key].re_val),line)
            if not re_res:
                continue

            order += 1
            re_res = re_res.groupdict()
            if key == ";":
                # ;的值可能存在多个，这里使用列表存储它的值
                script_body[key]["value"].append(re_res.get("value"))
                script_body[key]["order"] = order,
                script_body[key]["zh_title"] = SCRIPT_INFO[key].zh_title
            else:
                script_body[key] = {
                    "value": re_res.get("value"),
                    "order": order,
                    "zh_title": SCRIPT_INFO[key].zh_title,
                }

        if set_default:
            # 验证是否存在必选内容
            for key in SCRIPT_REQUIRED:
                if key in script_body:
                    # 如果有必选项，则跳过
                    continue
                order += 1
                script_body[key] = {"value": SCRIPT_REQUIRED[key],
                                    "order": order,
                                    "zh_title": SCRIPT_INFO[key].zh_title
                                    }
        return script_body, end_index

    @staticmethod
    def garbage(textlist, start_index=0, *args, **kwargs):
        """
        解析Garbage

        这里的内容并不是那么重要-_-！

        :param textlist: 字幕文本列表
        :param start_index: 起始下标
        :param args:
        :param kwargs:
        :return: 解析到的该项数据和结束下标
        """
        return AssParse.script(textlist, start_index, False)

    @staticmethod
    def style(textlist,  start_index=0, *args, **kwargs):
        """
        解析style的内容，format和style行，不包含[V4+ Styles]行

        使用方法：
        你需要传入一个文本列表，已经指定一个起始的列表下标，方便解析。如
        果传入一个错误的列表下标，那么可能会返回一个期望以外的结果。

        当第一行不是Format:...，则触发异常；当Format的内容项存在不合
        法内容时，触发异常。解析style内容时，如果存在不合法的style行，
        则会抛弃该行内容。

        如何判断该项内容结束：
        根据start_index开始循环textlist，直到遇到空行或者[xxx]内容
        行。

        关于顺序，这里会在解析每行内容的时候自动生成uuid，作为该行的唯
        一标识符，uuid还会存入一个order的列表中，方便反向生成数据，以
        及快速找到并修改指定内容（前端发起修改时）。

        全部解析完成后，会返回一个元组，这里面包含了解析好的内容（通常是
        一个字典），以及解析完当前项内容时的最后行的下一行下标。

        :param textlist: 字幕文本列表
        :param start_index: 起始下标
        :param args:
        :param kwargs:
        :return: 解析到的该项数据和结束下标
        """
        STYLE_INFO = {
            "Format": Field(r"Format:\s?", r"(?P<Format>Style):\s?", zh_title="格式"),
            "Name": Field(r"Name", r"(?P<Name>[^,]+)", zh_title="名称"),
            "Fontname": Field(r"Fontname", r"(?P<Fontname>[^,]+)", zh_title="字体"),
            "Fontsize": Field(r"Fontsize", r"(?P<Fontsize>[\d\.]+)", zh_title="字体大小"),
            "PrimaryColour": Field(r"PrimaryColour", r"(?P<PrimaryColour>&H[0-9a-fA-F]{8})", zh_title="主要颜色"),
            "SecondaryColour": Field(r"SecondaryColour", r"(?P<SecondaryColour>&H[0-9a-fA-F]{8})", zh_title="次要颜色"),
            "OutlineColour": Field(r"OutlineColour", r"(?P<OutlineColour>&H[0-9a-fA-F]{8})", zh_title="边框颜色"),
            "BackColour": Field(r"BackColour", r"(?P<BackColour>&H[0-9a-fA-F]{8})", zh_title="阴影颜色"),
            "Bold": Field(r"Bold", r"(?P<Bold>0|-1)", zh_title="粗体"),
            "Italic": Field(r"Italic", r"(?P<Italic>0|-1)", zh_title="斜体"),
            "Underline": Field(r"Underline", r"(?P<Underline>0|-1)", zh_title="下划线"),
            "StrikeOut": Field(r"StrikeOut", r"(?P<StrikeOut>0|-1)", zh_title="删除线"),
            "ScaleX": Field(r"ScaleX", r"(?P<ScaleX>[\d\.]+)", zh_title="文字水平缩放"),
            "ScaleY": Field(r"ScaleY", r"(?P<ScaleY>[\d\.]+)", zh_title="文字垂直缩放"),
            "Spacing": Field(r"Spacing", r"(?P<Spacing>[\d\.]+)", zh_title="文字间距"),
            "Angle": Field(r"Angle", r"(?P<Angle>[\d\.\-]+)", zh_title="旋转"),
            "BorderStyle": Field(r"BorderStyle", r"(?P<BorderStyle>[\d\.]+)", zh_title="轮廓风格"),
            "Outline": Field(r"Outline", r"(?P<Outline>[\d\.]+)", zh_title="轮廓宽度"),
            "Shadow": Field(r"Shadow", r"(?P<Shadow>[\d\.]+)", zh_title="阴影深度"),
            "Alignment": Field(r"Alignment", r"(?P<Alignment>[\d]+)", zh_title="对齐"),
            "MarginL": Field(r"MarginL", r"(?P<MarginL>[\d\.]+)", zh_title="左边距"),
            "MarginR": Field(r"MarginR", r"(?P<MarginR>[\d\.]+)", zh_title="右边距"),
            "MarginV": Field(r"MarginV", r"(?P<MarginV>[\d\.]+)", zh_title="垂直边距"),
            "Encoding": Field(r"Encoding", r"(?P<Encoding>[\d]+)", zh_title="编码"),
        }


        end_index = -1  # 读取到下一个标题时的下标
        val_re = r""

        # 检查第一行是否是合法的Format内容
        if textlist[start_index].startswith("Format:"):
            formats = textlist[start_index][len("Format:"):].split(",")
            for num, format_ in enumerate(formats):
                formats[num] = format_.strip()
                if formats[num] not in STYLE_INFO:
                    raise exceptions.AssParseError("解析ASS文件Style时发生错误。"
                                                   "原因：Format的内容相存在不合法项目或无效项目。")
                if num == len(formats) - 1:
                    val_re = "%s%s" % (val_re, STYLE_INFO[formats[num]].re_val)
                else:
                    val_re = r"%s%s,\s?" % (val_re, STYLE_INFO[formats[num]].re_val)
        else:
            raise exceptions.AssParseError("解析ASS文件Style时发生错误。"
                                           "原因：没有找到Format行内容。")

        style_body = {
            "format": formats,
            "style": {},
            "style_name": [],
            "order": [],
        }  # 保存style信息

        for num, line in enumerate(textlist[start_index + 1:], start_index + 1):
            if (line.startswith("[") and line.endswith("]")) or not line:
                # 如果读取到空行或者下一个标题时，说明这部分内容以及解析结束
                end_index = num
                break

            re_res = re.search(r"^Style:\s?%s$" % val_re, line)
            if not re_res:
                continue

            # 生成uid，并验证uid是否唯一
            while True:
                uid = uuid.uuid4().hex[-6:]
                if uid not in style_body["order"]: break

            style_body["order"].append(uid)
            style_body["style"][uid] = re_res.groupdict()
            if style_body["style"][uid]["Name"] not in style_body["style_name"]:
                style_body["style_name"].append(style_body["style"][uid]["Name"])
            # style_body["style"].append(re_res.groupdict())

        return style_body, end_index

    @staticmethod
    def event(textlist, start_index=0, *args, **kwargs):
        """
        解析event内容

        使用方法：
        你需要传入一个文本列表，已经指定一个起始的列表下标，方便解析。如
        果传入一个错误的列表下标，那么可能会返回一个期望以外的结果。

        当第一行不是Format:...，则触发异常；当Format的内容项存在不合
        法内容时，触发异常。解析event内容时，如果存在不合法的event行，
        则会抛弃该行内容。

        如何判断该项内容结束：
        根据start_index开始循环textlist，直到遇到空行或者[xxx]内容
        行。

        关于先后顺序的保持，这里会在解析每行内容的时候自动生成uuid，作为
        该行的唯一标识符，uuid还会存入一个order的列表中，方便反向生成数
        据，以及快速找到并修改指定内容（前端发起修改时）。

        :param textlist: 字幕文本列表
        :param start_index: 起始下标
        :param args:
        :param kwargs:
        :return: 解析到的该项数据和结束下标
        """
        # event类型
        EVENT_TYPES = ("Dialogue", "Comment", "Picture", "Sound", "Movie", "Command",)
        # event formats
        EVENT_INFO = {
            "Format": Field(re_val=r"(?P<Format>%s):\s?" % "|".join(EVENT_TYPES), zh_title="格式"),
            "Layer": Field(re_val=r"(?P<Layer>\d+)", zh_title="图层"),
            "Start": Field(re_val=r"(?P<Start>\d{1,2}:(?:5\d|[0-4]\d):(?:5\d|[0-4]\d).(?:9\d{1,2}|[0-8]\d{1,2}))", zh_title="开始时间"),
            "End": Field(re_val=r"(?P<End>\d{1,2}:(?:5\d|[0-4]\d):(?:5\d|[0-4]\d).(?:9\d{1,2}|[0-8]\d{1,2}))", zh_title="结束时间"),
            "Style": Field(re_val=r"(?P<Style>[^,]+)", zh_title="样式"),
            "Name": Field(re_val=r"(?P<Name>[^,]*)", zh_title="角色名"),
            "MarginL": Field(re_val=r"(?P<MarginL>(?:\d|[1-9]\d{1,3}))", zh_title="左边距"),
            "MarginR": Field(re_val=r"(?P<MarginR>(?:\d|[1-9]\d{1,3}))", zh_title="右边距"),
            "MarginV": Field(re_val=r"(?P<MarginV>(?:\d|[1-9]\d{1,3}))", zh_title="垂直边距"),
            "Effect": Field(re_val=r"(?P<Effect>[^,]*)", zh_title="过渡特效"),
            "Text": Field(re_val=r"(?P<Text>.*)", zh_title="对白字幕"),
        }

        end_index = -1  # 读取到下一个标题时的下标
        val_re = r""

        # 检查第一行是否是合法的Format内容
        if textlist[start_index].startswith("Format:"):
            formats = textlist[start_index][len("Format:"):].split(",")
            for num, format_ in enumerate(formats):
                formats[num] = format_.strip()
                if formats[num] not in EVENT_INFO:
                    raise exceptions.AssParseError("解析ASS文件event时发生错误。"
                                                   "原因：Format的内容相存在不合法项目或无效项目。")
                if num == len(formats) - 1:
                    if formats[num] != "Text":
                        raise exceptions.AssParseError("解析ASS文件event时发生错误。"
                                                       "原因：Format行最后项非Text。")
                    val_re = "%s%s" % (val_re, EVENT_INFO[formats[num]].re_val)
                else:
                    val_re = r"%s%s,\s?" % (val_re, EVENT_INFO[formats[num]].re_val)
        else:
            raise exceptions.AssParseError("解析ASS文件event时发生错误。"
                                           "原因：没有找到Format行内容。")

        # 用于匹配每行event内容的正则表达式
        val_re = "%s%s" % (EVENT_INFO["Format"].re_val, val_re)
        event_body = {
            "format": formats,
            "event": {},
            "order": [],
        }  # 保存event信息

        for num, line in enumerate(textlist[start_index + 1:], start_index + 1):
            if (line.startswith("[") and line.endswith("]")):
                # 如果读取到下一个标题时，说明这部分内容以及解析结束
                end_index = num
                break
            if num == len(textlist) - 1:
                end_index = num

            re_res = re.search(r"^%s$" % val_re, line)
            if not re_res:
                continue

            # 生成uid，并验证uid是否唯一
            while True:
                uid = uuid.uuid4().hex[-6:]
                if uid not in event_body["order"]: break

            event_body["order"].append(uid)
            event_body["event"][uid] = re_res.groupdict()

        return event_body, end_index

    def all(self):
        pass

