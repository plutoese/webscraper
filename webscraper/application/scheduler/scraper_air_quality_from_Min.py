# coding = UTF-8

"""
@title: 中国环境保护部城市空气质量日报数据爬虫
@introduction：爬取城市的空气质量信息
@author：glen
@date：2017.12.19
@tag：scraper air_quality
@scheduler: 每月的1、11、21号的中午12点
"""

import time
from datetime import datetime
from application.airqualityfromministry.class_air_quality_scraper import AirQualityScraper

# 0. 参数设定
# 计时器
start = time.time()
using_proxy = True


# 爬取数据
air_scraper = AirQualityScraper(using_proxy=using_proxy)
air_scraper.init()
air_scraper.start_scrape()

# 输出基本信息
print('scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)