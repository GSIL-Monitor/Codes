# -*- coding: utf-8 -*-
import datetime
import requests
import re
import sys
import os
import json
import random
import time
from pyquery import PyQuery as pq
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent import monkey
monkey.patch_all()


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import util, db, traceback_decorator, loghelper, traceback_decorator

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

import android

# logger
loghelper.init_logger("hicloud_detail cralwer", stream=True)
logger = loghelper.get_logger("hicloud_detail cralwer")

Rule = {'type': 'http', 'anonymity': 'high'}
LinkPattern = '/app/C\d+'
Headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', }

APPMARKET = 16090
Hrefs = []


def get_proxy():
    while True:
        try:
            item = proxy_pool.get_single_proxy(Rule)
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            logger.info('%s:%s' % (ip, port))
            url = "http://app.hicloud.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hicloud') >= 0:
                logger.info('ip:%s for hicloud' % ip_port)
                return proxies
        except Exception, e:
            logger.info('Proxy Exception:%s' % e)

def change_href_status(href):

    mongo = db.connect_mongo()
    collection = mongo.market.links
    try:
        if href:
            collection.update({'href':href},{'$set':{'hicloudprocessed':True}})
        else:
            collection.update({'is_app':True},{'$set':{'hicloudprocessed':None}},multi=True)
    except Exception,e:
        logger.info('mongo error:%s'%e)
    mongo.close()

def change_android_status(apkname, found=True):
    mongo = db.connect_mongo()
    collection_android = mongo.market.android
    try:
            collection_android.update_one({"apkname": apkname},
                                      {"$set": {"hicloudprocessed": True, "hicloudfound": found}})
    except Exception as e:
        logger.info('mongo error:%s' % e)
    mongo.close()

def take_items():
    mongo = db.connect_mongo()
    collection = mongo.market.links
    items = []
    try:
        items = list(collection.find({'is_app': True, 'hicloudprocessed':None},{'href':1},limit=1000))
    except Exception as e:
        logger.info('mongo error:%s' % e)
    mongo.close()
    return items

def to_crawler(href):
    url = 'http://app.hicloud.com' + href
    apkname = url.split('app/')[-1]
    logger.info('start to cralw url:%s'%url)
    i = 0
    j = 0
    while True:
        global Proxies
        if i >= 3:
            Proxies = get_proxy()
            i = 0
        try:
            time.sleep(2)
            r = requests.get(url, headers=Headers, proxies=Proxies, timeout=10)
            change_href_status(href)
            if r.text.find('app-info flt') >= 0:
                return r.content.decode('utf-8'), url
            else:
                logger.info("App: %s is not found", apkname)
                change_android_status(apkname,found=False)
                return None, None

        except Exception, e:
            logger.info('requests error:%s' % e)
            i += 1
            if j >= 6:
                return None, None

def to_parser(page, url):
    try:
        d = pq(html.fromstring(page.decode('utf-8')))

        uls = d('div.app-info> ul.app-info-ul')

        name = d(uls)('span.title').text().strip()
        logger.info('start to parser name:%s | url:%s' % (name, url))

        apkurl = url.split('app/')[-1]
        key = apkurl.split('C')[-1]
        key_int = int(key)
        icon = d(uls)('li.img> img.app-ico').attr('src')

        downloadstr = d(uls)('span.title').next().text().split('：')[-1]
        download = None
        try:
            download = int(downloadstr)
        except:
            if downloadstr.find('万次') >= 0:
                download = int(float(downloadstr.replace('万次', '')) * 10000)
            elif downloadstr.find('亿次') >= 0:
                download = int(float(downloadstr.replace('亿次', '')) * 10000 * 10000)
            else:
                logger.info("********download :%s cannot get", downloadstr)

        sizestr = d(uls).eq(1)('li').eq(0)('span').text().strip()
        size = None
        if sizestr.find('KB') >= 0:
            size = int(float(sizestr.replace("KB","").strip())* 1024)
        elif sizestr.find("MB") >= 0:
            size = int(float(sizestr.replace("MB", "").strip()) * 1024 * 1024)

        updatedatestr = d(uls).eq(1)('li').eq(1)('span').text().strip()
        updatedate = datetime.datetime.strptime(updatedatestr, '%Y-%m-%d')
        author = d(uls).eq(1)('li').eq(2)('span').attr('title')
        version = d(uls).eq(1)('li').eq(3)('span').text().strip()
        if version.startswith("V"):
            version = version.replace("V", "")
        elif version.startswith("v"):
            version = version.replace("v", "")

        screenshots = []
        imgs = d('ul.imgul> li')
        for img in imgs:
            imgurl = d(img)('a').attr('href')
            screenshots.append(imgurl)

        desc = d('div.content').text().replace('\r','').strip()
        re1 = re.search(r'(hide.*none)', desc, re.S)
        if re1:
            desc = desc.replace(re1.group(1),'')

        commentbyeditor = d('div#comment_list').text().replace('\r','').strip()
        re2 = re.search(r'(var.*/;)', commentbyeditor, re.S)
        if re2:
            commentbyeditor = commentbyeditor.replace(re2.group(1), '')

        apknamestr = d('div.app-function> a').attr('onclick')
        re3 = re.search(r'apk/.*?/.*?/(.*)\.\d+\.apk', apknamestr)
        if not re3:
            return
        apkname = re3.group(1)
        if apkname.find('.huawei') >= 0:
            apkname = apkname.replace('.huawei','')
        logger.info('------------%s------------'%apkname)

        item = {
            "link": url,
            "apkname": apkname,
            "appmarket": APPMARKET,
            "name": name,
            "brief": None,
            "website": None,
            "description": desc,
            "commentbyeditor": commentbyeditor,
            "updateDate": updatedate,
            "language": None,
            "tags": None,
            "version": version,
            "updates": None,
            "size": size,
            "compatibility": None,
            "icon": icon,
            "author": author,
            "screenshots": screenshots,
            "type": None,
            "key": key,
            "key_int": key_int,
            "download": download,
        }
        # logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder, indent=2))
        mongo = db.connect_mongo()
        collection = mongo.market.android_market
        collection_android = mongo.market.android
        android.save(collection, APPMARKET, item)
        android.merge(item)
        change_android_status(apkname, found=True)
        mongo.close()
        logger.info('parser done')
    except Exception, e:
        logger.info('parser error:%s' % e)
        raise e

def run():
    while True:

        if len(Hrefs) == 0:
            return

        href = Hrefs.pop()

        page, url = to_crawler(href)

        if page is None:continue

        to_parser(page, url)


@traceback_decorator.try_except
def start_run():
    while True:
        logger.info('hicloud start ... ')
        global Proxies
        Proxies = get_proxy()
        items = take_items()

        if len(items) == 0:
            # change_href_status(href=None)
            logger.info('sleep a day')
            time.sleep(60 * 60 * 24)

        for item in items:
            if not re.search(LinkPattern, item.get('href')):
                continue
            Hrefs.append(item.get('href'))

        theads = [gevent.spawn(run) for i in xrange(10)]
        gevent.joinall(theads)

        logger.info('hicloud end.')



if __name__ == '__main__':
    start_run()
