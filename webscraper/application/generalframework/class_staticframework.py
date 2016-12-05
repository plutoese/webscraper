# coding = UTF-8

from libs.class_staticsitescraper import StaticSiteScraper, BeautifulSoup
import random
from libs.class_htmlextractor import HtmlTableParser
from libs.class_proxymanager import ProxyManager
from libs.class_mongodb import MongoDB
from libs.class_multithread import MultiThread
import re


class StaticFramework:
    def __init__(self):
        # 初始化
        self._proxy_manager = ProxyManager()

    def run(self, using_proxy=True, parse_fn=None, parse_param=None,transform_fn=None,
            transform_param=None, check_num=None, db_store=None, web_recorder=None, multi_thread=False):
        webs = web_recorder.collection.find().distinct('web')
        if multi_thread:
            while webs:
                multi_webs = webs[0:min(len(webs),multi_thread)]
                print(multi_webs)
                self.multi_thread(webs=multi_webs, using_proxy=using_proxy, parse_fn=parse_fn,
                                  parse_param=parse_param,transform_fn=transform_fn,
                                  transform_param=transform_param, check_num=check_num,db_store=db_store,
                                  web_recorder=web_recorder)
                webs = web_recorder.collection.find().distinct('web')
        else:
            while webs:
                web = webs[0]
                result = []
                one_result = self.grasp_single_web(web=web, using_proxy=using_proxy, parse_fn=parse_fn,
                                                   parse_param=parse_param,transform_fn=transform_fn,
                                                   transform_param=transform_param, check_num=check_num,db_store=db_store,
                                                   web_recorder=web_recorder)
                if one_result:
                    result.extend(one_result)
                webs = web_recorder.collection.find().distinct('web')
                print(len(result))
            return result

    def grasp_single_web(self, web=None, using_proxy=True, parse_fn=None, parse_param=None,
                         transform_fn=None, transform_param=None, check_num=None, db_store=None,
                         web_recorder=None):
        try:
            # 创建StaticSiteScraper对象
            if using_proxy:
                site_scraper = StaticSiteScraper(web,proxy=random.choice(self._proxy_manager.best_speed_proxies))
            else:
                site_scraper = StaticSiteScraper(web)
            # 抓取当前网页
            html_content = site_scraper.get_current_page_content()

            if parse_fn is not None:
                result = parse_fn(html_content,**parse_param)()
            else:
                result = html_content

            if transform_fn is not None:
                result = transform_fn(result,**transform_param)

            if check_num is not None:
                if len(result) != check_num:
                    return False

            if db_store is not None:
                for item in result:
                    print(item)
                    found = db_store.collection.find_one(item)
                    if found is None:
                        db_store.collection.insert_one(item)

            if web_recorder is not None:
                web_recorder.collection.delete_one({'web':web})

            return result
        except Exception as e:
            print('Parser Error: ',e)
            return False

    def multi_thread(self, webs=None, using_proxy=True, parse_fn=None, parse_param=None,
                         transform_fn=None, transform_param=None, check_num=None, db_store=None,
                         web_recorder=None):
        """ 多线程验载入医院信息
        :return: 无返回值
        """
        threads = []
        for web in webs:
            t = MultiThread(self.grasp_single_web,args=(web,using_proxy, parse_fn, parse_param, transform_fn,
                                                          transform_param, check_num, db_store, web_recorder),name=web)
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == '__main__':
    frame = StaticFramework()

    db = MongoDB()
    db.connect('cache','airqualityinfo')
    web_fmt = 'http://datacenter.mep.gov.cn/report/air_daily/air_dairy.jsp?city=&startdate=2014-01-01&enddate=2016-12-02&page={}'
    #for num in range(1,11):
    #    db.collection.insert_one({'web':web_fmt.format(str(num))})

    #print(frame.run(using_proxy=False,parse_fn=HtmlTableParser, parse_param={'css':'#report1'},
    #                check_num=35,web_recorder=db,multi_thread=2))
