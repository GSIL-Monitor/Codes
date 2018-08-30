# -*- coding: utf-8 -*-
import json
import os, sys
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy,ProxyType



sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, util, db


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool




headers = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    # "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    # "Accept-Encoding": "gzip, deflate, sdch",
    # "Connection": "keep-alive",
    # "Cache-Control": "max-age=0",
    # "Upgrade-Insecure-Requests": "1",
    # "Referer": "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action",
    }
def __clear_brs():
    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep firefox').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep Xvfb').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    print('clear firefox done')

def get_proxy(http_type='http'):
    proxy = {'type': http_type, 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        print("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            print("proxy_pool.get_single_proxy return None")
        print(proxy_ip['ip:port'])
        return proxy_ip['ip:port']

def get_webdriver(proxies=None):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=" + headers["User-Agent"])
    options.binary_location = '/root/firefox/firefox'

    if proxies is None:
        proxies = get_proxy()
    proxy = Proxy({
        'proxyType':ProxyType.MANUAL,
        'httpProxy':proxies,
        # 'ftpProxy': '120.52.73.1:96',
        # 'sslProxy': '120.52.73.1:96',
        'noProxy': ''
    })

    driver = webdriver.Firefox(firefox_options=options,executable_path='./geckodriver', proxy=proxy)# TODO
    # 在指定时间范围等待：
    driver.implicitly_wait(30)
    # 设置超时
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    return driver, proxies

def get_cookie(url):
    cookies_result = {'status': False, 'cookies': None}
    retry = 0
    while True:
        retry += 1
        if retry > 5:
            return cookies_result, None
        try:
            print('to get cookie...')
            # proxies = '120.52.73.1:96' bad
            # proxy = '122.72.18.34:80' ok
            driver, proxy = get_webdriver()
            driver.get(url)
            # time.sleep(5)
            # print driver.page_source

            raw_cookies = driver.get_cookies()

            driver.quit()
            __clear_brs()
            # print driver.page_source
            cookies = {}
            for c in raw_cookies:
                cookies[c["name"]] = c["value"]
            print(cookies)
            if cookies.has_key('__jsluid') and cookies.has_key('__jsl_clearance'):
                cookies_result['status'] = 'got'
                cookies_result['cookies'] = cookies
                return cookies_result, proxy
        except Exception as e:
            print('driver error :%s',e)
            __clear_brs()

if __name__ == "__main__":
    cr, p = get_cookie("http://www.ebrun.com/capital/ipo/1")
    if cr.has_key('status') and cr['status'] == 'got':
        STR = ''
        for c in cr["cookies"]:
            # print c
            # print cr["cookies"][c]
            STR += c + '=' + cr["cookies"][c]
            STR += "; "
        print p
        print STR
        headers['Cookie'] = STR
        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/59.0'
        import requests
        proxy = {
            # {'122.72.18.34': '80'}
            'http':p
        }

        r = requests.get('http://www.ebrun.com/capital/ipo/1',headers=headers,proxies=proxy,timeout=10)
        print(r.text)