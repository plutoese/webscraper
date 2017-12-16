# coding = UTF-8

import re
import json
import requests
from urllib.parse import quote, unquote

print(unquote('wds=%5B%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%222015%22%7D%5D&dfwds=%5B%5D&'))
print(quote('[{"wdcode":"sj","valuecode":"2015"}]'))

parameters = {'m': 'QueryData', 'dbcode': 'fsnd', 'rowcode': 'reg', 'colcode':'zb',
              'wds':[{"wdcode":"sj","valuecode":"1980"}], 'dfwds':[{"wdcode":"zb","valuecode":"A0203"}],
              'k1':'14930450350'}
url_template = 'http://data.stats.gov.cn/easyquery.htm?m={}&dbcode={}&rowcode={}&colcode={}&wds={}&dfwds={}&k1={}'
print(parameters.get('wds').__repr__())
print(quote(re.sub('\s+','',parameters.get('wds').__repr__())))
wds = re.sub('\s+', '', parameters.get('wds').__repr__())
wds = re.sub('\'','\"',wds)
dfwds = re.sub('\s+', '', parameters.get('dfwds').__repr__())
dfwds = re.sub('\'','\"',dfwds)

rurl = url_template.format(parameters.get('m'), parameters.get('dbcode'), parameters.get('rowcode'), parameters.get('colcode'),
                    quote(wds), quote(dfwds), parameters.get('k1'))
print(rurl)













