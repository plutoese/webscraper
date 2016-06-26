# coding=UTF-8

import requests
import urllib

# Getting Data-files with requests

response = requests.get("http://www.dgtle.com/portal.php")
print(response.status_code)
print(response.headers)
print(response.encoding)


def download(url):
    print('Downloading:',url)
    try:
        html = urllib.request.urlopen(url).read()
    except urllib.URLError as e:
        print('Download error:',e.reason)
        html = None
    return html


def download_requests(url):
    print('Downloading:',url)
    try:
        html = requests.get(url=url,timeout=30)
    except requests.exceptions.RequestException as e:
        print('Download error:',e)
        html = None
    return html.content

print(download_requests("http://www.cuaa.net/cur/2015/2015gkzydc/07"))