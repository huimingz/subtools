#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: "Kairu"

import sys, os
import time
import re
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subtools.ass import Ass

appid = open("../appid.txt", 'r', encoding='utf-8').read()

file_path0 = "./Macross Ai Oboete Imasu Ka.ass"
file_path1 = "./ass1.ass"
file_path2 = "./ass2.ass"
file_path3 = "./ass3.ass"
file_path4 = "./ass4.ass"
file_path5 = "./utf8.ass"
file_path6 = "./uk.ass"

start_time = time.time()

my_ass = Ass()
my_ass.from_file("./2.ass")
my_ass.parse_all()

# json_data = my_ass.as_json()

# my_ass.parse_script()
# my_ass.parse_garbages()
# my_ass.parse_style()
# my_ass.parse_event()
# my_ass.as_pickle()

my_ass.furigana(["Default", "Default1"], appid)

# for uid in my_ass.text_dict["Events"]["order"]:
#     print(my_ass.text_dict["Events"]["event"][uid])

text = my_ass.as_str(furigana=True)
print(text)

# my_ass.save2file("2_new.ass", True)
print(my_ass.VERSION)

print("\nCPU total time-consuming: %fms" % ((time.time() - start_time) * 1000))

#######################################################