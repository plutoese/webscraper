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


if __name__ == '__main__':
    db = MongoDB()
    db.connect('cache','scraper')
    html = list(db.collection.find())[0]['content']

    htmlparser = HtmlParser(html_content=html)

