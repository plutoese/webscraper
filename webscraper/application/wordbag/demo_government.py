# coding = UTF-8

import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

file = open('D:/data/result/govern_1954.txt', encoding='UTF-8')
content = file.read()

# 利用结巴分词，精确模式
seg_list = jieba.cut(content, cut_all=False)

result = []
cou = Counter(seg_list)
for item in cou.most_common(100):
    if len(item[0]) > 1:
        print(item)
        result.append(item)

print(result)

wordcloud = WordCloud(font_path=r'C:\Windows\Fonts\msyh.ttc', background_color="black").generate_from_frequencies(result)
plt.imshow(wordcloud)
plt.axis("off")
plt.show()