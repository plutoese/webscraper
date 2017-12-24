# coding = UTF-8

"""
@title: 高德地图城市拥挤每小时均值指数爬虫
@introduction：爬取高德地图城市每小时平均交通拥堵延时指数
@author：glen
@date：2017.12.19
@tag：scraper traffic_congestion
@scheduler: 每天早上8点
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
congest_scraper.scrape_city_hourly_congestion(citycode=None)

# 输出基本信息
print('Hourly City Congestion scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)