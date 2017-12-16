# coding=UTF-8

"""
=========================================
StatsGov类
=========================================

:Author: glen
:Date: 2017.5.4
:Tags: stats database
:abstract: 自建国家统计局网站数据接口

**类**
==================
StatsGovProvinceVars
    抓取国家统计局省级统计变量
MonDatabase
    连接MongoDB数据库中的database
MonCollection
    连接MongoDB数据库中的collection

**使用方法**
==================
连接MongoDB数据库
    创建MongoDB实例就可以建立数据库连接，可以通过两种方式创建数据库实例：其一是连接字符串，例如'mongodb://plutoese:z1Yh29@139.196.189.191:3717/'，其二是指定主机和端口。
连接MongoDB数据库中的Database
    创建MonDatabase实例就可以建立Database连接。
连接MongoDB数据库中的colletion
    创建MonCollection实例就可以建立collection连接。
MongoDB中的数据库列表
    调用MongoDB类中的database_names属性
关闭MongoDB数据库连接
    无论是MongoDB、MonDatabase及MonCollection类中，都有close()来关闭MongoDB数据库连接

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

import re
import requests
from arrow import Arrow
from libs.class_mongodb import MongoDB


class StatsGovVars:
    def __init__(self):
        # to connect to database
        self._db =  MongoDB(mongo_str='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/')

        # variable query website
        self._var_query_web = 'http://data.stats.gov.cn/adv.htm'
        self._var_query_web_params = {'m': 'findZbXl', 'wd': 'zb'}

        self._tags = {'年度全国':'hgnd', '年度地区':'fsnd'}

    def update_categories_in_db(self, tag=None):
        self._db.connect('statsgov', 'categories')
        if tag is None:
            for tag in self._tags:
                for item in self.categories(db=self._tags.get(tag),tag=tag):
                    found = self._db.collection.find_one(item)
                    if found is None:
                        self._db.collection.insert_one(item)
        else:
            if self._tags.get(tag) is not None:
                for item in self.categories(db=self._tags.get(tag), tag=tag):
                    found = self._db.collection.find_one(item)
                    if found is None:
                        self._db.collection.insert_one(item)
            else:
                print('Undefiend tag!')
                raise Exception

    def categories(self, db, tag):
        all_categories = []
        for item in self.main_tree(db=db, tag=tag):
            print(item['name'])
            all_categories.append(item)
            all_categories.extend(self.sub_categories(item))
        print(len(all_categories))
        return all_categories

    def main_tree(self, db='hgnd', tag='年度全国'):
        """ 返回指标大类

        :param str db: 统计数据类型，例如年度全国数据、年度地区数据
        :param str tag: 标签说明
        :return: 返回指标大类
        :rtype: list
        """
        categories = []
        params = self._var_query_web_params.copy()
        params['db'] = db
        r = requests.post(self._var_query_web, data=params)
        for item in r.json():
            record = {key:item[key] for key in ['id','name','pid']}
            record['db'] = db
            record['tag'] = tag
            record['isParent'] = True
            categories.append(record)
        return categories

    def sub_categories(self, category):
        if not category['isParent']:
            return category
        else:
            categories = []
            params = self._var_query_web_params.copy()
            params.update({'db': category['db'], 'treeId': category['id']})
            r = requests.post(self._var_query_web, data=params)
            for item in r.json():
                record = {key: item[key] for key in ['id', 'name', 'pid', 'isParent']}
                record['tag'] = category['tag']
                record['db'] = category['db']
                if isinstance(self.sub_categories(record),list):
                    categories.append(record)
                    categories.extend(self.sub_categories(record))
                else:
                    categories.append(self.sub_categories(record))
            return categories

    def _query(self, param):
        variables_found = []
        r = requests.get('http://data.stats.gov.cn/adv.htm?m={}&db={}&wd={}&treeId={}'.
                         format(param.get('m'),param.get('db'),param.get('wd'),param.get('treeId')))
        for item in r.json():
            variables_found.append({key: item[key] for key in ['id', 'name', 'pid', 'exp', 'dbcode', 'wd']})
        return variables_found

    def variables(self,tag=None):
        self._db.connect('statsgov','categories')
        if tag is not None:
            treeid_found = self._db.collection.find({'isParent':False,'tag':tag})
            param = self._var_query_web_params.copy()
            param['db'] = self._tags.get(tag)
            for treeid in treeid_found:
                print(treeid['name'])
                param['treeId'] = treeid['id']
                variables = self._query(param=param)
        else:
            variables = []
            for mtag in self._tags:
                print('---',mtag,'---\n\n\n\n\n')
                treeid_found = self._db.collection.find({'isParent': False, 'tag': mtag})
                param = self._var_query_web_params.copy()
                param['db'] = self._tags.get(mtag)
                for treeid in treeid_found:
                    print(treeid['name'])
                    param['treeId'] = treeid['id']
                    variables.extend(self._query(param=param))
        return variables

    def update_variables_in_db(self, tag=None):
        mdb = MongoDB(mongo_str='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/')
        mdb.connect('statsgov', 'variables')
        for var in self.variables(tag=tag):
            print(var)
            found = mdb.collection.find_one(var)
            if found is None:
                mdb.collection.insert_one(var)

    @property
    def provinces(self):
        provinces_found = []
        r = requests.get('http://data.stats.gov.cn/adv.htm?m=findZbXl&db=fsnd&wd=reg&treeId=00')
        for item in r.json():
            provinces_found.append({key: item[key] for key in ['id', 'name']})
        return provinces_found


class StatsGov:
    def __init__(self):
        self._db = MongoDB(mongo_str='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/')
        self._tags = {'年度全国': 'hgnd', '年度地区': 'fsnd'}
        self._stats_gov_url_template = 'http://data.stats.gov.cn/easyquery.htm?m={}&dbcode={}&rowcode={}&' \
                                       'colcode={}&wds={}&dfwds={}&k1=14930450350'

    def update_nation_data_in_db(self):
        self._db.connect('statsgov','variables')
        variables = self._db.collection.find(projection={'_id':0,'id':1,'name':1})
        for var in variables:
            print(var)

    def update_province_data_in_db(self):
        self._db.connect('statsgov', 'variables')
        variables = self._db.collection.find({'dbcode':'fsnd'},projection={'_id': 0, 'id': 1, 'name': 1})
        self._db.connect('statsgov','provincedata')
        for var in variables:
            for y in range(1949,2017):
                rdata = self.province_query(variable=var.get('id'), year=str(y))
                if len(rdata) > 0:
                    for item in rdata:
                        found = self._db.collection.find_one(item)
                        if found is None:
                            print(item)
                            self._db.collection.insert_one(item)

    def query(self, tag='年度地区', variable='^人均地区生产总值', year=range(2013,2017)):
        self._db.connect('statsgov','variables')
        found = list(self._db.collection.find(({'name':{'$regex':variable}}),projection={'_id':0,'id':1,'name':1}))
        if len(found) < 1:
            print('No such variable!')
            raise Exception
        elif len(found) < 2:
            variable = found[0].get('id')
            if tag == '年度地区':
                if isinstance(year,(list,tuple,range)):
                    rdata = []
                    for y in year:
                        rdata.extend(self.province_query(variable=variable,year=str(y)))
                else:
                    rdata = self.province_query(variable=variable,year=str(y))
            else:
                rdata = self.nation_query(variable=variable)
            return rdata
        else:
            print('Too many variables!',list(found))
            raise Exception

    def nation_query(self, variable='A020101', start_year='1949', rowcode='zb', colcode='sj'):
        wds = StatsGov.to_url_str([{'wdcode': rowcode, 'valuecode': variable}])
        dfwds = StatsGov.to_url_str([{'wdcode': colcode, 'valuecode': ''.join([start_year, '-'])}])
        retrive_url = self._stats_gov_url_template.format('QueryData', 'hgnd', rowcode, colcode, wds, dfwds)
        r = requests.get(retrive_url)
        return StatsGov.json_to_data(r.json(), condition={'zb':variable,'sj':range(int(start_year),Arrow.utcnow().year+1)})

    def province_query(self, variable='A020201', year='2013', rowcode='sj', colcode='zb'):
        wds = StatsGov.to_url_str([{'wdcode': rowcode, 'valuecode': year}])
        dfwds = StatsGov.to_url_str([{'wdcode': colcode, 'valuecode': variable}])
        retrive_url = self._stats_gov_url_template.format('QueryData', 'fsnd', 'reg', 'zb', wds, dfwds)
        r = requests.get(retrive_url)
        return StatsGov.json_to_data(r.json(),condition={'zb': variable, 'sj': [int(year)], 'reg':None})

    @staticmethod
    def json_to_data(json_data, condition=None):
        to_data = []
        return_data = json_data.get('returndata')
        data_nodes = return_data.get('datanodes')
        for node in data_nodes:
            rdata = node.get('data')
            info = node.get('wds')
            if not rdata.get('hasdata'):
                continue
            mnode = dict()
            mnode['data'] = rdata.get('data')
            if condition is not None:
                if 'zb' in condition:
                    if [item['valuecode'] for item in info if item.get('wdcode')=='zb'][0] == condition.get('zb'):
                        mnode['variable'] = condition.get('zb')
                    else:
                        continue
                if 'reg' in condition:
                    if condition['reg'] is not None:
                        if [item['valuecode'] for item in info if item.get('wdcode')=='reg'][0] == condition.get('reg'):
                            mnode['region'] = condition.get('reg')
                    else:
                        mnode['region'] = [item['valuecode'] for item in info if item.get('wdcode') == 'reg'][0]
                if 'sj' in condition:
                    if int([item['valuecode'] for item in info if item.get('wdcode')=='sj'][0]) in condition.get('sj'):
                        mnode['year'] = int([item['valuecode'] for item in info if item.get('wdcode') == 'sj'][0])
                    else:
                        continue
            else:
                mnode['variable'] = [item['valuecode'] for item in info if item.get('wdcode')=='zb'][0]
                mnode['region'] = [item['valuecode'] for item in info if item.get('wdcode') == 'reg'][0]
                mnode['year'] = [item['valuecode'] for item in info if item.get('wdcode') == 'sj'][0]
            to_data.append(mnode)
        return to_data

    @staticmethod
    def to_url_str(params):
        return re.sub('\'','\"', re.sub('\s+', '', params.__repr__()))

if __name__ == '__main__':
    stats_var = StatsGovVars()
    #stats_var.update_categories_in_db()
    #stats_var.update_variables_in_db()

    #print(stats_var.main_tree())
    stats_gov = StatsGov()
    #result = stats_gov.province_query(year='1949')
    #for item in result:
    #    print(item)
    #stats_gov.update_nation_data_in_db()
    #result = stats_gov.query()
    #for item in result:
    #    print(item)
    stats_gov.update_province_data_in_db()