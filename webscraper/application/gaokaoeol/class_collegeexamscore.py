# coding=UTF-8

# --------------------------------------------------------------
# class_collegeexamscore文件
# @class: CollegeExamScore类
# @introduction: CollegeExamScore类用来抓取高考分数
# @datasource：http://gkcx.eol.cn/
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.24
# --------------------------------------------------------------

import re
from libs.class_proxymanager import ProxyManager
from libs.class_dynamicscraper import DynamicScraper
from selenium.webdriver.common.by import By
from libs.class_mongodb import MongoDB


class CollegeExamScore:
    """CollegeExamScore类用来抓取高考分数

    :param str website: 网页地址
    :return: 无返回值
    """
    def __init__(self,website=None,numbers=None,label='CollegeEntranceExam'):
        # 设置网站地址
        self.website = website
        self.numbers = numbers

        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','scraper')

        # 设置标示
        self.label = label

        # 设置代理服务器集合
        self.pmanager = ProxyManager()

    def scrape_and_store(self):
        for num in self.numbers:
            found = self.db.collection.find_one({'label':'CollegeEntranceExam','mid':num})
            if found is None:
                web_address = self.website.format(num)
                dscraper = DynamicScraper(website=web_address,label='eol.cn')

                dscraper.surf(proxies=self.pmanager.best_speed_proxies,proxy_type='http',
                              timeout=5,type=0,ready_check=(By.CSS_SELECTOR,'#pageid'))
                content = dscraper.act_once([('get_text',{'location':'#queryschoolad'})])
                record = {'label':self.label,'mid':num,
                          'content':content,'website':'eol.cn'}
                print(record)
                self.db.collection.insert_one(record)

    def scrape_and_store_more(self):
        """ 抓取网页，并储存网页内容到MongoDB

        :return: 无返回值
        """
        # 组成num:webaddress的字典
        webs = dict([(num,self.website.format(num)) for num in self.numbers])
        # 删除那些已经进入数据库的项
        nums = set()
        for num in webs:
            found = self.db.collection.find_one({'label':'CollegeEntranceExam','mid':num})
            if found is not None:
                nums.add(num)
        for n in nums:
            webs.pop(n)

        if len(webs) < 1:
            print('All Done@^@')
            return True

        # while循环用来抓取webs里的网页，并储存结果到数据库
        while webs:
            # 创建动态抓取器
            dscraper = DynamicScraper(website=dict(tuple(webs.items())),label='eol.cn')
            # 执行动态抓取，返回结果到result
            result = dscraper.surf_more(proxies=self.pmanager.best_speed_proxies,proxy_type='http',
                                        timeout=5,type=0,ready_check=(By.CSS_SELECTOR,'#pageid'),
                                        action=[('get_text',{'location':'#queryschoolad'})])
            # 储存结果到MongoDB，如果抓取内容不完备，则返回while循环继续抓取
            for num in result:
                if len(re.split('\n',result[num])) < 2:
                    continue
                record = {'label':self.label,'mid':num,'content':result[num],'website':'eol.cn'}
                print(num,'---',record)
                self.db.collection.insert_one(record)
                webs.pop(num)

if __name__ == '__main__':
    cexam = CollegeExamScore(website='http://gkcx.eol.cn/soudaxue/queryProvinceScore.html?page={}&scoreSign=3',
                             numbers=range(1,8))
    print(cexam.numbers)
    cexam.scrape_and_store_more()

