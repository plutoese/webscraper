# coding=UTF-8

"""
=========================================
代理服务器获取类
=========================================

:Author: glen
:Date: 2017.5.8
:Tags: proxy
:abstract: 从XiciDaili.com获取代理服务器

**类**
==================
ProxyListFromXiciDaili
    从XiciDaili.com获取代理服务器

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
"""

from bs4 import BeautifulSoup
import re
import requests
from libs.class_mongodb import MongoDB


class ProxyListFromXiciDaili:
    def __init__(self):
        # to connect to database
        self._db =  MongoDB(mongo_str='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/')

    @property
    def proxies(self):
        r = requests.get('http://api.xicidaili.com/free2016.txt')
        return [re.sub('\s+','',item) for item in re.split('\n',r.text)]


if __name__ == '__main__':
    proxy_list = ProxyListFromXiciDaili()
    print(proxy_list.proxies)