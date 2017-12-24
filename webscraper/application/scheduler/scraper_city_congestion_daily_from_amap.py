# coding = UTF-8

"""
@title: scraper of daily city congestion from amap
@introduction：scraper of daily city congestion from amap
@author：glen
@date：2017.12.19
@tag：scraper traffic_congestion
@scheduler: Every week
"""

import time
from datetime import datetime
from application.citydigest.class_city_congest import CityCongestionScraper

# 0. setup
# timer
start = time.time()
using_proxy = True


# scraping
congest_scraper = CityCongestionScraper(using_proxy=using_proxy)
congest_scraper.scrape_city_daily_congestion(citycode=None, year=2017, quarter=4)

# output information
print('Daily city congestion scraper date: ',datetime.now())
print('Total: {}'.format(time.time() - start))
print('-'*50)