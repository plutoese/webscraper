# coding=UTF-8

import re
from bs4 import BeautifulSoup
from libs.class_proxymanager import ProxyManager
from libs.class_staticsitescraper import StaticSiteScraper
from libs.class_htmlparser import HtmlParser
from libs.class_Excel import Excel
from libs.class_mongodb import MongoDB

# 0. Single web grasp --- air quality
pmanager = ProxyManager()
ramdomproxy = pmanager.recommended_proxies(number=1)[0]
'''
site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/shanghai-201609.html',proxy=ramdomproxy)
html = site_scraper.get_current_page_content()

# html parsing
htmlparser = HtmlParser(html_content=html)
table = htmlparser.table('.b')
outfile = r'd:\down\quality.xlsx'
moutexcel = Excel(outfile)
moutexcel.new().append(table, 'mysheet')
moutexcel.close()

# 1. Multi web grasp --- air quality
site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/',proxy=ramdomproxy)
print(site_scraper.get_current_page_content().title)
site_scraper.get_links(page_url='shanghai-201610.html',condition='^/aqi/shanghai-2016.+',cache=True)

outfile = r'd:\down\air_quality.xlsx'
moutexcel = Excel(outfile)
new_excel = moutexcel.new()

db = MongoDB()
db.connect('cache','scraper')
result = db.collection.find()
for item in result:
    htmlparser = HtmlParser(html_content=item['content'])
    table = htmlparser.table('.b')
    new_excel.append(table, re.split('\.',re.split('-',item['web'])[1])[0])
moutexcel.close()'''

'''
site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/',proxy=ramdomproxy)
html = site_scraper.get_current_page_content()

# html parsing
regions = dict()
htmlparser = HtmlParser(html_content=html)
table = htmlparser.bs_obj.select('.citychk > dl')
for item in table:
    row = item.find_all("a")
    for unit in row:
        three = re.split('\"',str(unit))
        #print(re.split('\.',three[1])[0])
        #print(re.split('\s+<',re.split('>',three[2])[1])[0])
        regions[re.split('\s+<',re.split('>',three[2])[1])[0]] = re.split('\.',three[1])[0]
print(regions)
print(len(regions))'''
