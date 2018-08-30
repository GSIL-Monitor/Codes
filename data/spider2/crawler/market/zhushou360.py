# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import pymongo
from distutils.version import LooseVersion
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, db, util, hz, name_helper
import android

#logger
loghelper.init_logger("zhushou360", stream=True)
logger = loghelper.get_logger("zhushou360")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android_market


APPMARKET = 16010
EVENT = Event()
START = 0
LATEST = 0

class Zhushou360Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url, content):
        if content.find('<meta http-equiv="refresh" content="0.1;url=http://zhushou.360.cn">') >= 0:
            return True

        if content.find('获取应用内容失败，请尝试ctrl+f5刷新') >= 0:
            return True

        if content.find('360安全中心') >= 0:
            return True

        return False


def process(url, key, content):
    global LATEST
    if content.find('360安全中心') == -1:
        return

    #logger.info(content)

    r = "var detail = \(function \(\) \{\s*?return\s*?(.*?);\s*?\}\)"
    result = util.re_get_result(r,content)
    (b,) = result
    base = json.loads(b.replace("'",'"'),strict=False)
    name = base["sname"]
    type = base["type"]
    package = base["pname"].strip()
    #logger.info("%s, %s, %s" % (type, name, package))

    d = pq(html.fromstring(content.decode("utf-8")))
    desc = ""
    try:
        # desc = d('div.breif').contents()[0].strip()
        desc = d('div.breif').text().strip()
        ts = desc.split("【基本信息】")
        desc = ts[0].strip()
    except:
        pass
    if desc == "":
        try:
            desc = d('div#html-brief').text().strip()
        except:
            pass

    #logger.info(desc)

    author = d('div.base-info> table> tbody> tr> td').eq(0).contents()[1].strip()
    chinese, is_company = name_helper.name_check(author)
    if chinese and is_company:
        author = name_helper.company_name_normalize(author)
    author = None

    #logger.info(author)
    modify_date_str = d('div.base-info> table> tbody> tr> td').eq(1).contents()[1].strip()
    #logger.info(modify_date_str)
    modify_date =  datetime.datetime.strptime(modify_date_str,"%Y-%m-%d")
    #logger.info(modify_date)
    versionname = None
    try:
        versionname = d('div.base-info> table> tbody> tr> td').eq(2).contents()[1].strip()
        if versionname.startswith("V"):
            versionname = versionname.replace("V", "")
    except:
        pass
    #logger.info(versionname)
    compatibility = d('div.base-info> table> tbody> tr> td').eq(3).contents()[1].strip()
    language = d('div.base-info> table> tbody> tr> td').eq(4).contents()[1].strip()

    if language == "其他":
        if hz.is_chinese_string(desc):
            language = "中文"
    #logger.info(language)

    icon = d('div#app-info-panel> div> dl> dt >img').attr("src").strip()
    #logger.info(icon)

    screenshots = []
    try:
        screenshots = d('div#scrollbar').attr("data-snaps").split(",")
    except:
        pass

    commentbyeditor = None
    r = "<p><strong>【小编点评】</strong>(.*?)</p>"
    result = util.re_get_result(r,content)
    if result:
        (commentbyeditor,) = result

    updates = None
    r = "<br/><b>【更新内容】</b><br/>(.*?)</div>"
    result = util.re_get_result(r,content)
    if result:
        (updates,) = result
        updates = updates.replace("<br />","\n").strip()

    tags = d("div.app-tags> a").text().replace(" ",",")

    size = None
    r = "'size':'(.*?)'"
    result = util.re_get_result(r,content)
    if result:
        (size,) = result
        size = int(size)

    downloadstr = d("span.s-3").eq(0).text().replace("下载：","").replace("次","").replace("+","").strip()
    download = None
    try:
        if downloadstr.endswith("千"):
            download = float(downloadstr.replace("千","")) * 1000
        elif downloadstr.endswith("万"):
            download = float(downloadstr.replace("万","")) * 10000
        elif downloadstr.endswith("亿"):
            download = float(downloadstr.replace("亿","")) * 10000 * 10000
        else:
            download = int(downloadstr)
        score = float(d("span.s-1").text().replace("分","").strip())*0.5
    except:
        traceback.print_exc()

    item = {
        "link": url,
        "apkname": package,
        "appmarket": APPMARKET,
        "name": name,
        "brief": None,
        "website": None,
        "description": desc,
        "commentbyeditor": commentbyeditor,
        "updateDate": modify_date,
        "language": language,
        "tags": tags,
        "version": versionname,
        "updates": updates,
        "size": size,
        "compatibility": compatibility,
        "icon": icon,
        "author": author,
        "screenshots": screenshots,
        "type": type,
        "key": str(key),
        "key_int": key,
        "download": download,
    }
    logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

    android.save(collection, APPMARKET, item)
    android.merge(item)

    if LATEST < key:
        LATEST = key

def run(crawler):
    global START, LATEST

    while True:
        if START > 3000000 and START > LATEST + 2000:
            return
        key = START
        START += 1
        url = "http://zhushou.360.cn/detail/index/soft_id/%s" % key
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(url, key, result['content'])
                except Exception, e:
                    logger.error(e)
                break

def run_key(crawler, key):

    url = "http://zhushou.360.cn/detail/index/soft_id/%s" % key
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                process(url, int(key), result['content'])
            except Exception, e:
                logger.error(e)
            break

def start_run(concurrent_num, flag):
    global START, LATEST
    while True:
        logger.info("zhushou 360 %s start...", flag)

        LATEST = 1
        if flag == "incr":
            item = collection.find_one({"appmarket":APPMARKET}, sort=[("key_int", pymongo.DESCENDING)], limit=1)
            if item:
                LATEST = item["key_int"] -10
        START = LATEST

        threads = [gevent.spawn(run, Zhushou360Crawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("zhushou 360 %s end.", flag)

        #break

        if flag == "incr":
            gevent.sleep(60*30)         #30 minutes
        else:
            gevent.sleep(86400*0.5)       #1/2 day


if __name__ == "__main__":
    flag = "incr"
    concurrent_num = 10
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        run_key(Zhushou360Crawler(),flag)
    if flag == "all":
        concurrent_num = 50

    start_run(concurrent_num, flag)
