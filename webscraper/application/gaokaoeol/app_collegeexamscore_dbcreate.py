# coding=UTF-8

import re
from libs.class_proxymanager import ProxyManager
from libs.class_dynamicscraper import DynamicScraper
from selenium.webdriver.common.by import By
from libs.class_mongodb import MongoDB

# 1. 设置源数据库
db = MongoDB()
db.connect('cache','scraper')

# 2. 读取源数据
records = []
for doc in db.collection.find({'label':'CollegeEntranceExam'}):
    print(doc['label'],doc['website'])
    rows = re.split('\n',doc['content'])
    vars = re.split('\s+',rows[0])[0:8]
    for row in rows[1:]:
        if re.match('^\d+$',re.split('\s+',row)[3]) is not None:
            record = dict(zip(vars,[re.sub('--','',item) for item in re.split('\s+',row)]))
            print(record)
            record['mid'] = ''.join([record['学校名称'],record['招生地区'],record['年份'],
                                    record['文理科'],record['录取批次']])
            records.append(record)
    print('-'*80)

# 3. 储存进入目标数据库
db.connect('application','collegeentrancescore')
for item in records:
    found = db.collection.find_one({'mid':item['mid']})
    if found is None:
        db.collection.insert_one(item)
