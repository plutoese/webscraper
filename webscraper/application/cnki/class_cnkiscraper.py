# coding = UTF-8

"""
=========================================
中国知网期刊库爬虫
=========================================

:Author: glen
:Date: 2016.10.14
:Tags: mongodb cnki literature
:abstract: 中国知网期刊库爬虫
"""


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
from libs.class_mongodb import MongoDB

class CnkiScraper:
    """ CnkiScraper类用来爬取中国期刊网数据

    :param str proxy: 代理服务器
    :param int type: 浏览器类型，0为PhantomJS，1为Firefox
    """
    def __init__(self, proxy=None, type=0):
        self.soups = list()
        self.browser = HeadlessBrowser(proxy=proxy, type=type)

    def is_connected(self):
        """ 检验是否连接上了知网

        :return: 连接成功返回True，否则为False
        :rtype: Bool
        """
        return self.browser.surf('http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ',
                                 ready_check=(By.CSS_SELECTOR,'#bottom'))

    def submit(self, wait=5):
        """ 提交查询，进行搜索

        :return: 无返回值
        """
        self.browser.interact_one_time(self.browser.locate(id="btnSearch"),click=True)
        time.sleep(wait)

    def switch_to_result_frame(self):
        """ 转换显示结果的框架

        :return: 无返回值
        """
        self.browser.switch(iframe='iframeResult')

    def sort(self,by='被引', wait=6):
        """ 根据by参数进行排序

        :param str by: 变量
        :return: 无返回值
        """
        self.browser.interact_one_time(location=self.browser.locate(link_text=by),click=True)
        time.sleep(wait)

    def clear_all_selected(self, wait=1):
        """ 清除所有选择项

        :return: 无返回值
        """
        self.browser.interact_one_time(location=self.browser.locate(link_text='清除'),click=True)
        time.sleep(wait)

    def select_all_literature(self, wait=2):
        """ 选择所有的文献

        :param wait: 等待时间
        :return: 无返回值
        """
        self.browser.interact_one_time(location=self.browser.locate(id='selectCheckbox'),click=True)
        time.sleep(wait)

    def export_literature(self, wait=1):
        """ 导出文献

        :param wait: 等待时间
        :return:无返回值
        """
        self.browser.interact_one_time(location='.SavePoint > a:nth-child(3)',click=True)
        time.sleep(wait)

    def is_exist_next_page(self):
        """ 检验是否存在下一页

        :return: 是否存在下一页
        :rtype: bool
        """
        if self.browser.locate(id='Page_next'):
            return True
        else:
            return False

    def go_next(self):
        """ 点击下一页

        :return: 无返回值
        """
        self.browser.interact_one_time(location=self.browser.locate(id='Page_next'),click=True)

    def cite_and_download(self):
        """ 返回文献被引次数和下载次数

        :return: 返回文献被引次数和下载次数
        :rtype: dict
        """
        literature_cite = dict()
        table = self.browser.get_text(location='.GridTableContent',beautiful=False)
        for item in re.split('分享',table)[1:]:
            record = [unit for unit in re.split(' ',item) if re.match('^\s*$',unit) is None]

            if len(record) > 0:
                title = record[1]
                to_be_split = re.split('\n',record[-1])
                if len(to_be_split) > 2:
                    if re.match('\d{4}/',to_be_split[0]) is not None:
                        cite = 0
                        download = int(to_be_split[1])
                    else:
                        cite = int(to_be_split[0])
                        download = int(to_be_split[1])
                else:
                    if re.match('\d{4}/',to_be_split[0]) is None:
                        cite = int(to_be_split[0])
                literature_cite[title] = {'cite':cite, 'download':download}

        return literature_cite

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

    def number_of_literature(self):
        """ 返回文献数量

        :return: 返回文献数量
        """
        total_number_str = self.browser.browser.find_element_by_css_selector('.pageBar_min > div:nth-child(1)').text
        return int(re.sub(',','',re.findall('\d+,?\d+',re.sub('\s+','',total_number_str))[0]))

    def export_to_pickle(self,file=r'D:\data\result\literature_list.pkl'):
        """ 到处有效的代理服务器列表到文件

        :param str file: 文件名
        :return: 无返回值
        """
        F = open(file, 'wb')
        pickle.dump(self.soups, F)
        F.close()

    def export_to_dict(self):
        literature = []
        for llist in self.soups:
            content = str(llist.find_all('p'))
            content = re.split('</p>\]',re.split('\[<p>',content)[1])[0]
            items = re.split('\n',content)

            one_literature = dict()
            for item in items:
                if '{Title}' in item:
                    title = re.sub('\s+','',re.split('}: ',item)[1])
                    one_literature['title'] = title
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
                    one_literature['issue'] = re.sub('\s+','',re.split('\}\: ',item)[1])
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
                    literature.append(one_literature)
                    one_literature = dict()

        return literature

    def export_to_json(self,file=r'E:\gitrobot\files\literature\literature_list.txt'):
        json.dump(self.export_to_dict(), fp=open(file,'w'))

    def close(self):
        """ 关闭浏览器

        :return: 无返回值
        """
        self.browser.quit()


class CnkiScraperInterface:
    """ 中国期刊网爬虫接口

    :param str proxy: 代理服务器
    :param int type: 浏览器类型，0为PhantomJS，1为Firefox
    :param bool multi: 是否启用多线性
    """
    def __init__(self, proxy=None, type=1):
        self.proxy = proxy
        self.type = type
        self.cnki_obj = None

    def query(self, querystr=None, period=None, subject=None, sortedby=None, limit=None, cite=False):
        # 检验是否成功连接上中国期刊网，如果不成功，报错
        if not self.check_connection():
            raise Exception

        # 设定查询字符串
        if querystr is not None:
            self.cnki_obj.set_query(querystr)

        time.sleep(1)

        # 设定时期
        if period is not None:
            self.cnki_obj.set_period(start_period=period.get('start_year'),end_period=period.get('end_year'))

        time.sleep(1)

        # 设定学科
        if subject is not None:
            self.cnki_obj.set_subject(subject)

        time.sleep(1)

        # 提交搜索
        self.cnki_obj.submit()

        # 设定被引
        if sortedby is not None:
            self.cnki_obj.sort(by=sortedby)

        time.sleep(2)

        # 转换到结果显示框架
        self.cnki_obj.switch_to_result_frame()

        # 记录查询得到的文献数量，用来进行后期核对
        total_number = self.cnki_obj.number_of_literature()

        # 切换到每页50条文献的显示
        self.cnki_obj.browser.interact_one_time(location='#id_grid_display_num > a:nth-child(3)',click=True)
        time.sleep(1)

        cites = dict()
        cites.update(self.cnki_obj.cite_and_download())
        self.cnki_obj.select_all_literature()

        if limit is not None:
            pages = int((limit-1)/50)
            for i in range(pages):
                if self.cnki_obj.is_exist_next_page():
                    self.cnki_obj.go_next()
                    time.sleep(1)
                    cites.update(self.cnki_obj.cite_and_download())
                    self.cnki_obj.select_all_literature()
        else:
            while self.cnki_obj.is_exist_next_page():
                self.cnki_obj.go_next()
                time.sleep(1)
                self.cnki_obj.select_all_literature()
                cites.update(self.cnki_obj.cite_and_download())
                self.cnki_obj.select_all_literature()

        #导出所有文献
        self.cnki_obj.export_literature()
        time.sleep(2)
        # 对文献进行一系列操作，并抓取文献到soups
        self.cnki_obj.child_operation()

        # 如果文献数量正确，插入文献到数据库
        literatures = self.cnki_obj.export_to_dict()

        for literature in literatures:
            if literature.get('title') in cites:
                literature['cite'] = cites.get(literature.get('title')).get('cite')
                literature['download'] = cites.get(literature.get('title')).get('download')
            else:
                print('Can not found: ',literature.get('title'))

        self.cnki_obj.close()

        if limit is None:
            if len(literatures) == total_number:
                return literatures
            else:
                print('Wrong Number: ', len(literatures))
                raise Exception

        return literatures

    def check_connection(self, max_connection_number=10):
        """ 连接并返回是否连接信息

        :param int max_connection_number: 最大连接次数
        :return: 返回是否成功连接
        :rtype: bool
        """
        is_proxy_successful = False
        max_connection_number = max_connection_number
        i = 1
        while not is_proxy_successful:
            proxy = random.choice(self.proxy)

            self.cnki_obj = CnkiScraper(proxy=proxy,type=1)
            if self.cnki_obj.is_connected():
                is_proxy_successful = True
            else:
                self.cnki_obj.close()
                time.sleep(5)
            i += 1
            if i > max_connection_number:
                return False
        return True

    def insert_to_db(self, literatures=None, database='paper', collection='cliterature'):
        db = MongoDB()
        db.connect(database,collection)
        for record in literatures:
            print(record['title'],record['journal'],record['year'],record['issue'],record.get('pages'))
            if record.get('author') is None:
                print('No author!')
                continue
            result = db.collection.find_one({'title':record.get('title'),
                                         'journal':record.get('journal'),
                                         'year':record.get('year'),
                                         'issue':record.get('issue'),
                                         'pages':record.get('pages')})
            if result is None:
                print('Insert...!')
                db.collection.insert_one(record)
            else:
                print('Update...!')
                db.collection.update_one({'title':record.get('title'),
                                               'journal':record.get('journal'),
                                               'year':record.get('year'),
                                               'issue':record.get('issue'),
                                               'pages':record.get('pages')},
                                              {'$set':{'cite':record.get('cite'),'download':record.get('download')}})


class CnkiJournalScraper:
    """ 抓取杂志文献

    :param dict,list journals: 抓取的杂志信息，list的每个元素是dict，键值包括journal，issn，start_year, end_year
    :param str proxy: 代理服务器
    :param int type: 浏览器类型，0为PhantomJS，1为Firefox
    :param bool multi: 是否启用多线性
    """
    def __init__(self, journals=None, proxy=None, type=1, multi=False):
        self.proxy = proxy
        self.type = type
        self.journals = journals
        self.multi = multi
        self.cnki_obj = None
        self.db = MongoDB()
        self.db.connect('paper','cliterature')

    def run(self):
        """ 运行爬虫

        :return: 无返回值
        """
        if isinstance(self.journals,dict):
            self.single_thread_start()

    def check_connection(self, max_connection_number=10):
        """ 连接并返回是否连接信息

        :param int max_connection_number: 最大连接次数
        :return: 返回是否成功连接
        :rtype: bool
        """
        is_proxy_successful = False
        max_connection_number = max_connection_number
        i = 1
        while not is_proxy_successful:
            proxy = random.choice(self.proxy)
            print(self.journals.get('journal'),'\t',proxy)

            self.cnki_obj = CnkiScraper(proxy=proxy,type=1)
            if self.cnki_obj.is_connected():
                is_proxy_successful = True
            else:
                self.cnki_obj.close()
                time.sleep(5)
            i += 1
            if i > max_connection_number:
                return False
        return True

    def single_thread_start(self):
        """ 单线程爬虫

        :return: 无返回值
        """
        # 设置issn，起始年份和终止年份
        journal = self.journals.get('journal')
        issn = self.journals.get('issn')
        start_year = self.journals.get('start_year')
        end_year = self.journals.get('end_year')

        # 检验是否成功连接网站，如果不成功，报错
        if not self.check_connection():
            raise Exception

        # 在网页上设定查询字符串，选择年份，然后提交
        query_str = ''.join(["SN='",issn,"'"])
        self.cnki_obj.set_query(query_str)
        time.sleep(1)
        self.cnki_obj.set_period(start_period=start_year,end_period=end_year)
        time.sleep(1)
        self.cnki_obj.submit()

        # 转换到结果显示框架
        self.cnki_obj.switch_to_result_frame()

        # 记录查询得到的文献数量，用来进行后期核对
        total_number = self.cnki_obj.number_of_literature()
        # 切换到每页50条文献的显示
        self.cnki_obj.browser.interact_one_time(location='#id_grid_display_num > a:nth-child(3)',click=True)
        time.sleep(1)

        # 选择所有文献
        self.cnki_obj.select_all_literature()

        # 如果存在下一页，那么点击进入下一页，并选择所有文献
        while self.cnki_obj.is_exist_next_page():
            self.cnki_obj.go_next()
            time.sleep(2)
            self.cnki_obj.select_all_literature()

        #导出所有文献
        self.cnki_obj.export_literature()
        time.sleep(2)
        # 对文献进行一系列操作，并抓取文献到soups
        self.cnki_obj.child_operation()

        # 如果文献数量正确，插入文献到数据库
        literatures = self.cnki_obj.export_to_dict()
        print(len(literatures),total_number,type(len(literatures)),type(total_number),int(total_number))
        if len(literatures) == int(total_number):
            self.insert_to_db(literatures)
        self.cnki_obj.close()

    def insert_to_db(self, literatures=None):
        for record in literatures:
            print(record['title'],record['journal'],record['year'],record['issue'],record.get('pages'))
            if record.get('author') is None:
                print('No author!')
                continue
            result = self.db.collection.find_one({'title':record.get('title'),
                                         'journal':record.get('journal'),
                                         'year':record.get('year'),
                                         'issue':record.get('issue'),
                                         'pages':record.get('pages')})
            if result is None:
                print('Insert...!')
                self.db.collection.insert_one(record)


if __name__ == '__main__':
    pmanager = ProxyManager()

    cnki_interface = CnkiScraperInterface(proxy=pmanager.recommended_proxies(10))
    literatures = cnki_interface.query(querystr="JN='经济研究'",
                                       period={'start_year':'2012'},
                                       subject=['经济与管理科学'],
                                       limit=100)
    cnki_interface.insert_to_db(literatures=literatures,collection='clit')

    '''
    # 杂志
    JOURNALS = ['经济研究', '中国社会科学', '经济学(季刊)', '金融研究', '人口研究', '世界经济', '管理世界',
                '中国工业经济', '经济地理', '中国农村经济', '经济学家', '数量经济技术经济研究', '财贸经济', '世界经济文汇']
    # 杂志对应的ISSN
    ISSNS = ['0577-9154', '1002-4921', '2095-1086', '1002-7246', '1000-6087', '1002-9621', '1002-5502',
             '1006-480X', '1000-8462', '1002-8870', '1003-5656', '1000-3894', '1002-8102', '0488-6364']

    START_YEAR = '2016'
    END_YEAR = '2016'

    for i in range(9,len(JOURNALS)):
        journal = {'journal':JOURNALS[i],'issn':ISSNS[i],'start_year':START_YEAR,'end_year':END_YEAR}
        print(journal)
        jscraper = CnkiJournalScraper(journals=journal,proxy=pmanager.recommended_proxies(10),type=0)
        jscraper.run()

    #journals = {'journal':'经济研究','issn':'0577-9154','start_year':'2015','end_year':'2015'}
    #jscraper = CnkiJournalScraper(journals=journals,proxy=pmanager.recommended_proxies(10),type=0)
    #jscraper.run()'''
