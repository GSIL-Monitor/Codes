# -*- coding: utf-8 -*-
import os, sys,datetime
import random, math
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util

#logger
loghelper.init_logger("crawler_newrank", stream=True)
logger = loghelper.get_logger("crawler_newrank")


class NewRankCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self,url,content):

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("微信公众号详情") >= 0 or title.find("新榜")>=0:
            return True
        if content.find("404") >= 0:
            return True
        return False



def gen_nonce():
    a = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    b = 0
    c = ""
    while b< 500:
        c = ""
        d = 0
        while d < 9:
            e = math.floor(16 * random.random())
            # print e
            c = c + a[int(e)]
            d += 1
        b += 1
    # print c
    return c

class nrmd5:
    def __init__(self):
        self.process = None
        self.answer = None

    def run(self, para, timeout):
        def target():
            # self.cmd = '/Users/mac/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs screenshot_phjs.js %s %s %s' % (url, websiteId, dest)
            self.cmd = '/opt/phantomjs/bin/phantomjs newrank_md5_2.js "%s"' % (para)
            logger.info(self.cmd)
            logger.info('Screenshot started')
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = self.process.communicate()
            logger.info(stdout)
            if stdout.find("xyz=")>=0 and self.answer is None:
                self.answer = stdout
            logger.info('Screenshot finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            logger.info('Terminating process')
            self.process.terminate()
            thread.join()
        logger.info("return code %s", self.process.returncode)
        if self.answer is not None:
            return self.answer.split("=")[-1].replace("\n","")
        else:
            return None

def gen_xyz(uuid, nonce):
    md = nrmd5()
    para = "/xdnphb/detail/getAccountArticle?AppKey=joker&flag=true&uuid=%s&nonce=%s" % (uuid, nonce)
    timeout = 10
    xyz = None
    while True:
        xyz = md.run(para, timeout)
        if xyz is not None: break
    logger.info('Got xyz: %s', xyz)
    return xyz



def process_uuid(acountName, content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    if title.find(acountName) >= 0:
        href = d('div.more> a').attr("href").strip()
        uuid = href.split("uuid")[-1].replace("=","")
        desc = d('p.info-detail-head-weixin-fun-introduce').attr("title").strip()
        company = d('p.info-detail-head-weixin-approve').text()
        if company is not None: company = company.replace("微信认证：","").strip()
        name = d('div.info-detail-head-weixin-name> span').text()

        logger.info("name: %s, uuid: %s, company: %s, desc: %s", name, uuid, company, desc)
        item = {"name": name, "uuid": uuid, "company": company, "description": desc}

    else:
        item = {}
    return item


def get_uuid(acountName,crawler):
    link = "https://www.newrank.cn/public/info/detail.html?account=%s" % acountName
    headers = {"Cookie": "token=38015FF097133FCD6C2E8BD112BD1826"}
    uuid = None
    while True:
        result = crawler.crawl(link, agent=True, headers=headers)
        if result['get'] == 'success':
            # logger.info(result["redirect_url"])
            try:
                uuid = process_uuid(acountName, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
    return uuid

def save(aName, item, nonce, xyz):
    mongo = db.connect_mongo()
    collection = mongo.raw.new_rank
    acount = collection.find_one({"wechatId": aName})
    if acount is not None:
        logger.info("account is existed")
    else:
        item = {"wechatId": aName,"uuid": item["uuid"],"nonce": nonce,"xyz":xyz,"name":item["name"],
                "company": item["company"], "description": item["description"], "checked":None}
        collection.insert(item)

def get_alink(acountNames):
    crawler = NewRankCrawler()

    for aName in acountNames:
        item = get_uuid(aName, crawler)
        if len(item) == 0:
            logger.info("Uuid for %s is missing",aName); continue
        nonce = gen_nonce()
        logger.info("uuid: %s, nonce: %s", item["uuid"], nonce)
        xyz = gen_xyz(item["uuid"], nonce)
        if xyz is not None:
            save(aName, item, nonce, xyz)
            link = "https://www.newrank.cn/xdnphb/detail/getAccountArticle?flag=true&uuid=%s&nonce=%s&xyz=%s" % (item["uuid"],nonce,xyz)
            logger.info("link: %s", link)

def gen_xyz_hot(date, rank_name, rank_name_group, nonce):
    md = nrmd5()
    para = '/xdnphb/list/day/article?AppKey=joker&end=%s&rank_name=%s&rank_name_group=%s&start=%s&nonce=%s' \
           % (date, rank_name, rank_name_group, date, nonce)
    timeout = 1
    xyz = None
    while True:
        xyz = md.run(para, timeout)
        if xyz is not None: break
    logger.info('Got xyz: %s', xyz)
    return xyz

def gen_xyz_re():
    nonce = gen_nonce()
    mongo = db.connect_mongo()
    collection = mongo.raw.new_rank
    acounts = collection.find({})
    for item in acounts:
        xyz = gen_xyz(item["uuid"], nonce)
        collection.update_one({"_id":item["_id"]},{"$set":{"nonce": nonce,"xyz":xyz}})
        break
    mongo.close()


if __name__ == "__main__":
    # gen_xyz_re()
    get_alink(["Qingliuclub"])
    # gen_xyz_hot()
