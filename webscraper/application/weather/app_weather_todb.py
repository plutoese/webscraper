# coding = UTF-8

import re
from bs4 import BeautifulSoup
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
import random
from libs.class_headlessbrowser import HeadlessBrowser
from libs.class_multithread import MultiThread


class WeatherDBCreator:
    def __init__(self, db='application',collection='weather'):
        self._db = MongoDB()
        self._db.connect(db,collection)

        self.pmanger = ProxyManager()

    def one_insertion(self,website=None):
        done = False
        while not done:
            done = self.record_to_db(website=website)

    def multi_thread(self,websites=None):
        threads = []
        for web in websites:
            t = MultiThread(self.one_insertion,args=(web,),name=web)
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def record_to_db(self,website=None):
        if re.search('index\.html',website) is None:
            try:
                ramdomproxy = random.choice(self.pmanger.recommended_proxies(10))
                browser = HeadlessBrowser(proxy=ramdomproxy,type=0)
                browser.surf(website)

                title = browser.get_text(location=browser.locate('.box-t-l'))
                region = re.split('\d{4}',title)[0]
                year = re.findall('\d{4}',title)[0]
                month = re.findall('\d{1}月',title)[0][0]

                web_content = re.split('\n',browser.get_text(location=browser.locate('.tqtongji2')))
                print('region:{}, year:{}, month:{}'.format(region,year,month))

                vars = web_content[0:6]
                del web_content[0:6]

                start = [i for i in range(len(web_content)) if re.match('^\d+-\d+-\d+$',web_content[i]) is not None]
                start.append(len(web_content))

                for i in range(len(start)-1):
                    record_row = web_content[start[i]:start[i+1]]
                    if len(record_row) == 6:
                        one_record = dict(zip(vars,record_row))
                        one_record['region'] = region
                        one_record['year'] = year
                        one_record['month'] = month
                    else:
                        temperature = None
                        one_record = dict()
                        for unit in record_row:
                            if re.match('^\d+-\d+-\d+$',unit) is not None:
                                one_record['日期'] = unit
                            elif re.match('^\d+$',unit) is not None:
                                if temperature is None:
                                    temperature = unit
                                else:
                                    if int(unit) > int(temperature):
                                        one_record['最高气温'] = unit
                                        one_record['最低气温'] = temperature
                                    else:
                                        one_record['最高气温'] = temperature
                                        one_record['最低气温'] = unit
                            elif re.match('^[东南西北]+风$',unit) is not None:
                                one_record['风向'] = unit
                            elif re.match('^\d级$',unit) is not None:
                                one_record['风力'] = unit
                            else:
                                one_record['天气'] = unit

                    one_record['region'] = region
                    one_record['year'] = year
                    one_record['month'] = month
                    one_record['source'] = website

                    found = self._db.collection.find_one({'region':one_record['region'],'日期':one_record['日期']})
                    if found is None:
                        self._db.collection.insert_one(one_record)
                return True

            except Exception as e:
                print('Download Error: ',e)
                return False
        else:
            print('Not a valid website: ',website)
            return True

if __name__ == '__main__':
    db_scraper = MongoDB()
    db_scraper.connect('cache','scraper')
    records = db_scraper.collection.find()

    wdbcreator = WeatherDBCreator()

    db_data = MongoDB()
    db_data.connect('application','weather')
    web_set = set(db_data.collection.find().distinct('source'))

    max_number = 10
    websites = []
    for record in records[100:500]:
        wdbcreator.one_insertion(record.get('web'))



