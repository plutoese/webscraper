# coding=UTF-8

"""
=========================================
代理服务器管理
=========================================

:Author: glen
:Date: 2017.8.24
:Tags: proxy
:abstract: 管理代理服务器

**类**
==================
Proxy
    代理服务器类
ProxyManager
    代理服务器管理类

**使用方法**
==================

"""

import random
from pymongo import DESCENDING, ASCENDING
from libs.database.class_mongodb import MonCollection


class Proxy:
    """ Proxy类用来代表一个代理服务器

    :param str ip: 代理服务器的ip地址
    :param str port: 代理服务器的端口
    :param str user: 代理服务器登录的用户名（可选）
    :param str passwd: 代理服务器登录的密码（可选）
    """
    def __init__(self, ip=None, port=None, user=None, passwd=None, type=0):
        self._ip = ip
        self._port = port
        self._user = user
        self._passwd = passwd
        self._type = type

    @property
    def address(self):
        if self._user is None:
            if self._type == 0:
                return ''.join(['http://',self._ip,':',str(self._port)])
            elif self._type == 1:
                return ''.join(['https://',self._ip,':',str(self._port)])
            else:
                return [''.join(['http://',self._ip,':',str(self._port)]), ''.join(['https://',self._ip,':',str(self._port)])]


class ProxyManager:
    """ ProxyManager类用来管理、检验和更新代理服务器列表
    :param str proxy_web: proxy的地址，默认为http://www.youdaili.net/Daili/guonei/
    :return: 无返回值
    """
    def __init__(self, mongodb='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/',
                 database='proxy', collection_name='proxys'):
        # 设置数据库
        self._conn = MonCollection(mongodb=mongodb, database=database, collection_name=collection_name)

    def find(self, type=0, limit=None):
        if type == 0:
            found = self._conn.find(filter={'protocol': {'$in': [0, 2]}},
                                    projection={'_id': False, 'ip': True, 'port': True, 'type': True},
                                    sort=[('score', DESCENDING), ('speed', ASCENDING)], limit=limit)
        else:
            found = self._conn.find(filter={'protocol': {'$in': [1, 2]}},
                                    projection={'_id': False, 'ip': True, 'port': True, 'type': True},
                                    sort=[('score', DESCENDING), ('speed', ASCENDING)], limit=limit)
        return {Proxy(ip=item['ip'],port=item['port'],type=type).address for item in found}

    @property
    def random_proxy(self):
        """ 随机返回一个代理服务器，选择的权重是它的count

        :return: 随机返回一个代理服务器
        """
        return random.choice(list(self.find(limit=40)))

    @property
    def top_50_proxies(self):
        """ 随机返回一个代理服务器，选择的权重是它的count

        :return: 随机返回一个代理服务器
        """
        return list(self.find(limit=50))

if __name__ == '__main__':
    pmanager = ProxyManager()
    print(pmanager.find(limit=10))
    print(pmanager.random_proxy)