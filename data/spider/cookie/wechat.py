# -*- coding: utf-8 -*-

import sys,os
import json

reload(sys)
sys.setdefaultencoding("utf-8")

import requests
from pyquery import PyQuery as pq

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))
import util

import time, random

import my_request
import requests

def get(name):
    # proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
    # s = my_request.get_single_session(proxy, new=True, agent=False)

    s = requests.session()

    url = 'http://weixin.sogou.com/weixin?type=1&query='+name
    s.headers['Refere'] = 'http://weixin.sogou.com/'
    r = s.get(url)
    r.encoding = r.apparent_encoding
    content = r.text

    print s.cookies.get_dict()
    # print content
    print s.headers
    print r.headers




if __name__ == '__main__':
    name = '篮圈'
    full_name = '厦门壹战信息科技有限公司'
    get(name)