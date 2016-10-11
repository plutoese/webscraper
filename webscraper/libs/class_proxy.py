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
import requests

class Proxy:
    """ Proxy类用来处理代理服务器

    :param str full_address: proxy的地址，形式如http://user:password@host:port/
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

    def is_valid(self, check_address=None):
        """ 验证proxy是否有效

        :param str,dict check_address: 验证网址
        :return: 返回验证结果
        :rtype: bool
        """
        if check_address is None:
            check_address = {'address': 'http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ',
                             'title': '学术期刊—中国知网'}
        try:
            proxies = {'http':self.__full_address}
            to_check_title = False
            if isinstance(check_address,dict):
                to_check_address = check_address['address']
                to_check_title = True
            elif isinstance(check_address,str):
                to_check_address = check_address
            else:
                print('Wrong address Type: ',type(check_address))
                return False

            html = requests.get(url=to_check_address,proxies=proxies,timeout=10)
            if html.status_code != requests.codes.ok:
                print(html.status_code.code)
                return False
            bs = BeautifulSoup(html.content,'lxml')
            # check title
            if to_check_title:
                title = re.split('<',re.split('>',re.sub('\s+','',str(bs.title)))[1])[0]
                if not (title==check_address['title']):
                    print('Wrong title: ',title)
                    return False
            else:
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
    proxy = Proxy(full_address='http://1.82.216.135:80')
    print(proxy.full_address,proxy.address,proxy.port,proxy.username,proxy.password)
    if proxy.is_valid(check_address={'address':'http://www.dgtle.com/portal.php','title':'数字尾巴-分享美好数字生活'}):
        print(proxy.full_address)
    else:
        print('It is a bad proxy!')
