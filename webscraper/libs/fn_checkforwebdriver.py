# coding=UTF-8

from libs.class_headlessbrowser import HeadlessBrowser
from selenium.webdriver.common.by import By
from libs.class_mongodb import MongoDB


def check_for_webdriver(website=None,timeout=5,type=1,ready_check=None):
    db = MongoDB()
    db.connect('cache','proxy')
    proxies = [item['proxy'] for item in db.collection.find(projection={'_id':0,'proxy':1})]
    for proxy in proxies:
        browser = HeadlessBrowser(proxy=proxy,timeout=timeout,type=type)
        if browser.surf(website=website,ready_check=ready_check):
            db.collection.find_one_and_update({'proxy':proxy},{'$set': {'checked':1}})
        else:
            db.collection.find_one_and_update({'proxy':proxy},{'$set': {'checked':0}})
        browser.quit()

check_for_webdriver(website='https://www.hqms.org.cn/usp/roster/index.jsp',
                    ready_check=(By.CSS_SELECTOR,'.table_result'))