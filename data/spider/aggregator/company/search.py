# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import requests
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")



def baidu_index(name):
    url = 'http://index.baidu.com/?tpl=trend&word='+name
    r = requests.get(url, timeout= 10)
    d = pq(r.text)




def haosou_index(name):
    url = 'http://index.haosou.com/#trend?q='+name
    requests.get(url, timeout= 10)
