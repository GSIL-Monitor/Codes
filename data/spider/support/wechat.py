# -*- coding: utf-8 -*-

import sys,os
import json

reload(sys)
sys.setdefaultencoding("utf-8")

import requests
from pyquery import PyQuery as pq

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import util

import time, random


def find_wechat1(name, full_name):
    i = 0
    while True:
        url = 'http://weixin.sogou.com/weixin?type=1&query='+name
        i += 1
        print i
    #
    #
    # r = requests.get(url)
    # r.encoding = r.apparent_encoding
    # content = r.text
    # headers = r.headers
    #
    # print headers
    #
    # cookies =  headers['set-cookie']
    # cookie_arr = cookies.split(';')
    #
    # c1 = ''
    # c2 = ''
    # c3 = ''
    #
    # for cookie in cookie_arr:
    #     print cookie
    # suv = c1+c2+c3
    #
    # print suv

        # r = requests.get(url)
        # r.encoding = r.apparent_encoding
        # content = r.text
        # headers = r.headers
        #
        # print headers
        #
        # cookies =  headers['set-cookie']

        session = requests.session()

        session.headers['cookie'] = 'ABTEST=0|1448523975|v1; expires=Sat, 26-Dec-15 07:46:15 GMT; path=/, SNUID=A8F66AFF989DB2F4529275AD983FFDFC; expires=Sun, 06-Dec-15 07:46:15 GMT; domain=sogou.com; path=/, IPLOC=CN88; expires=Fri, 25-Nov-16 07:46:15 GMT; domain=.sogou.com; path=/,SUID=306EF2676B20900A000000005656B8C7; expires=Wed, 21-Nov-35 07:46:15 GMT; domain=weixin.sogou.com; path=/, black_passportid=1; domain=.sogou.com; path=/; expires=Thu, 01-Dec-1994 16:00:00 GMT'
        r = session.get(url)
        r.encoding = r.apparent_encoding
        content = r.text
        headers = r.headers

        # print content
        print headers

        # sleep_time = random.randint(10, 20)
        # time.sleep(sleep_time)

        if '请输入验证码' in content:
            break

        # print content
        # print headers






def get(url):
    r = requests.get(url, timeout = 10)
    r.encoding = r.apparent_encoding
    return r.text

if __name__ == '__main__':
    name = '篮圈'
    full_name = '厦门壹战信息科技有限公司'
    print find_wechat1(name, full_name)
