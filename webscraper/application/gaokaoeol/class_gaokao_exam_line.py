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
import random
from bs4 import BeautifulSoup
from libs.database.class_mongodb import MongoDB, MonCollection
from libs.webscraper.class_async_static_scraper import AsyncStaticScraper


class GaoKaoExamLineScraper:
    mongo = MongoDB()

    def __init__(self, using_proxy=False):

        # 是否启用代理服务器
        self._using_proxy = using_proxy
        self._check_con = MonCollection(GaoKaoExamLineScraper.mongo, 'cache', 'gaokaorecord').collection

    def setup_scrape_college_enroll_student_number_db(self, records_per_page=50):
        url_fmt = 'https://data-gkcx.eol.cn/soudaxue/queryProvinceScore.html?messtype=jsonp&lunum=1&callback=jQuery18308512253654296293_1513822349743&provinceforschool=&schooltype=&page={}&size=50&keyWord=&schoolproperty=&schoolflag=&province=&fstype=&zhaoshengpici=&fsyear=&_=1513822349898'
        url = url_fmt.format('1')
        # 爬取数据
        scraper = AsyncStaticScraper(urls=[url], request_type='get', response_type='text', using_proxy=self._using_proxy)
        scraper.start()

        for result, url in scraper.result:
            content = re.sub('\s+', '', re.split('\)', re.split('\(', result)[1])[0])
            result_data = json.loads(content)
            total_record = int(result_data['totalRecord']['num'])
            pages = int(total_record/records_per_page) + 1
            record_number_of_last_page = total_record % records_per_page

        for i in range(1,pages+1):
            if i == pages:
                count = record_number_of_last_page
            else:
                count = records_per_page

            record = {'url':url_fmt.format(str(i)), 'count': count, 'scraped': 0}
            GaoKaoExamLineScraper.update_db(self._check_con, record)

    @classmethod
    def update_db(cls, conn, record):
        found = conn.find_one(record)
        if found is None:
            print('insert...: {}'.format(record))
            conn.insert_one(record)
        else:
            print('Already exists: ', record)


    def scrape_college_enroll_student_number(self, limit=100):
        """ 爬取每天的城市交通拥堵延时指数

        :param str,list citycode: 城市代码
        :param int,str,list year: 年份
        :param int,str,list quarter: 季节
        :return: 无返回值
        """
        gaokao_conn = MonCollection(GaoKaoExamLineScraper.mongo, 'scraperdata', 'gaokaocollegeenrollstudent').collection

        # 创建待爬取的网址
        urls = [item['url'] for item in self._check_con.find({'scraped':0},limit=limit)]

        # 爬取数据
        scraper = AsyncStaticScraper(urls=urls, request_type='get', response_type='text', using_proxy=self._using_proxy)
        scraper.start()

        # 把爬虫得到的数据进行解析，然后存入数据库
        for result, url in scraper.result:
            count = 0
            content = re.sub('\s+', '', re.split('\)', re.split('\(', result)[1])[0])
            result_data = json.loads(content)
            for item in result_data['school']:
                record = {'学校':item['schoolname'], '招生地区':item['localprovince'], '学校地区':item['province'],
                          '文理科':item['studenttype'], '录取批次':item['batch'], '录取平均分':item['var_score'],
                          '录取最高分': item['max'], '录取最低分': item['min'], '录取人数': item['num'],
                          '分差': item['fencha'], '省控线': item['provincescore'], '年份':item['year']}
                found = gaokao_conn.find_one(record)
                if found is None:
                    print('insert...: {}'.format(record))
                    gaokao_conn.insert_one(record)
                else:
                    print('Already exists: ', record)
                count += 1
            track_record = {'url':url, 'count':count}
            self._check_con.find_one_and_update(filter=track_record,update={'$set':{'scraped':1}})


if __name__ == '__main__':
    start = time.time()
    air_scraper = GaoKaoExamLineScraper(using_proxy=True)
    #air_scraper.setup_scrape_college_enroll_student_number_db()
    #air_scraper.scrape_college_enroll_student_number(limit=20)

    for i in range(20):
        air_scraper.scrape_college_enroll_student_number(limit=10)
        print('Let us take a break!.....times.{}'.format(str(i+1)))
        time.sleep(random.randint(5,80))
    print('Total: {}'.format(time.time() - start))

    '''
    mongo = MongoDB()
    conn = MonCollection(mongo, 'scraperdata', 'airqualityfromMin').collection
    #conn.update_many({'OPER_DATE':'2017-08-22'},{'$set': {'OPER_DATE': datetime.datetime.strptime('2017-08-22','%Y-%m-%d')}})
    print(sorted(conn.find().distinct('OPER_DATE')))
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING)])
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING),("CITYCODE", pymongo.ASCENDING)])'''



