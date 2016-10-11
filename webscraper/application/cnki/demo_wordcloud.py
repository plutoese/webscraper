# coding = UTF-8

import re
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

P = json.load(open(r'D:\data\result\literature_list_2015.txt'))

SKIP_WORDS = ['产业发展论坛','.*(大学|学院)$','《?经济研究》?','孙冶方','论坛综述','世界经济','中国社会科学院','笔谈文章',
              '(入选|学术)论文','.*论坛$','匿名审稿','审稿人','招聘启事','研究机构','裴长洪','学术(交流|研究)','研究中心','研究成果',
              '普通高等学校','论坛征文','(征文|论文)选题','中国青年','理事会成员','优秀成果奖','中国经济学','电子信箱','学术期刊',
              '海内外学者','人才培养','.+经济学','.+委员会','经济管理','王亚南','中国经济问题','蔡昉','^硕士学位.+','.+研究生',
              '中国金融','学者投稿','.+硕士$','皮书','推荐人','管理世界','理论与实践','经济学会','.+重点学科','经济学发展',
              '公告发布','国际经济与贸易','政府工作报告','人文社会科学','管理现代化','加油卡','专任教师','国外期刊','北三环中路',
              '经济增长','经济发展',
              ]

word_list = []
for key in P:
    keywords = P[key].get('keyword')
    if keywords is None:
        continue
    print(keywords)
    for word in keywords:
        skipped = False
        for skip in SKIP_WORDS:
            if re.match(skip,word) is not None:
                skipped = True
                break
        if skipped:
            continue

        word_list.append(word)

print(word_list)

new_text = ' '.join(word_list)

wordcloud = WordCloud(font_path=r'C:\Windows\Fonts\msyh.ttc', background_color="black").generate(new_text)
plt.imshow(wordcloud)
plt.axis("off")
plt.show()