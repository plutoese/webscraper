# coding = UTF-8

from libs.class_staticsitescraper import StaticSiteScraper, BeautifulSoup
import random
from libs.class_htmlparser import HtmlParser
import re
from libs.class_mongodb import MongoDB

for i in range(1,2):
    web = 'http://datacenter.mep.gov.cn/report/air_daily/air_dairy.jsp?city=&startdate=2014-01-01&enddate=2016-12-02&page={}'.format(str(i))
    site_scraper = StaticSiteScraper(web)
    html_content = site_scraper.get_current_page_content()

    htmlparser = HtmlParser(html_content=html_content)
    data_table = htmlparser.table('#report1')

    print(data_table)

    result = []
    for item in data_table:
        if re.match('^序号$',item[0]) is not None:
            variable = item[1:]
        if re.match('^\d+$',item[0]) is not None:
            record = dict(zip(variable,item[1:]))
            print(record)
            result.append(record)
    print(len(result))

count_db = MongoDB()
count_db.connect('cache', 'count')
count_db.collection.insert_one({'number':4})
print(count_db.collection.find().distinct('number'))
