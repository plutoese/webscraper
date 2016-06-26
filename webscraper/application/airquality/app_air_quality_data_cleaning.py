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
source = 'http://www.tianqihoubao.com/'

# 导入原始网页数据
db = MongoDB()
db.connect('cache','scraper')
html_files = db.collection.find({'label':'airquality'})

# 连接到空气质量数据库
db.connect('application','airquality')

# 解析数据和储存进入MongoDB数据库
for apage in html_files:
    if re.search('/aqi/[a-zA-Z]+-\d+',apage['webaddress']) is None:
        continue
    print(apage['webaddress'])
    # 网页内容
    html_content = apage['content']

    # 析出城市名
    htmlparser = HtmlParser(html_content=html_content)
    title = htmlparser.bs_obj.select('.api_month_list > h4')[0].text
    city = re.split('\d+月',title)[0]
    print(city)

    # 析出数据表格
    data_table = htmlparser.table('.b')

    # 变量
    vars = [re.sub('\.','',item) for item in data_table[0]]

    # 根据数据表格生成数据库记录
    for obs in data_table[1:]:
        data_row = {'city':city}

        # 生成唯一比较字符串
        mid = ''.join([city,obs[0]])
        data_row['mid'] = mid

        # 处理时间
        #mdate = [int(item) for item in re.split('-',obs[0])]
        #mdate = date(mdate[0],mdate[1],mdate[2])
        #data_row[vars[0]] = mdate

        # 组合数据生成可插入数据库记录形式
        data_row.update(dict(zip(vars,obs)))
        print(data_row)

        # 插入前查询是否有该条目
        found = db.collection.find_one({'mid':mid})
        if found is None:
            db.collection.insert_one(data_row)


