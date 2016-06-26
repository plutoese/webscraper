# coding=UTF-8

# --------------------------------------------------------------
# class_proxylistfromyoudaili文件
# @class: ProxyListFromYoudaili类
# @introduction: ProxyList类用来生成有效的代理服务器列表
# @dependency: urllib包
# @author: plutoese
# @date: 2016.02.23
# --------------------------------------------------------------

from bs4 import BeautifulSoup
import re
import requests
from libs.class_mongodb import MongoDB


class ProxyListFromYoudaili:
    """ ProxyList类用来生成有效的代理服务器列表

    :param str proxy_web: proxy的地址，默认为http://www.youdaili.net/Daili/guonei/
    :return: 无返回值
    """
    def __init__(self,proxy_web='http://www.youdaili.net/Daili/http/',
                 check_website='http://www.cuaa.net/'):
        self.__proxy_web = proxy_web
        self.__proxy_unchecked_list = self._parse()

    def export_to_db(self):
        """ 导出到MongoDB数据库

        """
        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','proxy')
        for item in self.proxy_unchecked_list:
            found = self.db.collection.find_one({'proxy':item})
            if found is None:
                self.db.collection.insert_one({'proxy':item, 'count':0})

    def _parse(self):
        """ 辅助函数，用来抓取网站上的代理服务器列表

        :return: 代理服务器列表
        :rtype: list
        """
        first_web = requests.get(self.__proxy_web)
        bsobj_first_web = BeautifulSoup(first_web.text, "lxml")
        result1 = bsobj_first_web.find(class_='newslist_line')
        proxy_web = result1.find('a').attrs['href']

        r = requests.get(proxy_web)
        r.encoding = 'utf-8'
        bsobj_second_web = BeautifulSoup(r.text, "lxml")

        ip_address_list = bsobj_second_web.find_all(text=re.compile('\d+\.\d+\.\d+\.\d+'))
        proxy_list = [re.split('@',re.sub('\s+','',ip))[0] for ip in ip_address_list]
        return proxy_list

    @property
    def proxy_unchecked_list(self):
        """ 返回网络抓取的代理服务器列表

        :return: 返回网络抓取的代理服务器列表
        :rtype: list
        """
        return self.__proxy_unchecked_list

if __name__ == '__main__':
    plist = ProxyListFromYoudaili()
    print(plist.proxy_unchecked_list)
    plist.export_to_db()
