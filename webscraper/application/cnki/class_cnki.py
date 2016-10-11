# coding=UTF-8

# --------------------------------------------------------------
# class_cnki文件
# @class: Cnki类
# @introduction: Cnki类用来连接cnki数据库
# @dependency: webdriver包
# @author: plutoese
# @date: 2016.02.27
# --------------------------------------------------------------

import re
import pickle
import json
import time
import random
from collections import OrderedDict
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from libs.class_headlessbrowser import HeadlessBrowser
from selenium.webdriver.common.by import By
from libs.class_proxymanager import ProxyManager


class Cnki:
    """ Cnki类用来连接cnki数据库

    """
    def __init__(self, proxy=None, type=0):
        self.soups = list()
        self.more = True
        self.browser = HeadlessBrowser(proxy=proxy, type=type)
        self.browser.surf('http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ',
                          ready_check=(By.CSS_SELECTOR,'#bottom'))
        time.sleep(2)

    def submit(self):
        """ 提交查询，进行搜索

        :return:
        """
        self.browser.interact_one_time(self.browser.locate(id="btnSearch"),click=True)
        time.sleep(5)

    def sort(self,by='被引'):
        """ 根据by参数进行排序

        :param str by: 变量
        :return: 无返回值
        """
        self.browser.switch(iframe='iframeResult')
        self.browser.interact_one_time(location=self.browser.locate(link_text=by),click=True)
        time.sleep(6)

    def select_all_literature(self):
        self.browser.interact_one_time(location=self.browser.locate(link_text='清除'),click=True)
        time.sleep(2)
        self.browser.interact_one_time(location=self.browser.locate(id='selectCheckbox'),click=True)
        time.sleep(2)
        self.browser.interact_one_time(location='.SavePoint > a:nth-child(3)',click=True)

    def get_more(self,limit=4):
        """ 查询下一页

        :param limit:
        :return:
        """
        i = 1
        while self.more:
            if i >= limit:
                self.more = False
            try:
                self.browser.switch(iframe='iframeResult')
                self.browser.interact_one_time(location=self.browser.locate(id='Page_next'),click=True)
                time.sleep(3)
            except NoSuchElementException:
                self.more = False
            else:
                time.sleep(5)
                self.select_all_literature()
                self.child_operation()
                i += 1
                time.sleep(2)

    def child_operation(self):
        """ 操作子页面，并添加文献信息到self.soups

        :return: 无返回值
        """
        self.browser.interact_one_time(location='.GTContentTitle > td:nth-child(1) > input:nth-child(1)',click=True)
        self.browser.interact_one_time(location='#file_export > input:nth-child(1)',click=True)
        time.sleep(5)
        self.browser.interact_one_time(location=self.browser.locate(link_text='NoteExpress'),click=True)
        time.sleep(5)
        self.soups.append(BeautifulSoup(self.browser.browser.find_element_by_css_selector('.mainTable').text,"lxml"))
        time.sleep(5)
        self.browser.switch_to_parent(close=True)
        self.browser.switch_to_parent(close=True)
        time.sleep(5)

    def set_query(self,query_str=None):
        """ 设置专业查询字符串

        :param str query_str: 查询字符串
        :return: 无返回值
        """
        self.browser.interact_one_time(self.browser.locate(id='1_4'),click=True)
        time.sleep(2)
        self.browser.interact_one_time('#expertvalue',send_text=query_str)
        time.sleep(1)

    def set_period(self,start_period=None,end_period=None):
        """ 设置起始和终止时期

        :param str start_period: 起始时期
        :param str end_period: 终止时期
        :return: 无返回值
        """
        if start_period is not None:
            self.browser.interact_one_time(location=self.browser.locate(id='year_from'),select_text=start_period)
        if end_period is not None:
            self.browser.interact_one_time(location=self.browser.locate(id='year_to'),select_text=end_period)

        time.sleep(1)

    def set_subject(self,subjects=None):
        """ 选择学科领域

        :param list subjects: 学科字符串
        :return: 无返回值
        """
        self.browser.interact_one_time(location='input.btn:nth-child(1)',click=True)
        for subject in subjects:
            self.browser.interact_one_time(location=self.browser.locate(xpath=''.join(["//input[@name='",subject,"']"])),click=True)
        time.sleep(1)

    def export_to_pickle(self,file=r'D:\data\result\literature_list.pkl'):
        """ 到处有效的代理服务器列表到文件

        :param str file: 文件名
        :return: 无返回值
        """
        F = open(file, 'wb')
        pickle.dump(self.soups, F)
        F.close()

    def export_to_dict(self):
        literature = OrderedDict()

        for llist in self.soups:
            content = str(llist.find_all('p'))
            content = re.split('</p>\]',re.split('\[<p>',content)[1])[0]
            items = re.split('\n',content)

            one_literature = dict()
            for item in items:
                if '{Title}' in item:
                    title = re.sub('\s+','',re.split('}: ',item)[1])
                if '{Author}' in item:
                    one_literature['author'] = [re.sub('\s+','',author) for author in re.split('\{Author\}\: ',item)
                                                if len(author) > 0]
                if '{Author Address}' in item:
                    one_literature['address'] = [re.sub('\s+','',address) for address in re.split(';',re.split('\}\: ',item)[1])
                                                if len(address) > 0]
                if '{Journal}' in item:
                    one_literature['journal'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{Year}' in item:
                    one_literature['year'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{Issue}' in item:
                    one_literature['issure'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{Pages}' in item:
                    one_literature['pages'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{Keywords}' in item:
                    one_literature['keyword'] = [re.sub('\s+','',keyword) for keyword in re.split(';',re.split('\}\: ',item)[1])
                                                 if len(keyword) > 0]
                if '{Abstract}' in item:
                    one_literature['abstract'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{ISBN/ISSN}' in item:
                    one_literature['ISBN/ISSN'] = re.sub('\s+','',re.split('\}\: ',item)[1])
                if '{Database Provider}' in item:
                    literature[title] = one_literature
                    one_literature = dict()

        return literature

    def export_to_json(self,file=r'E:\gitrobot\files\literature\literature_list.txt'):
        json.dump(self.export_to_dict(), fp=open(file,'w'))

    def close(self):
        """ 关闭浏览器

        :return: 无返回值
        """
        self.browser.quit()

if __name__ == '__main__':
    #cnki_obj = Cnki()
    pmanager = ProxyManager()
    random.seed()
    proxy = random.choice(pmanager.best_speed_proxies)
    print(proxy)
    cnki_obj = Cnki(proxy=proxy,type=1)
    print(cnki_obj.browser.browser.get_cookies())
    cnki_obj.set_query("JN='经济研究'")
    time.sleep(4)
    cnki_obj.set_period(start_period="2015",end_period="2015")
    time.sleep(5)
    cnki_obj.submit()
    cnki_obj.sort()
    cnki_obj.select_all_literature()
    time.sleep(5)
    cnki_obj.child_operation()
    cnki_obj.get_more(limit=100)

    cnki_obj.export_to_json(file=r'D:\data\result\literature_list_2010.pkl')
    cnki_obj.close()
