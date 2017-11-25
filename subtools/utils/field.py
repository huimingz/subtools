#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

class Field(object):
    """字段内容"""
    def __init__(self, re_key="", re_val="", zh_title="", default=None, order=None, default_order=None):
        self.re_val = re_val
        self.re_key = re_key
        self.default = default
        self.zh_title = zh_title
        self.order = order
        self.default_order = default_order