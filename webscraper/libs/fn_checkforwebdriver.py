# coding=UTF-8

from libs.class_headlessbrowser import HeadlessBrowser
from selenium.webdriver.common.by import By
from libs.class_mongodb import MongoDB
import datetime


def check_for_webdriver(website=None,timeout=5,type=1,ready_check=None):
    db = MongoDB()
    db.connect('cache','proxy')
    proxies = [item['proxy'] for item in db.collection.find(projection={'_id':0,'proxy':1})]
    for proxy in proxies:
        start_time = datetime.datetime.now()
        browser = HeadlessBrowser(proxy=proxy,timeout=timeout,type=type)
        if browser.surf(website=website,ready_check=ready_check):
            webdriver_speed = (datetime.datetime.now() - start_time).total_seconds()
            db.collection.find_one_and_update({'proxy':proxy},{'$set': {'checked':1,'webdriverspeed':webdriver_speed}})
        else:
            db.collection.find_one_and_update({'proxy':proxy},{'$set': {'checked':0,'webdriverspeed':-1}})
        browser.quit()

check_for_webdriver(website='http://gkcx.eol.cn/soudaxue/queryProvinceScore.html?page=1&scoreSign=3',type=0,
                    ready_check=(By.CSS_SELECTOR,'#pageid'))