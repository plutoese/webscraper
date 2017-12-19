# coding = UTF-8

import pymongo
from libs.database.class_mongodb import MongoDB, MonCollection

# 0. 填写数据库与集合名称
database_name = 'scraperdata'
collection_name = 'citydailycongestionfromamap'

# 连接数据库
mongo = MongoDB()
conn = MonCollection(mongo,database=database_name,collection_name=collection_name)

# 更新数据库
filter = {}
update = {'$set':{'name':'交通拥堵延时指数'}}
conn.collection.update_many(filter=filter, update=update)




