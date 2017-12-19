# coding = UTF-8

"""
@title: 高德地图城市市区高架拥堵指数爬虫
@introduction：爬取高德地图高架拥堵指数
@author：glen
@date：2017.12.19
@tag：scraper highway
@scheduler: 每隔一天
"""

import time
from datetime import datetime
from application.citydigest.class_city_congest import CityCongestionScraper

# 0. 参数设定
# 计时器
start = time.time()
using_proxy = True


# 爬取数据
congest_scraper = CityCongestionScraper(using_proxy=False)
congest_scraper.scrape_city_highway_realtime_congestion(period='day')
congest_scraper.scrape_city_highway_realtime_congestion(period='week')

# 输出基本信息
print('Hourly City Congestion scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)