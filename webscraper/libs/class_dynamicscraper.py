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
        """ 连接网址冲浪

        :param website: 网址
        :param ready_check: 检查网页是否载入成功，例如(By.CSS_SELECTOR,'.table_result')
        :return: 无返回值
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

    def quit(self):
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

