# coding = UTF-8

"""
@title: 高德地图城市拥挤日均指数爬虫
@introduction：爬取高德地图城市日均交通拥堵延时指数
@author：glen
@date：2017.12.19
@tag：scraper traffic_congestion
@scheduler: 每月的1号的晚上23点
"""

import time
from datetime import datetime
from application.citydigest.class_city_congest import CityCongestionScraper

# 0. 参数设定
# 计时器
start = time.time()
using_proxy = True


# 爬取数据
congest_scraper = CityCongestionScraper(using_proxy=True)
congest_scraper.scrape_city_daily_congestion(citycode=None, year=2017, quarter=4)

# 输出基本信息
print('scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)