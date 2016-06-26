# coding=UTF-8

# --------------------------------------------------------------
# class_htmlparser文件
# @class: HtmlParser类
# @introduction: HtmlParser类用来解析html对象
# @dependency: bs4及re包
# @author: plutoese
# @date: 2016.06.24
# --------------------------------------------------------------

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from libs.class_mongodb import MongoDB
import requests
import re


class HtmlParser:
    """HtmlParser类用来解析html对象

    :param str htmlcontent: html的字符串
    :return: 无返回值
    """
    def __init__(self,html_content=None):
        # 设置网站地址
        self.html_content = html_content
        self.bs_obj = BeautifulSoup(self.html_content, "lxml")

    def table(self,css=None):
        """ 返回表格的数据

        :param css: table的css选择器
        :return: 表格的列表
        """
        table = []
        if css is not None:
            tds = self.bs_obj.select(''.join([css,' > tr']))

        for item in tds:
            table.append([re.sub('\s+','',unit.text) for unit in item.select('td')])

        return table

if __name__ == '__main__':
    db = MongoDB()
    db.connect('cache','scraper')
    html = list(db.collection.find())[2]['content']

    htmlparser = HtmlParser(html_content=html)
    #print(htmlparser.bs_obj.select('.b > tr'))
    print(htmlparser.table('.b'))

