# -*- coding: utf-8 -*-
import json
import os, sys, datetime
import random

from lxml import html
from pyquery import PyQuery as pq
import requests
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy,ProxyType
import time


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db # ,util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

# import appmini selenium webdriver 与 logger_help 冲突

source = 16080
Rule = {'type':'HTTPS', 'anonymous':'high'}
Rule2 = {'type':'https', 'anonymity':'high'}


def __clear_brs():

    for line in os.popen('ps -ef |grep firefox').readlines():
        vars = line.split()
        proc = ''.join(vars[7:])  # get proc description
        if line.find('/root/firefox') == -1: continue
        pid = vars[1]  # get pid
        ppd = vars[2]
        out = os.popen('kill ' + pid)
        out2 = os.popen('kill ' + ppd)
    print('clear firefox done')

def get_proxy():
    global Proxiesr
    if len(Proxiesr) == 0:
        Proxiesr = proxy_pool.get_single_proxy_x(Rule,1000)
    while True:
        try:
            item = Proxiesr[random.randint(0, len(Proxiesr) - 1)]
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            print('%s:%s' % (ip, port))
            url = "https://www.baidu.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hao123') >= 0:
                print('ip:%s for qimai' % ip_port)
                return ip, port
        except Exception,e:
            print('Proxy Exception:%s' % e)

def get_proxy2():
    while True:
        try:
            item = proxy_pool.get_single_proxy(Rule2)
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            print('%s:%s' % (ip, port))
            url = "https://www.baidu.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hao123') >= 0:
                print('ip:%s for qimai' % ip_port)
                return ip, port
        except Exception, e:
            print('Proxy Exception:%s' % e)

def delete_tmpfile():
    command = 'rm -f /tmp/tmpaddon*'
    os.system(command)
    print('clean tmp_file done')

def get_webdriver(ip,port,is_proxies=False):
    while True:
        delete_tmpfile()
        try:
            options = webdriver.FirefoxOptions()
            options.binary_location = '/root/firefox/firefox'
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument(
                'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36')

            profile = webdriver.FirefoxProfile()
            # profile.set_preference('browser.download.dir','/tmp/profileqimai.default')
            profile.set_preference('network.proxy.type', 1)
            # # # profile.set_preference('network.proxy.http', '120.52.73.1')
            # # # profile.set_preference('network.proxy.http_port', 96)  # int
            profile.set_preference('network.proxy.ssl', ip)
            profile.set_preference('network.proxy.ssl_port', int(port))
            profile.update_preferences()



            # method 2 not func
            # proxy = Proxy({
            #     'proxyType':ProxyType.MANUAL,
            #     # 'httpProxy':proxies,
            #     'sslProxy':proxies,
            #     'noProxy': ''
            # })
            # driver = webdriver.Firefox(firefox_options=options,executable_path='./geckodriver')#,proxy=proxy)
            if is_proxies:
                driver = webdriver.Firefox(firefox_profile=profile,firefox_options=options,executable_path='./geckodriver')
            else:
                driver = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver')  # ,proxy=proxy)

            driver.implicitly_wait(30)
            # 设置超时
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            return driver
        except Exception as e:
            print('driver error:%s'%e)
            driver.quit()
            time.sleep(5)

def get_page_source(url,ip,port):
    i = 1
    while True:
        delete_tmpfile()
        if i >= 3:
            ip,port = get_proxy2()
            i= 0
        bro = get_webdriver(ip,port,is_proxies=True)

        try:
            bro.get(url)
            time.sleep(10)
            page = bro.page_source
            if page is None:
                bro.quit()
                # __clear_brs()
                continue
            bro.quit()
            # __clear_brs()
            return page,ip,port
        except Exception as e:
            bro.quit()
            # __clear_brs()
            print(e)
            i += 1
            time.sleep(5)

def has_content(page_source):
    if page_source.find('class="header"') >=0:
        return True

def parse(page_spurce,id,url):
    try:
        d = pq(html.fromstring(page_spurce.decode('utf-8','ignore')))
    except UnicodeEncodeError:
        d = pq(html.fromstring(page_spurce))
    appname = d('div.header> div.info-wrap> p.title').text().strip()
    if appname == '':
        return
    tag = d('div.header> div.info-wrap> div.content-wrap> div.item').eq(0).find('p').eq(1).text().strip()
    fullname = d('div.header> div.info-wrap> div.content-wrap> div.item').eq(1).find('p').eq(1).text().strip()
    iconlink = d('img.app-icon').attr('src')
    codelink = d('img.code').attr('src')
    if codelink.find('data:image/png') >=0:
        codelink = ''
    rank = d('div.header> div.num-wrap> div.item').eq(0).find('p').eq(0).text().strip()
    if rank == '-':
        rank = ''
    index = d('div.header> div.num-wrap> div.item').eq(1).find('p').eq(0).text().strip()
    if index == '-':
        index = ''
    official_accounts = []
    app_list = d('ul.app-list> li')
    for app in app_list:
        icon = d(app)('a.icon').attr('href')
        if icon is not None:
            icon = 'https://www.qimai.cn' + icon
        name = d(app)('div.app-wrap> a.title').text().strip()
        official_accounts.append({'icon':icon,'name':name})

    screenshots = []
    imgs = d('div.screenshot-box> img')
    for img in imgs:
        img = d(img).attr('src')
        screenshots.append(img)

    item = {
        'source':source,
        'appid':id,
        'link':url,
        'name':appname,
        'tag':tag,
        'author':fullname,
        'icon':iconlink,
        'code':codelink,
        'rank':rank,
        'index':index,
        'official_accounts':official_accounts,
        'createtime':datetime.datetime.now(),
        'modifytime':datetime.datetime.now(),
        "screenshots":screenshots
    }
    # print(json.dumps(item,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    mongo = db.connect_mongo()
    collection = mongo.market.appmini_market
    appmini_save(collection,source,item)
    appmini_merge(item)
    mongo.close()

def save(collection_content):
    mongo = db.connect_mongo()
    collection = mongo.market.appmini_market
    try:
        item = collection.find_one({'name':collection_content['name'],'appid':collection_content['appid']})
        createtime = item['createtime']
        if item is not None:
            collection.delete_one({'name':collection_content['name'],'appid':collection_content['appid']})
            print('old ---> news')
            collection_content['createtime'] = createtime
        collection.insert_one(collection_content)
        print('save item done')
    except Exception as e:
        print('mongo error:%s'%e)
    mongo.close()

def get_new_item(item, record):
    item = dict(item)
    record = dict(record)
    record.pop('createtime')
    if record.has_key('modifytime'):
        record.pop('modifytime')
    if record.has_key('updatedate'):
        record.pop('updatedate')
    item.pop('createtime')
    if item.has_key('modifytime'):
        item.pop('modifytime')
    if item == record:
        return item, 'same'
    # logger.info(json.dumps(item,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    # logger.info(json.dumps(record,ensure_ascii=False,indent=2,cls=util.CJsonEncoder))
    for key in record.keys():
        if item.get(key) is None:
            item[key] = record[key]
    return item, 'diff'

def save_pagesource(id,url,page_source):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    collection_content = {
        'key':id,
        'link':url,
        'source':source,
        'content':page_source,
        'createtime': datetime.datetime.now()
    }
    try:
        item = collection.find_one({'source':source,'key':id,'link':url})
        if item is None:
            collection.insert_one(collection_content)
            print('save page_source done')
    except Exception as e:
        print('mongo error:%s'%e)
    mongo.close()

def appmini_save(collection_market, source, item):
    # projection histories false 不显示历史字段
    record = collection_market.find_one({'name': item['name'], 'source': source}, projection={'histories': False})
    if record:
        _id = record.pop('_id')
        new_item, status = get_new_item(item, record)
        if status == 'diff':
            new_item['createtime'] = item['createtime']
            new_item['modifytime'] = datetime.datetime.now()
            if new_item.get('updatedate') is None:
                new_item['updatedate'] = datetime.datetime.now()
            collection_market.update_one({"_id": _id}, {'$set': new_item, '$addToSet': {"histories": record}})
            print('new version ---> addtoset down')
        else:
            new_item['createtime'] = record['createtime']
            new_item['modifytime'] = datetime.datetime.now()
            collection_market.update_one({"_id": _id}, {'$set': new_item})
            print('same version ---> update done')
    else:
        item["createtime"] = datetime.datetime.now()
        item["modifytime"] = datetime.datetime.now()
        if item.get('updatedate') is None:
            item["updatedate"] = datetime.datetime.now()
        try:
            collection_market.insert(item)
            print('insert a new item down')
        except Exception, e:
            print(e)

def appmini_merge(item):
    item = dict(item)
    for key in item.keys():
        if key in ['_id', 'rank', 'index', 'source', 'appid','updatedate']:
            item.pop(key)
    if item.has_key("screenshots") and len(item["screenshots"]) > 0:
        sshots = item["screenshots"]
        if sshots[0].find("bdimg") >= 0:
            # baidu image not work
            item["screenshots"] = []
    mongo = db.connect_mongo()
    collection = mongo.market.appmini
    miniapp = collection.find_one({'name':item['name']},projection={'histories':False})
    if miniapp is None:
        item["createtime"] = datetime.datetime.now()
        item["modifytime"] = item["createtime"]
        try:
            collection.insert(item)
            print('insert a new miniapp down')
        except Exception,e:
            print(e)
    else:
        _id = miniapp.pop('_id')
        new_app, status = get_new_item(item,miniapp)
        if status == 'diff':
            new_app['createtime'] = item['createtime']
            new_app['modifytime'] = datetime.datetime.now()
            collection.update_one({"_id": _id}, {'$set': new_app, '$addToSet': {"histories": miniapp}})
            print('new version miniapp ---> addtoset down ')
        else:
            print('no change')
            pass
    mongo.close()

def take_appid():
    mongo = db.connect_mongo()
    collection = mongo.market.appmini_market
    try:
        item = list(collection.find({'source':source}).sort('appid'))[-1]
        appid = item['appid']
        mongo.close()
        return appid
    except Exception as e:
        print('mongo error:%s' % e)
    mongo.close()

def run():
    while True:
        # global Proxiesr
        # Proxiesr = proxy_pool.get_single_proxy_x(Rule, 1000)

        print(datetime.datetime.now())

        ip,port = get_proxy2()

        appid = take_appid()
        print('appid:%d go ahead'%appid)
        for id in range(appid+1,appid+101):
            while True:
                url = 'https://www.qimai.cn/weixin/miniapp/type/baseinfo/appid/%d'%id
                print('start to crawl url:%s'%url)
                page_source,ip,port = get_page_source(url,ip,port)
                # page_source, ip, port = get_page_source(url, None, None)
                if not has_content(page_source):
                    break
                save_pagesource(id,url,page_source)
                parse(page_source,id,url)
                break
        print('sleep 24 hours')
        time.sleep(60*60*24)

if __name__ == '__main__':
    run()
