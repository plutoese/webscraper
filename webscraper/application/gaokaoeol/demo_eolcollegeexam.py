# coding=UTF-8

import random
from urllib.parse import urljoin
from libs.class_staticsitescraper import StaticSiteScraper
from libs.class_proxymanager import ProxyManager
from libs.class_dynamicscraper import DynamicScraper
from selenium.webdriver.common.by import By
import re

# proxy
pmanager = ProxyManager()
ramdomproxy = random.choice(pmanager.best_speed_proxies)
print(ramdomproxy)

str_format = 'http://gkcx.eol.cn/soudaxue/queryProvinceScore.html?page={}&scoreSign=3'
web_address = str_format.format(1)

'''
site_scraper = StaticSiteScraper(web_address,proxy=ramdomproxy)
bsobj = site_scraper.get_current_page_content(beautifulsoup=True)
print(bsobj.select_one('#queryschoolad'))'''

dscraper = DynamicScraper(website=web_address,label='eol.cn')
dscraper.surf(proxies=pmanager.best_speed_proxies,proxy_type='http',timeout=5,type=0,
              ready_check=(By.CSS_SELECTOR,'#pageid'))
result = dscraper.act_once([('get_text',{'location':'#queryschoolad'})])


for item in re.split('\n',result):
    print(re.split('\s+',item))
