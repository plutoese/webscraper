# coding=UTF-8

# --------------------------------------------------------------
# class_dynamicscraper文件
# @class: DynamicScraper类
# @introduction: DynamicScraper类用来进行动态网页数据抓取
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.28
# --------------------------------------------------------------

import time
import random
from bs4 import BeautifulSoup
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
from libs.class_headlessbrowser import HeadlessBrowser
from selenium.webdriver.common.by import By
import requests
import re


class DynamicScraper:
    """ DynamicScraper类用来进行动态网页数据抓取

    :param str website: 网页地址
    :return: 无返回值
    """
    def __init__(self,website=None,label=None):
        # 设置网站地址
        self.website = website

        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','scraper')

        # 设置标示
        self.label = label

    def surf(self,proxies=None,proxy_type='http',timeout=0,type=0,ready_check=None):
        """ 连接上网

        :param list proxies: 代理服务器池
        :param str proxy_type: 代理服务器类型，例如'http'
        :param int timeout: 超时
        :param int type: 浏览器类型，如果type=0，则用PhantomJS，若type=1，则用firefox
        :param tuple ready_check: 检查网页是否载入成功，例如(By.CSS_SELECTOR,'.table_result')
        :param list action: 操作，例如[('interaction',{'location':'.province_select','select_text':'河北省'}),
                              ('interaction',{'location':'#btn_search','click':True}),
                              ('timeout',10),
                              ('get_text',{'location':'.table_result'})]
        :return: 返回字典，网址id：抓取内容
        :rtype: dict
        """
        times = 0
        successful = False
        while(not successful):
            random.seed()
            proxy = random.choice(proxies)
            self.browser = HeadlessBrowser(proxy=proxy,proxy_type=proxy_type,
                                           timeout=timeout,type=type)
            if self.browser.surf(website=self.website,ready_check=ready_check):
                successful = True
            else:
                times += 1
                if times > 10:
                    successful = True
                self.browser.quit()
        time.sleep(2)

    def act_once(self,action=None):
        """ 进行操作

        :param action: 操作列表
        :return:
        """
        print('Action Begins: ')
        result = None
        operation = {'interaction':self.browser.interact_one_time}
        for step in action:
            if step[0] == 'get_text':
                result = self.browser.get_text(**step[1])
                continue
            if step[0] == 'timeout':
                time.sleep(step[1])
                continue
            operation[step[0]](**step[1])

        return result

    def surf_more(self,proxies=None,proxy_type='http',timeout=0,type=0,ready_check=None,action=None):
        """ 连接上网，返回结果

        :param list proxies: 代理服务器池
        :param str proxy_type: 代理服务器类型，例如'http'
        :param int timeout: 超时
        :param int type: 浏览器类型，如果type=0，则用PhantomJS，若type=1，则用firefox
        :param tuple ready_check: 检查网页是否载入成功，例如(By.CSS_SELECTOR,'.table_result')
        :param list action: 操作，例如[('interaction',{'location':'.province_select','select_text':'河北省'}),
                              ('interaction',{'location':'#btn_search','click':True}),
                              ('timeout',10),
                              ('get_text',{'location':'.table_result'})]
        :return: 返回字典，网址id：抓取内容
        :rtype: dict
        """
        times = 0
        successful = False
        web_result = dict()
        # 检验是否成功，成功则终止循环
        while not successful:
            if len(self.website) < 1:
                successful = True
                continue

            # 设置代理服务器，从代理服务器池里随机选择
            random.seed()
            proxy = random.choice(proxies)
            # 创建浏览器
            self.browser = HeadlessBrowser(proxy=proxy,proxy_type=proxy_type,
                                           timeout=timeout,type=type)
            # 随机选择一组网页，组别大小由random.randint决定
            for _ in range(random.randint(1,min(50,len(self.website)))):
                # 随机选择一个网页
                key_choice = random.choice(list(self.website.keys()))
                # 检验网页是否可得，如果可得，那么执行动作，得到抓取结果，更新web_result字典，弹出得到的网页选择
                if self.browser.surf(website=self.website[key_choice],ready_check=ready_check):
                    #time.sleep(1)
                    content = self.act_once(action=action)
                    web_result.update({key_choice:content})
                    self.website.pop(key_choice)
                # 如果网页载入错误，那么关闭浏览器，退出循环，返回while循环，继续选择代理服务器
                else:
                    times += 1
                    if times > 100:
                        successful = True
                    self.browser.quit()
                    break
        # 返回结果
        return web_result

    def quit(self):
        """ 关闭浏览器

        :return: 无返回值
        """
        self.browser.quit()


if __name__ == '__main__':
    pmanager = ProxyManager()
    dscraper = DynamicScraper(website='https://www.hqms.org.cn/usp/roster/index.jsp',label='hqms.org.cn')
    dscraper.surf(proxies=pmanager.best_speed_proxies,proxy_type='https',timeout=5,type=1,
                  ready_check=(By.CSS_SELECTOR,'.table_result'))
    result = dscraper.act_once([('interaction',{'location':'.province_select','select_text':'河北省'}),
                              ('interaction',{'location':'#btn_search','click':True}),
                              ('timeout',10),
                              ('get_text',{'location':'.table_result'})])
    print(result)
    dscraper.quit()

