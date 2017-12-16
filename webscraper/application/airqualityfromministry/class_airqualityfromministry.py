# coding = UTF-8

from application.generalframework.class_staticframework import StaticFramework
from libs.class_htmlextractor import HtmlTableParser
from libs.class_staticsitescraper import StaticSiteScraper, BeautifulSoup
import random
from libs.class_htmlparser import HtmlParser
from libs.class_proxymanager import ProxyManager
from libs.class_mongodb import MongoDB
from libs.class_multithread import MultiThread
import re


class AirQualityFromMinistry:
    def __init__(self, web_template=None, web_range=None, additional_info=None):
        self.static_framework = StaticFramework()

        # 设置数据库
        self.air_db = MongoDB()
        self.air_db.connect('application', 'airquality')

        # 设置计数数据库
        self.web_db = MongoDB()
        self.web_db.connect('cache', 'airqualityinfo')

        self._additional_info = additional_info
        self._web_temple = web_template
        self._web_range = web_range

        self.setup_info_db()

    def setup_info_db(self):
        for num in self._web_range:
            found = self.web_db.collection.find_one({'web':self._web_temple.format(str(num))})
            if found is None:
                self.web_db.collection.insert_one({'web':self._web_temple.format(str(num))})

    def run(self, using_proxy=True, check_num=30, multi_thread=False):
        self.static_framework.run(using_proxy=using_proxy, parse_fn=HtmlTableParser, parse_param={'css':'#report1'},
                                  transform_fn=self.transform_table,transform_param={}, check_num=check_num,
                                  db_store=self.air_db, web_recorder=self.web_db, multi_thread=multi_thread)

    def transform_table(self,data_table=None):
        result = []
        for item in data_table:
            if re.match('^序号$', item[0]) is not None:
                variable = item[1:]
            if re.match('^\d+$', item[0]) is not None:
                record = dict(zip(variable, item[1:]))
                if self._additional_info is not None:
                    record.update(self._additional_info)
                print(record)
                result.append(record)
        return result


if __name__ == '__main__':
    air_grasper = AirQualityFromMinistry(web_template='http://datacenter.mep.gov.cn/report/air_daily/air_dairy.jsp?city=&startdate=2014-01-01&enddate=2016-12-02&page={}',
                                         web_range=range(1,5),
                                         additional_info={'source':'中国环境保护部数据中心'})
    air_grasper.run(using_proxy=False,multi_thread=1)
