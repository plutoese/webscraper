# coding=UTF-8

# --------------------------------------------------------------
# class_hospitalscraper文件
# @class: HospitalScraper类
# @introduction: HospitalScraper类用来抓取医院信息
# @datasource：https://www.hqms.org.cn/usp/roster/index.jsp
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.28
# --------------------------------------------------------------

import time
import random
from bs4 import BeautifulSoup
from libs.class_dynamicscraper import DynamicScraper
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
from selenium.webdriver.common.by import By
from libs.class_multithread import MultiThread
import re


class HospitalScraper:
    """ HospitalScraper类用来抓取医院信息

    :param str website: 网页地址
    :return: 无返回值
    """
    def __init__(self):
        # 初始化
        self.pmanager = ProxyManager()
        self.dscraper = DynamicScraper(website='https://www.hqms.org.cn/usp/roster/index.jsp',
                                       label='hqms.org.cn')

        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','scraper')

        # 地区
        #self.regions = ['河北省', '山西省']

        self.regions = ['北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省',
                        '上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省', '湖北省',
                        '湖南省', '广东省', '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省',
                        '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔族自治区', '新疆生产建设兵团']

    def one_thread(self,region):
        self.dscraper.surf(proxies=self.pmanager.best_speed_proxies,proxy_type='https',timeout=5,type=1,
                      ready_check=(By.CSS_SELECTOR,'.table_result'))
        result = self.dscraper.act_once([('interaction',{'location':'.province_select','select_text':region}),
                                  ('interaction',{'location':'#btn_search','click':True}),
                                  ('timeout',10),
                                  ('get_text',{'location':'.table_result'})])
        record = {'region':region,'content':result,'label':'hospital'}
        print(region)
        self.db.collection.insert_one(record)
        self.dscraper.quit()

    def multi_thread(self):
        """ 多线程验载入医院信息
        :return: 无返回值
        """
        while self.regions:
            region = self.regions[0]
            found = self.db.collection.find_one({'region':region})
            if found is None:
                self.one_thread(region)
            else:
                self.regions.pop(0)

if __name__ == '__main__':
    hscraper = HospitalScraper()
    hscraper.multi_thread()

