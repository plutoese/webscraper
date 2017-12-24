# coding=UTF-8

"""
=========================================
高德交通大数据爬虫
=========================================

:Author: glen
:Date: 2017.12.18
:Tags: amap transportation
:abstract: 高德地图的交通大数据爬虫，网址：http://report.amap.com/detail.do?city=310000

**类**
==================
CityCongestionScraper
    高德交通大数据爬虫

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
from itertools import product
from collections import deque
from libs.database.class_mongodb import MongoDB, MonCollection
from libs.webscraper.class_async_static_scraper import AsyncStaticScraper


class CityCongestionScraper:
    # 连接交通大数据库
    mongo = MongoDB()

    def __init__(self, using_proxy=False):

        # 是否启用代理服务器
        self._using_proxy = using_proxy

        # 获得高德交通大数据的城市列表
        self._cities = self._get_cities()
        # 城市的字典，城市代码：城市名称
        self._cities_dict = {str(item['code']):item['name'] for item in self._cities}

    def scrape_city_daily_congestion(self, citycode=None, year=2017, quarter=4):
        """ 爬取每天的城市交通拥堵延时指数

        :param str,list citycode: 城市代码
        :param int,str,list year: 年份
        :param int,str,list quarter: 季节
        :return: 无返回值
        """
        var_name = '交通拥堵延时指数'
        url_template = 'http://report.amap.com/ajax/cityDailyQuarterly.do?cityCode={citycode}&year={year}&quarter={quarter}'
        conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata', 'citydailycongestionfromamap').collection

        # 处理年份，转换为列表
        if isinstance(year,(int,str)):
            year = [str(year)]
        # 处理季节，转换为列表
        if isinstance(quarter,(int,str)):
            quarter = [str(quarter)]
        # 处理城市代码
        if citycode is None:
            citycode = [item['code'] for item in self._cities]
        else:
            if isinstance(citycode,(int,str)):
                citycode = [str(citycode)]

        # 创建待爬取的网址
        urls = []
        for city in citycode:
            for myear,mquarter in product([str(y) for y in year],[str(q) for q in quarter]):
                urls.append(url_template.format(citycode=city,year=myear,quarter=mquarter))

        urls_list = CityCongestionScraper.split(urls=urls)

        for to_urls in urls_list:
            # 爬取数据
            scraper = AsyncStaticScraper(urls=to_urls, request_type='get', response_type='text', using_proxy=self._using_proxy)
            scraper.start()

            # 把爬虫得到的数据进行解析，然后存入数据库
            for result, url in scraper.result:
                city_code = re.split('\&',re.split('cityCode=',url)[1])[0]
                city = self._cities_dict[city_code]
                result_data = json.loads(result)
                for i in range(len(result_data['categories'])):
                    date = datetime.datetime.strptime(result_data['categories'][i],'%Y-%m-%d')
                    value = result_data['serieData'][i]
                    record = {'city':city, 'acode':city_code, 'date':date, 'value':value, 'name':var_name}
                    found = conn.find_one(record)
                    if found is None:
                        print('insert...', len(record), record)
                        conn.insert_one(record)
                    else:
                        print('Already exists: ', record)

            print('Let us take a break!.....times.{}'.format(str(i + 1)))
            time.sleep(random.randint(5, 80))

    def scrape_city_hourly_congestion(self, citycode=None):
        """ 爬取每小时的城市交通拥堵延时指数

        :param citycode:
        :return:
        """
        var_name = '交通拥堵延时指数'

        url_fmt = 'http://report.amap.com/ajax/cityHourly.do?cityCode={}'
        conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata', 'cityhourlycongestionfromamap').collection

        # 处理城市代码
        if citycode is None:
            citycode = [item['code'] for item in self._cities]
        else:
            if isinstance(citycode, (int, str)):
                citycode = [str(citycode)]

        urls = []
        for city_code in citycode:
            urls.append(url_fmt.format(city_code))

        urls_list = CityCongestionScraper.split(urls=urls)

        for to_urls in urls_list:

            scraper = AsyncStaticScraper(urls=to_urls, request_type='get', using_proxy=self._using_proxy)
            scraper.start()

            for result, url in scraper.result:
                city_code = re.split('\&', re.split('cityCode=', url)[1])[0]
                city = self._cities_dict[city_code]
                result_data = json.loads(result)
                for item in result_data:
                    date_time = datetime.datetime.fromtimestamp(int(item[0]/1000))
                    record = {'datetime':date_time, 'value':item[1], 'city':city, 'acode':city_code, 'name':var_name}
                    found = conn.find_one(record)
                    if found is None:
                        print('insert...', len(record), record)
                        conn.insert_one(record)
                    else:
                        print('Already exists: ', record)

            print('Let us take a break!.....times.{}'.format(str(i + 1)))
            time.sleep(random.randint(5, 80))

    def scrape_city_district_realtime_congestion(self, citycode=None):
        url_fmt = 'http://report.amap.com/ajax/districtRank.do?linksType=1&cityCode={}'
        conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata', 'citydistricthourlycongestionfromamap').collection

        # 处理城市代码
        if citycode is None:
            citycode = [item['code'] for item in self._cities]
        else:
            if isinstance(citycode, (int, str)):
                citycode = [str(citycode)]

        urls = []
        for city_code in citycode:
            urls.append(url_fmt.format(city_code))

        urls_list = CityCongestionScraper.split(urls=urls)

        for to_urls in urls_list:

            scraper = AsyncStaticScraper(urls=to_urls, request_type='get', using_proxy=self._using_proxy)
            scraper.start()

            for result, url in scraper.result:
                city_code = re.split('\&', re.split('cityCode=', url)[1])[0]
                city = self._cities_dict[city_code]
                result_data = json.loads(result)
                for item in result_data:
                    date_time = datetime.datetime.now()
                    print(city, item['name'],item['index'],item['speed'])
                    record = {'datetime': date_time, '交通拥堵延时指数': item['index'], 'city': city, 'acode': city_code,
                              '旅行速度': item['speed'], 'district': item['name']}
                    found = conn.find_one(record)
                    if found is None:
                        print('insert...', len(record), record)
                        conn.insert_one(record)
                    else:
                        print('Already exists: ', record)

            print('Let us take a break!.....times.{}'.format(str(i + 1)))
            time.sleep(random.randint(5, 80))

    def scrape_city_highway_realtime_congestion(self, citycode='310000', period='day'):
        var_name = '交通拥堵延时指数'
        if period == 'day':
            url_fmt = 'http://report.amap.com/ajax/roadDetail.do?roadType=1&timeType=1&cityCode={}&lineCode={}'
            conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata',
                                 'cityhighwaycongestioninadayfromamap').collection
        else:
            url_fmt = 'http://report.amap.com/ajax/roadDetail.do?roadType=1&timeType=2&cityCode={}&lineCode={}'
            conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata',
                                 'cityhighwaycongestioninaweekfromamap').collection

        highway_info_conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata', 'cityhighwayinfofromamap').collection

        # 处理urls
        urls = []
        for record in highway_info_conn.find({'acode':citycode},projection={'_id':False,'rid':True}):
            urls.append(url_fmt.format(citycode,record['rid']))

        scraper = AsyncStaticScraper(urls=urls, request_type='get', using_proxy=self._using_proxy)
        scraper.start()

        for result, url in scraper.result:
            rid = re.split('lineCode=', url)[1]
            city = self._cities_dict[citycode]
            result_data = json.loads(result)
            for item in result_data:
                date_time = datetime.datetime.fromtimestamp(int(item[0] / 1000))
                record = {'datetime':date_time, 'value':item[1], 'city':city, 'acode':citycode, 'name':var_name, 'rid':rid}
                found = conn.find_one(record)
                if found is None:
                    print('insert...', len(record), record)
                    conn.insert_one(record)
                else:
                    print('Already exists: ', record)

    def getCityHighwayInfo(self,citycode='310000',period='insevendays'):
        if period == 'realtime':
            url_fmt = 'http://report.amap.com/ajax/roadRank.do?roadType=1&timeType=0&cityCode={}'
        elif period == 'yesterday':
            url_fmt = 'http://report.amap.com/ajax/roadRank.do?roadType=1&timeType=1&cityCode={}'
        elif period == 'insevendays':
            url_fmt = 'http://report.amap.com/ajax/roadRank.do?roadType=1&timeType=2&cityCode={}'
        else:
            print('Unknown Period')
            raise Exception
        conn = MonCollection(CityCongestionScraper.mongo, 'scraperdata', 'cityhighwayinfofromamap').collection

        urls = []
        urls.append(url_fmt.format(citycode))

        scraper = AsyncStaticScraper(urls=urls, request_type='get', response_type='text',using_proxy=self._using_proxy)
        scraper.start()

        for result, url in scraper.result:
            city = self._cities_dict[citycode]
            result_data = json.loads(result)['tableData']
            for item in result_data:
                item.pop('coords')
                record = {'dir': item['dir'], 'city': city, 'acode': citycode, 'name': item['name'],
                          'rid': item['id'], 'length': item['length']}
                found = conn.find_one(record)
                if found is None:
                    print('insert...', len(record), record)
                    conn.insert_one(record)
                else:
                    print('Already exists: ', record)

    def _get_cities(self):
        """ 辅助函数，返回城市列表

        :return: 返回城市列表
        """
        url = 'http://report.amap.com/ajax/getCityInfo.do'
        scraper = AsyncStaticScraper(urls=[url],request_type='get',response_type='text',using_proxy=self._using_proxy)
        scraper.start()

        return json.loads(scraper.result[0][0])

    @classmethod
    def split(cls, urls, limit=10):
        urls_deque = deque(urls)

        split_urls = []
        while len(urls_deque) > 0:
            if len(urls_deque) >= limit:
                split_urls.append([urls_deque.popleft() for i in range(limit)])
            else:
                split_urls.append([urls_deque.popleft() for i in range(len(urls_deque))])

        return split_urls

    @classmethod
    def city_code(self):
        return self._cities



if __name__ == '__main__':

    start = time.time()
    congest_scraper = CityCongestionScraper(using_proxy=False)
    #congest_scraper.scrape_city_daily_congestion()
    #congest_scraper.scrape_city_highway_realtime_congestion()
    congest_scraper.getCityHighwayInfo(period='realtime')
    #air_scraper.start_scrape()
    #print('Total: {}'.format(time.time() - start))

    '''
    mongo = MongoDB()
    conn = MonCollection(mongo, 'scraperdata', 'airqualityfromMin').collection
    #conn.update_many({'OPER_DATE':'2017-08-22'},{'$set': {'OPER_DATE': datetime.datetime.strptime('2017-08-22','%Y-%m-%d')}})
    print(sorted(conn.find().distinct('OPER_DATE')))
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING)])
    #conn.create_index([("OPER_DATE", pymongo.ASCENDING),("CITYCODE", pymongo.ASCENDING)])'''



