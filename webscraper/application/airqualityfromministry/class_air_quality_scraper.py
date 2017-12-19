# coding=UTF-8

"""
=========================================
空气质量日报爬虫
=========================================

:Author: glen
:Date: 2017.12.17
:Tags: asyncio scraper
:abstract: 中国环境保护部的空气质量日报爬虫，网址：http://datacenter.mep.gov.cn:8099/ths-report/report!list.action

**类**
==================
AirQualityScraper
    空气质量日报爬虫

**使用方法**
==================


**示范代码**
==================
::

"""

import pymongo
import datetime
import time
import arrow
import copy
import re
import json
from bs4 import BeautifulSoup
from libs.database.class_mongodb import MongoDB, MonCollection
from libs.webscraper.class_async_static_scraper import AsyncStaticScraper


class AirQualityScraper:
    mongo = MongoDB()
    conn = MonCollection(mongo, 'scraperdata', 'airqualityfromMin').collection

    def __init__(self, start_date=None, end_date=None, xmlname='1462259560614', using_proxy=False):
        """ 初始化空气质量爬虫

        :param str start_date: 起始日期
        :param str end_date: 终止日期
        :param xmlname: 网站所需参数
        """

        # 如果起始起始日期缺省，就设置起始和终止日期为昨天
        if start_date is None:
            last_date = sorted(AirQualityScraper.conn.find().distinct('OPER_DATE'))[-1]
            start_date = last_date + datetime.timedelta(days=1)
            start_date = start_date.strftime(format='%Y-%m-%d')

        if end_date is None:
            today = arrow.utcnow().shift(days=-1)
            end_date = today.strftime(format='%Y-%m-%d')

        # 设置待爬取的网址
        self._url = 'http://datacenter.mep.gov.cn:8099/ths-report/report!list.action'
        # 请求的方式为post
        self._request_type = 'post'
        # 设置post data
        self._request_data = {'xmlname': xmlname, 'V_DATE': start_date, 'E_DATE': end_date}
        # 待爬取的总记录数
        self._total_record = 0
        # 待爬取的总页数
        self._total_page = 0

        # 待爬取的网页列表
        self._urls = []
        # 是否启用代理服务器
        self._using_proxy = using_proxy

    def init(self):
        """ 启动爬虫前的初始化工作，主要提取记录总数和页面总数

        :return: 无返回值
        """
        # 启动爬虫，爬取基础网页
        scraper = AsyncStaticScraper(urls=[(self._url,self._request_data)],request_type='post',using_proxy=self._using_proxy)
        scraper.start()

        # 提取总页数和总页数到变量self._total_record和self._total_page
        html_obj = BeautifulSoup(scraper.result[0][0], 'lxml')
        mvalue = html_obj.select('.report_page')
        self._total_page = int(re.split('\<', re.split('总页数：', re.sub('\s+', '', str(mvalue[0])))[1])[0])
        self._total_record = int(re.split('条',re.split('总记录数：',re.sub('\s+','',str(mvalue[0])))[1])[0])

        # 设置self.urls
        for n in range(1,self._total_page+1):
            requests_data = copy.copy(self._request_data)
            requests_data['page.pageNo'] = str(n)
            self._urls.append((self._url,requests_data))

    def start_scrape(self):
        """ 启动爬虫进行爬取

        :return: 无返回值
        """
        # 启动爬虫
        scraper = AsyncStaticScraper(urls=self._urls,request_type='post',using_proxy=self._using_proxy,processor=AirQualityScraper.parse)
        scraper.start()

        # 保存爬虫数据到results
        results = []
        for page_data in scraper.result[0]:
            results.extend(page_data)

        # 打印结果
        print('\n{}Result{}\nTotal Record: {}, Actually Scraped Record: {}!'.format('-'*20,'-'*20,self._total_record,len(results)))
        if len(results) < self._total_record:
            print('Failed: {} < {}'.format(len(results), self._total_record))
            raise Exception

    @classmethod
    def parse(cls,request_data):
        """ 处理爬虫获取的网页数据

        :param request_data: 爬取的原始数据
        :return: 返回处理过的数据
        """
        # 解析原始的爬取数据
        html_obj = BeautifulSoup(request_data, 'lxml')
        mvalue = html_obj.select('#gisDataJson')
        page_data = json.loads(mvalue[0]['value'])
        for item in page_data:
            item['OPER_DATE'] = datetime.datetime.strptime(item['OPER_DATE'],'%Y-%m-%d')
            found = cls.conn.find_one(item)
            if found is None:
                print('insert...', len(item), item)
                cls.conn.insert_one(item)
            else:
                print('Already exists: ', item)
        return page_data


if __name__ == '__main__':

    start = time.time()
    air_scraper = AirQualityScraper(using_proxy=True)
    air_scraper.init()
    air_scraper.start_scrape()
    print('Total: {}'.format(time.time() - start))

    '''
    mongo = MongoDB()
    conn = MonCollection(mongo, 'scraperdata', 'airqualityfromMin').collection
    #conn.update_many({'OPER_DATE':'2017-08-22'},{'$set': {'OPER_DATE': datetime.datetime.strptime('2017-08-22','%Y-%m-%d')}})
    print(sorted(conn.find().distinct('OPER_DATE')))
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING)])
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING),("CITYCODE", pymongo.ASCENDING)])'''



