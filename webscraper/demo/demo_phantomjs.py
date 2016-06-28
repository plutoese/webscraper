# coding=UTF-8

from selenium import webdriver
from libs.class_proxymanager import ProxyManager

pmanager = ProxyManager()
proxy = pmanager.random_proxy
print(''.join(['--proxy=',proxy]))

service_args = [''.join(['--proxy=',proxy]),'--proxy-type=http']
driver = webdriver.PhantomJS(executable_path="D:\\tools\\phantomjs\\bin\\phantomjs.exe",
                             service_args=service_args)

driver.get('http://impactfactor.cn/')
print(driver.title)

'''
driver.set_window_size(1120, 550)
driver.get("https://duckduckgo.com/")
driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
driver.find_element_by_id("search_button_homepage").click()
print(driver.current_url)
driver.quit()
'''
