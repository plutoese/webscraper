# coding = UTF-8

from libs.class_dynamicscraper import DynamicScraper
from selenium.webdriver.common.by import By
from libs.class_proxymanager import ProxyManager

dscraper = DynamicScraper(website='http://epub.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ',label='cnki.net')
dscraper.surf(proxies=ProxyManager().best_speed_proxies,proxy_type='http',timeout=5,type=0,ready_check=(By.CSS_SELECTOR,'.botNav'))

