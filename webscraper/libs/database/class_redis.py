# coding=UTF-8

"""
=========================================
Redis数据库类
=========================================

:Author: glen
:Date: 2017.9.3
:Tags: redis database
:abstract: 连接redis数据库，并进行基本操作。

**类**
==================
Redis
    连接Redis数据库

**使用方法**
==================


**示范代码**
==================
::

"""

import redis


class Redis:
    """ 连接Redis数据库

    :param str host: 数据库主机，默认是'localhost'
    :param int port: 数据库端口，默认是6379
    :param str password: 数据库登录密码
    :return: 无返回值
    """
    def __init__(self, host='106.14.237.43', port=6379, password='z1Yh2900'):
        self._r = redis.Redis(host=host, port=port, password=password)

    def __len__(self):
        """ 返回redis数据库的记录数

        :return: 返回redis数据库的记录数
        """
        return self._r.dbsize()

    def set(self,name,value):
        """ 添加记录到Redis数据库中

        :param str name: 记录的名称
        :param str,tuple,list,set,dict value: 记录的值
        :return: 无返回值
        """
        if isinstance(value,str):
            self._r.set(name=name, value=value)
        elif isinstance(value,(tuple,list)):
            for item in value:
                self._r.rpush(name, item)
        elif isinstance(value,set):
            for item in value:
                self._r.sadd(name, item)
        elif isinstance(value,dict):
            for key,kvalue in value.items():
                self._r.hmset(name,{key:kvalue})
        else:
            raise Exception

    def get(self,name):
        """ 获取记录

        :param str name: 记录的名称
        :return: 返回记录的值
        """
        if bytes.decode(self.type(name)) == 'str':
            return self._r.get(name=name)
        elif bytes.decode(self.type(name)) == 'list':
            return [bytes.decode(item) for item in self._r.lrange(name=name,start=0,end=self._r.llen(name=name))]
        elif bytes.decode(self.type(name)) == 'set':
            return {bytes.decode(item) for item in self._r.smembers(name=name)}
        elif bytes.decode(self.type(name)) == 'hash':
            return {bytes.decode(key):bytes.decode(self._r.hgetall(name)[key]) for key in self._r.hgetall(name)}
        else:
            raise Exception

    def clear_all(self):
        """ 清除Redis数据库所有记录

        :return: 无返回值
        """
        self._r.flushdb()

    def delete(self,name):
        """ 删除某个记录

        :param name:
        :return:
        """
        self._r.delete(name)

    def type(self,name):
        """ 返回某个记录的类型

        :param str name: 记录的名称
        :return: 返回某个记录的类型
        """
        return self._r.type(name=name)

    def exists(self, name):
        """ 测试某个key是否存在

        :param name: key值
        :return:
        """
        return self._r.exists(name)

if __name__ == '__main__':
    db = Redis()

    core_dbs = db.get('core_database')
    for item in core_dbs:
        print(db.get(item)['label'])

    #db.set('testdict',{'name':[1,2,3,4]})
    result = db.get('testdict')
    print(result,type(result),result['name'],type(result['name']))

    '''
    #db.set('core_database',['ceic'])
    #db.set('scraper_database',['airquality'])
    db.set('ceic',{'label':'中国宏观经济数据平台(CEIC)',
                   'intro':'中国数据库包含超过30万条宏观经济、行业及区域的时间序列数据，CEIC中国数据库已经成为分析中国经济的最佳工具。',
                   'author':'system',
                   'group':'core_database',
                   'source':'CEIC中国数据库',
                   'link':'../core_database/querier_ceic.ipynb?dashboard'})
    db.set('airquality', {'label': '中国城市空气质量日报数据库',
                          'intro': '中国城市空气质量日报数据包含2014年1月1日以来每天中国城市空气质量日报的数据。',
                          'author': 'admin',
                          'group': 'scraper_database',
                          'source':'中华人民共和国环境保护部数据中心',
                          'link':'../scraper_database/querier_airquality.ipynb?dashboard'})'''

    '''
    print(len(db))
    db.clear_all()

    db.set('car',['hello','world'])
    print(db.get('car'))

    db.set('check',{'not','good'})
    print(db.get('check'))

    db.set('mdic',{'name':'Alice','age':24})
    print(db.get('mdic'))'''


