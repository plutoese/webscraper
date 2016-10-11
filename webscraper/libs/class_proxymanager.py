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
import datetime
import numpy as np
from libs.class_proxy import Proxy
from libs.class_mongodb import MongoDB
from libs.class_multithread import MultiThread
from selenium.webdriver.common.by import By


class ProxyManager:
    """ ProxyManager类用来管理、检验和更新代理服务器列表
    :param str proxy_web: proxy的地址，默认为http://www.youdaili.net/Daili/guonei/
    :return: 无返回值
    """
    def __init__(self,proxy_list=None, check_websites=None):
        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','proxy')

        # 设置检验代理服务器有效性的网址列表
        if check_websites is None:
            self.check_websites = [{'address':'http://www.163.com','title':'网易'},
                                   {'address':'http://www.sina.com.cn','title':'新浪首页'},
                                   {'address':'http://www.zhibo8.cc/','title':'直播吧-NBA直播|NBA直播吧|足球直播|英超直播|CCTV5在线直播|CBA直播|体育直播'},
                                   {'address':'http://www.dgtle.com/portal.php','title':'数字尾巴-分享美好数字生活'}]
        else:
            self.check_websites = check_websites

        # 设置代理服务器列表
        if proxy_list is None:
            self.proxy_list = [item['proxy'] for item in self.db.collection.find(projection={'_id':0,'proxy':1})]
        else:
            self.proxy_list = proxy_list

        # 设置检验完的代理服务器列表
        self.__checked_proxy_list = dict()

    def set_check_websites(self, check_websites=None):
        """ 设置检验代理服务器有效性的网址列表

        :param list check_websites: 待验证的网页地址列表
        :return: 无返回值
        """
        if check_websites is not None:
            self.check_websites = check_websites

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

        :param list check_websites: 待验证的网页地址列表
        :return:
        """
        if check_websites is not None:
            self.set_check_websites(check_websites)

        self.multi_thread_check_proxy()

        for key in self.__checked_proxy_list:
            self.db.collection.find_one_and_update({'proxy':key},
                                                   {'$set': {'count': self.__checked_proxy_list[key]}})

    def update_proxy_db(self, min_pass=2):
        """ 更新代理服务器数据库列表
        :return: 无返回值
        """
        self.db.collection.delete_many({'count':{'$lt':min_pass}})

    def speed_test(self,proxy_address,websites=None):
        """ 测试某个代理服务器的速度

        :param proxy_address: 代理服务器地址
        :param websites: 测试网速的网址
        :return: 网速
        """
        if websites is None:
            websites = self.check_websites

        speed = []
        count = 0
        for web in websites:
            start_time = datetime.datetime.now()
            if Proxy(''.join(['http://',proxy_address])).is_valid(check_address=web):
                count += 1
                speed.append((datetime.datetime.now() - start_time).total_seconds())

        if len(speed) > 0:
            return count,np.mean(speed)
        else:
            return count,-1

    def speed_for_valuable_proxies(self):
        """ 添加速度到最优的代理服务器

        :return: 无返回值
        """
        for proxy in [item['proxy'] for item in
                      self.db.collection.find({'count':len(self.check_websites)},projection={'_id':0,'proxy':1})]:
            count, mean_speed = self.speed_test(proxy)
            self.db.collection.find_one_and_update({'proxy':proxy},
                                                   {'$set': {'count':count,
                                                             'speed': mean_speed}})
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

    @property
    def best_speed_proxies(self):
        """ 返回所有通过四个网站测试的代理服务器，用速度排序

        :return: 代理服务器列表
        """
        result = self.db.collection.find({'count':len(self.check_websites),'speed': {'$gt':0}},
                                         projection={'_id':0,'proxy':1,'count':1,'speed':1},
                                         sort=[('speed',1)])
        return [item['proxy'] for item in result]

    def recommended_proxies(self, number=1):
        """ 返回推荐的代理服务器

        :param int number: 推荐代理服务器个数
        :return: 返回推荐的代理服务器
        :rtype: list
        """
        return random.sample(self.best_speed_proxies,min(number,len(self.best_speed_proxies)))

if __name__ == '__main__':
    web_list = [{'address':'http://www.163.com','title':'网易'},
                {'address':'http://www.sina.com.cn','title':'新浪首页'},
                {'address':'http://www.zhibo8.cc/','title':'直播吧-NBA直播|NBA直播吧|足球直播|英超直播|CCTV5在线直播|CBA直播|体育直播'},
                {'address':'http://www.dgtle.com/portal.php','title':'数字尾巴-分享美好数字生活'}]


    pmanager = ProxyManager()
    pmanager.set_check_websites(check_websites=web_list)

    #pmanager.check_and_store()

    #pmanager.update_proxy_db()

    #pmanager.speed_for_valuable_proxies()

    print(pmanager.proxy)
    print(pmanager.random_proxy)
    print(pmanager.recommended_proxies(number=5))
    print(pmanager.best_speed_proxies)