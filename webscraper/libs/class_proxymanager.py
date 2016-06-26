# coding=UTF-8

# --------------------------------------------------------------
# class_proxymanager文件
# @class: ProxyManager类
# @introduction: ProxyManager类用来管理和更新代理服务器列表
# @dependency: urllib包
# @author: plutoese
# @date: 2016.02.23
# --------------------------------------------------------------

import random
from libs.class_proxy import Proxy
from libs.class_mongodb import MongoDB
from libs.class_multithread import MultiThread


class ProxyManager:
    """ ProxyManager类用来管理、检验和更新代理服务器列表

    :param str proxy_web: proxy的地址，默认为http://www.youdaili.net/Daili/guonei/
    :return: 无返回值
    """
    def __init__(self,proxy_list=None):
        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','proxy')

        # 设置检验代理服务器有效性的网址列表
        self.check_websites = ['http://www.163.com',
                               'http://www.sina.com.cn']

        # 设置代理服务器列表
        if proxy_list is None:
            self.proxy_list = [item['proxy'] for item in self.db.collection.find(projection={'_id':0,'proxy':1})]
        else:
            self.proxy_list = proxy_list

        # 设置检验完的代理服务器列表
        self.__checked_proxy_list = dict()

    def set_check_websites(self,websites=None):
        """ 设置检验代理服务器有效性的网址列表

        :param websites:
        :return:
        """
        if websites is not None:
            self.check_websites = websites

    def check_one_validity(self,proxy_address):
        """ 辅助函数，用来检验代理服务器的有效性

        :param str proxy_address: 代理服务器地址，形如13.24.22.34:8080
        :return: 无返回值
        """
        count = 0
        for web in self.check_websites:
            if Proxy(''.join(['http://',proxy_address])).is_valid(check_address=web):
                count += 1
                print('successful: ',proxy_address)
        self.__checked_proxy_list.update({proxy_address:count})

    def multi_thread_check_proxy(self):
        """ 多线程验证代理服务器的有效性，调用辅助函数self._check_and_put_proxy

        :return: 无返回值
        """
        threads = []
        for ip in self.proxy_list:
            t = MultiThread(self.check_one_validity,args=(ip,),name=ip)
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def check_and_store(self,check_websites=None):
        """ 验证和储存有效的代理服务器地址

        :param check_websites:
        :return:
        """
        if check_websites is not None:
            self.set_check_websites(check_websites)

        self.multi_thread_check_proxy()

        for key in self.__checked_proxy_list:
            self.db.collection.find_one_and_update({'proxy':key},
                                                   {'$inc': {'count': self.__checked_proxy_list[key]}})

    def update_proxy_db(self):
        """ 更新代理服务器数据库列表

        :return: 无返回值
        """
        self.db.collection.delete_many({'count':{'$lt':1}})

    @property
    def proxy(self):
        """ 返回代理服务器的字典列表

        :return: 返回代理服务器字典列表
        """
        result = self.db.collection.find(projection={'_id':0,'proxy':1,'count':1},
                                         sort=[('count',-1)])
        return list(result)

    @property
    def random_proxy(self):
        """ 随机返回一个代理服务器，选择的权重是它的count

        :return: 随机返回一个代理服务器
        """
        result = []
        for item in self.proxy:
            result.extend([item['proxy']]*item['count'])
        return random.choice(result)


if __name__ == '__main__':
    web_list = ['http://www.163.com',
                 'http://www.sina.com.cn',
                 'http://www.ecust.edu.cn/',
                 'http://www.dgtle.com/portal.php']

    pmanager = ProxyManager()
    #pmanager.check_and_store(check_websites=web_list)
    #pmanager.update_proxy_db()
    print(pmanager.proxy)
    print(pmanager.random_proxy)