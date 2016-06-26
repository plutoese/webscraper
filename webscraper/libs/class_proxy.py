# coding=UTF-8

# --------------------------------------------------------------
# class_proxy文件
# @class: Proxy类
# @introduction: Proxy类用来处理代理服务器
# @dependency: urllib包
# @author: plutoese
# @date: 2016.02.23
# --------------------------------------------------------------

import re
from bs4 import BeautifulSoup
from urllib import request


class Proxy:
    """ Proxy类用来处理代理服务器

    :param str address: proxy的地址，形式如http://user:password@host:port/
    :param str type: 代理服务类型
    :return: 无返回值
    """
    def __init__(self,full_address,type='http'):
        self.__full_address = full_address
        self.__type = type

        self.__username = None
        self.__password = None
        if '@' in self.__full_address:
            username_and_password, address_and_port = re.split('@',re.split('//',self.__full_address)[1])
            self.__username, self.__password = re.split(':',username_and_password)
        else:
            address_and_port = re.split('//',self.__full_address)[1]

        address_and_port_list = re.split(':',address_and_port)
        self.__address = address_and_port_list[0]
        if len(address_and_port_list) > 1:
            self.__port = int(address_and_port_list[1])
        else:
            self.__address = 80

    def is_valid(self,check_address='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ'):
        """ 验证proxy是否有效

        :param str check_address: 验证网址
        :return: 返回验证结果
        :rtype: bool
        """
        try:
            proxy_handler = request.ProxyHandler({self.__type: self.__full_address})
            opener = request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            request.install_opener(opener)
            req = request.Request(check_address)
            web = request.urlopen(req,timeout=60)
            bs = BeautifulSoup(web.read(),'lxml')
            print(bs.title)
        except Exception:
            return False
        return True

    @property
    def full_address(self):
        """ 返回proxy地址

        :return: 返回proxy地址
        :rtype: str
        """
        return self.__full_address

    @property
    def address(self):
        return self.__address

    @property
    def port(self):
        return self.__port

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

if __name__ == '__main__':
    proxy = Proxy(full_address='http://36.250.74.87:8102')
    print(proxy.full_address,proxy.address,proxy.port,proxy.username,proxy.password)
    if proxy.is_valid(check_address='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ'):
        print(proxy.full_address)
    else:
        print('It is a bad proxy!')
