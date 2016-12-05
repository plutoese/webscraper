# coding=UTF-8

# --------------------------------------------------------------
# class_htmlextractor文件
# @class: HtmlParser类
# @introduction: HtmlParser类用来解析html对象
# @dependency: bs4及re包
# @author: plutoese
# @date: 2016.06.24
# --------------------------------------------------------------

from bs4 import BeautifulSoup
import re
from libs.class_proxymanager import ProxyManager
from libs.class_staticsitescraper import StaticSiteScraper
from libs.class_Excel import Excel


class HtmlParser:
    """HtmlParser类用来解析html对象

    :param str htmlcontent: html的字符串
    :return: 无返回值
    """
    def __init__(self, html_content=None):
        if isinstance(html_content,BeautifulSoup):
            self.bs_obj = html_content
        else:
            self.html_content = html_content
            self.bs_obj = BeautifulSoup(self.html_content, "lxml")


class HtmlTableParser(HtmlParser):
    def __init__(self, html_content=None, css=None):
        super().__init__(html_content=html_content)
        self._css = css

    def __call__(self):
        """ 返回表格的数据

        :param css: table的css选择器
        :return: 表格的列表
        """
        table = []
        if self._css is not None:
            tds = self.bs_obj.select(''.join([self._css,' > tr']))

        for item in tds:
            table.append([re.sub('\s+','',unit.text) for unit in item.select('td')])

        return table

if __name__ == '__main__':
    pmanager = ProxyManager()
    ramdomproxy = pmanager.recommended_proxies(number=1)[0]
    site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/shanghai-201609.html',proxy=ramdomproxy)
    html = site_scraper.get_current_page_content()
    print(html.title)
    print(isinstance(html,BeautifulSoup))

    htmlparser = HtmlParser(html_content=html)
    #print(htmlparser.bs_obj.select('.b > tr'))
    table = htmlparser.table('.b')
    outfile = r'd:\down\quality.xlsx'
    moutexcel = Excel(outfile)
    moutexcel.new().append(table, 'mysheet')
    moutexcel.close()

