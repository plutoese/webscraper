# coding = UTF-8

import re
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from collections import Counter

P = json.load(open('D:/data/result/literature_list_2015.txt'))

text = ''
for key in P:
    abst = P[key].get('abstract')
    if abst is not None:
        text = '\n'.join([text,abst])

print(text)

# 利用结巴分词，精确模式
seg_list = jieba.cut(text, cut_all=False)

cou = Counter(seg_list)
for item in cou.most_common(500):
    if len(item[0]) > 1:
        print(item)

