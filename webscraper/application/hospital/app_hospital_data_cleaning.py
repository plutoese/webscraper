# coding=UTF-8

# --------------------------------------------------------------
# app_air_quality_data_cleaning文件
# @introduction: 解析空气质量网页数据，并存入数据库
# @source：天气后报，http://www.tianqihoubao.com/aqi/
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.26
# --------------------------------------------------------------

import re
from libs.class_mongodb import MongoDB
from libs.class_htmlparser import HtmlParser
from datetime import date

# 初始化
source = 'https://www.hqms.org.cn/usp/roster/index.jsp'

# 导入原始网页数据
db = MongoDB()
db.connect('cache','scraper')
html_files = db.collection.find({'label':'hospital'})

# 连接到空气质量数据库
db.connect('application','hospital')

# 解析数据和储存进入MongoDB数据库
for apage in html_files:
    content = apage['content']
    print(content)


