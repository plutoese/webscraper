# coding = UTF-8

"""
=========================================
中国知网指定期刊论文抓取
=========================================

:Author: glen
:Date: 2016.10.14
:Tags: mongodb cnki literature
:abstract: 定期抓取中国知网指定期刊论文
"""

import re
import time
import random
from libs.class_proxymanager import ProxyManager
from libs.class_proxymanager import MultiThread
from application.cnki.class_cnki import Cnki

# --------------------
# 0. 参数设置
# --------------------

# 0.1 系统参数
# 代理服务器管理
proxy_manager = ProxyManager()

# 0.2 用户定义参数
# 这部分参数用户可以自定义
# 杂志
JOURNALS = ['经济研究', '中国社会科学', '经济学(季刊)', '金融研究', '人口研究', '世界经济', '管理世界',
            '中国工业经济', '经济地理', '中国农村经济', '经济学家', '数量经济技术经济研究', '财贸经济', '世界经济文汇']
# 杂志对应的ISSN
ISSNS = ['0577-9154', '1002-4921', '2095-1086', '1002-7246', '1000-6087', '1002-9621', '1002-5502',
         '1006-480X', '1000-8462', '1002-8870', '1003-5656', '1000-3894', '1002-8102', '0488-6364']

# 设定年份
START_YEAR = '2015'
END_YEAR = '2015'


# --------------------
# 1. 定义操作函数

# 爬取单个杂志数据程序
def crawler(issn):
    is_proxy_successful = False
    while(not is_proxy_successful):
        proxy = random.choice(proxy_manager.recommended_proxies(10))

        print(issn,'\t',proxy)
        cnki_obj = Cnki(proxy=proxy,type=1)
        if cnki_obj.is_connected():
            is_proxy_successful = True
        else:
            cnki_obj.close()
            time.sleep(10)
    query_str = ''.join(["SN='",issn,"'"])
    cnki_obj.set_query(query_str)
    time.sleep(1)
    cnki_obj.set_period(start_period=START_YEAR,end_period=END_YEAR)
    time.sleep(1)
    cnki_obj.submit()
    cnki_obj.browser.switch(iframe='iframeResult')
    # store number of records
    total_number_str = cnki_obj.browser.browser.find_element_by_css_selector('.pageBar_min > div:nth-child(1)').text
    total_number = re.sub(',','',re.findall('\d+,?\d+',re.sub('\s+','',total_number_str))[0])
    print(total_number)

    cnki_obj.browser.interact_one_time(location='#id_grid_display_num > a:nth-child(3)',click=True)
    time.sleep(1)
    cnki_obj.select_all_literature()

    time.sleep(2)
    cnki_obj.child_operation()
    cnki_obj.get_more(limit=100)
    cnki_obj.export_to_json(file=''.join(['D:/data/result/literature_',issn,'_',START_YEAR,'.pkl']))
    cnki_obj.close()

# 多线程爬取程序
def multi_crawler():
    threads = []
    for issn in sorted(ISSNS)[0:2]:
        t = MultiThread(crawler,args=(issn,),name=issn)
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

crawler(ISSNS[0])