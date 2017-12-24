# coding = UTF-8

"""
@title: 创建索引
@introduction：创建数据库索引
@tag：database index
@author：glen
@date：2017.12.18
"""

import pymongo
from libs.database.class_mongodb import MongoDB, MonCollection

# 0. 填写数据库与集合名称
database_name = 'cache'
collection_name = 'gaokaorecord'
# 索引格式：[("mike", pymongo.ASCENDING),("eliot", pymongo.DESCENDING)]
index_to_be_created = [[("url", pymongo.ASCENDING)]]
'''
index_to_be_created = [[("学校", pymongo.ASCENDING)],[("年份", pymongo.ASCENDING)],
                       [("年份", pymongo.ASCENDING),("学校",pymongo.ASCENDING)],
                       [("学校", pymongo.ASCENDING), ("年份", pymongo.ASCENDING)]]'''

# 连接数据库
mongo = MongoDB()
conn = MonCollection(mongo,database=database_name,collection_name=collection_name)

# 创建索引
for one_index in index_to_be_created:
    conn.create_index(one_index)

