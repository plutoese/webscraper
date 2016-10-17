# coding=UTF-8

"""
=========================================
尝试：中文期刊导出
=========================================

:Author: glen
:Date: 2016.10.14
:Tags: mongodb database
:abstract: 连接MongoDB数据库，导出中文所需期刊

**类**
==================
无

**使用方法**
==================

**示范代码**
==================
::

    >>># 连接MongoDB
    >>>mongo = MongoDB(conn_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
    >>># 连接MongoDB中的数据库
    >>>mdb = MonDatabase(mongodb=mongo, database_name='region')
    >>># 返回MongoDB中的数据库列表
    >>>print(mongo.client.database_names())
    >>># 返回MongoDB数据库中数据集合列表
    >>>print(mdb.collection_names)
    >>># 创建一个新的数据集合
    >>>mdb.create_collection('cities')
    >>># 删除一个数据集合
    >>>mdb.drop_collection('cities')
    >>># 连接数据库中的collection
    >>>mcollection = MonCollection(database=mdb, collection_name='cities')
    >>># 插入数据到collection中
    >>>mcollection.insert([{'name':'Andy'}])
    >>># 在collection中查询数据
    >>>print(list(mcollection.find({'name':'Tom'})))
    >>>#关闭MongoDB连接
    >>>mcollection.close()
"""

from libs.class_mongodb import MongoDB


# 1. 连接数据库
db = MongoDB()
db.connect(database_name='publication',collection_name='ChineseJournal')
result = list(db.collection.find(projection={'_id':False,'中文名称':1,'综合影响因子':1,'ISSN':1},sort=[('综合影响因子',-1)]))

selected = (0,1,4,5,10,11,12,19,20,23,36,60,74,190)
print([result[i]['ISSN'] for i in selected])