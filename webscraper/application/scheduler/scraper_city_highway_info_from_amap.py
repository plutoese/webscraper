# coding = UTF-8

"""
@title: 高德地图城市市区高架信息爬虫
@introduction：爬取高德地图高架信息
@author：glen
@date：2017.12.19
@tag：scraper highway
@scheduler: 每隔一个小时爬取
"""

import time
from datetime import datetime
from application.citydigest.class_city_congest import CityCongestionScraper

# 0. 参数设定
# 计时器
start = time.time()
using_proxy = True


# 爬取数据
congest_scraper = CityCongestionScraper(using_proxy=using_proxy)
congest_scraper.getCityHighwayInfo(period='realtime')

# 输出基本信息
print('Hourly City Congestion scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)