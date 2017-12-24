# coding = UTF-8

import requests
import urllib
import json
import re

url_fmt = 'https://data-gkcx.eol.cn/soudaxue/queryProvinceScore.html?messtype=jsonp&callback=jQuery18302686541919312133_1513666161984&provinceforschool=&schooltype=' \
          '&page=1&size=50&keyWord=&schoolproperty=&schoolflag=&province={}&fstype={}&zhaoshengpici=&fsyear=&_=1513666162089'

url = 'https://data-gkcx.eol.cn/soudaxue/queryProvinceScore.html?messtype=jsonp&callback=jQuery18302686541919312133_1513666161984&provinceforschool=&schooltype=' \
      '&page=1&size=10&keyWord=&schoolproperty=&schoolflag=&province=%E5%8C%97%E4%BA%AC&fstype=%E7%90%86%E7%A7%91&zhaoshengpici=&fsyear=&_=1513666162089'

province = urllib.parse.quote('上海')
fstype = urllib.parse.quote('理科')

r = requests.get(url_fmt.format(province,fstype))
content = re.sub('\s+','',re.split('\)',re.split('\(',r.text)[1])[0])
print(json.loads(content))
print(len(json.loads(content)['school']))
for school in json.loads(content)['school']:
    print(school)