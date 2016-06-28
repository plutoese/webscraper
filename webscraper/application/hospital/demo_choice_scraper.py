# coding=UTF-8

import re
import random
from libs.class_staticsitescraper import StaticSiteScraper
from libs.class_proxymanager import ProxyManager

pmanager = ProxyManager()
ramdomproxy = random.choice(pmanager.best_speed_proxies)
site_scraper = StaticSiteScraper('https://www.hqms.org.cn/usp/roster/index.jsp',proxy=ramdomproxy)
bsobj = site_scraper.get_current_page_content()
choices = re.split('\s+',(bsobj.select_one('.province_select').text))[2:]
print(choices[:len(choices)-1])