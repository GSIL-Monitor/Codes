# -*- coding: utf-8 -*-
import os, sys,datetime
import pymongo
from pymongo import MongoClient
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper
import util
import url_helper, name_helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler
import android
#logger
loghelper.init_logger("crawler_wandoujia", stream=True)
logger = loghelper.get_logger("crawler_wandoujia")

#mongo
mongo = db.connect_mongo()
collection = mongo.market.android_market
collection_android = mongo.market.android


APKS=[]
APPMARKET=16030

class WandoujiaCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        #exception
        if content.find("com.vivekwarde.onegbrambooster") > 0:
            return True

        if content.find("com.vivekwarde.threegbrambooster") > 0:
            return True

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("豌豆荚") >= 0:
            return True
        #exception
        if title.find("豌豆家") > 0:
            return True

        if title.find("该应用已下架") > 0:
            return True

        return False


def has_content(content,apkname):
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))
    logger.info("herecheck : " + apkname)
    # logger.info(content)
    if content.find("data-pn=\""+apkname) == -1:
        # logger.info("herecheck2 : " + apkname)
        return False
    if content.find("该应用已下架") > 0:
        # logger.info("herecheck1 : " + apkname)
        return False
    if content.find("app-offline-tips") > 0:
        # logger.info("herecheck1 : " + apkname)
        return False
    return True

def process(crawler, url, apkname, content):
    # logger.info(content)
    if has_content(content,apkname):
        logger.info("hereherehere")
        #content = content.decode('utf-8')
        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        #content = unicode(content, encoding="utf-8", errors='replace')
        #d = pq(content)

        name = d('span.title').text()
        # logger.info("name: %s",name)

        icon = d('div.app-icon> img').attr("src")

        brief = d('p.tagline').text()
        # logger.info(brief)

        commentbyeditor= d('div.editorComment> div').text()
        #logger.info(editor_comment)

        screenshots = []
        imgs = d('div.overview> img')
        # logger.info(imgs)
        for img in imgs:
            imgurl = pq(img).attr("src")
            screenshots.append(imgurl)

        desc = d('div.desc-info> div').text()
        # logger.info(desc)
        updates = d('div.change-info> div').text()
        # logger.info(update_desc)
        try:
            size = int(d('meta[itemprop="fileSize"]').attr("content"))
        except:
            size = d('meta[itemprop="fileSize"]').attr("content")
            if size.find("KB") >= 0:
                size = int(float(size.replace("KB","").strip())* 1024)
            elif size.find("MB") >= 0:
                size = int(float(size.replace("MB","").strip())* 1024 * 1024)
            else:
                size = None
        tags = d('dd.tag-box >a').text().replace(" ",",")


        datestr = d('time#baidu_time').text()
        updatedate = datetime.datetime.strptime(datestr, "%Y年%m月%d日")
        #versionname = d(':contains("版本")').next()
        #logger.info(versionname)
        author = d('span.dev-sites').text()
        chinese, is_company = name_helper.name_check(author)
        if chinese and is_company:
            author = name_helper.company_name_normalize(author)
        try:
            website=d('a.dev-sites').attr("href")
            website = url_helper.url_normalize(website)
        except:
            website=None

        compatibility=None
        if content.find("查看权限要求") == -1:
            r1 = "content=\"Android\">(.*?)</dd>.*<dt>来自"
        else:
            r1 = "content=\"Android\">(.*?)<div>.*"
        result1 = util.re_get_result(r1, content)
        if result1:
            (compatibility,)= result1
            compatibility=compatibility.replace("\n","").replace("\r","").replace("\s","").replace(" ","")
        #logger.info(compatibility)

        versionname=None
        r2 = "<dt>版本</dt>.*<dd>(.*?)</dd>.*<dt>要求"
        result2 = util.re_get_result(r2, content)
        if result2:
            (versionname,)= result2
            versionname = versionname.replace("\n", "").replace("\r", "").replace("\s", "").replace("&nbsp;","").strip()

        #logger.info(versionname)

        try:
            versionname = versionname.split()[0]
            if versionname.startswith("V"):
                versionname = versionname.replace("V", "")
        except:
            pass
        # download = int(d("i[itemprop='interactionCount']").attr("content").split(":")[1])
        dnum = d("i[itemprop='interactionCount']").attr("content").split(":")[1]
        download = None
        try:
            download = int(dnum)
        except:
            if dnum.find("万") >= 0:
                download = int(float(dnum.replace("万", "").strip()) * 10000)
            elif dnum.find("亿") >= 0:
                download = int(float(dnum.replace("亿", "").strip()) * 10000 * 10000)
            else:
                logger.info("********download :%s cannot get", dnum)

        item = {
            "link": url,
            "apkname": apkname,
            "appmarket": APPMARKET,
            "name": name,
            "brief": brief,
            "website": website,
            "description": desc,
            "commentbyeditor": commentbyeditor,
            "updateDate": updatedate,
            "language": None,
            "tags": tags,
            "version": versionname,
            "updates": updates,
            "size": size,
            "compatibility": compatibility,
            "icon": icon,
            "author": author,
            "screenshots": screenshots,
            "type": None,
            "key": apkname,
            "key_int": None,
            "download":download,
            }

        logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))

        android.save(collection, APPMARKET, item)
        android.merge(item)
        collection_android.update_one({"apkname": apkname}, {"$set": {"wandoujiaprocessed": True, "wandoujiafound": True}})

    else:
        logger.info("App: %s has no content", apkname)
        #logger.info(content)
        collection_android.update_one({"apkname": apkname}, {"$set": {"wandoujiaprocessed": True, "wandoujiafound": False}})


def run(crawler):
    while True:
        if len(APKS) ==0:
            return
        apkname = APKS.pop(0)

        url = "https://www.wandoujia.com/apps/%s" % apkname
        while True:
            result = crawler.crawl(url, agent=True, redirect=False)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(crawler, url, apkname, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect' and (result['url'] ==  "http://www.wandoujia.com/" or result['url'] ==  "https://www.wandoujia.com/" or result['url'].find("pmt.wandoujia.com") >0):
                logger.info("App: %s is not found", apkname)
                collection_android.update_one({"apkname": apkname}, {"$set": {"wandoujiaprocessed": True, "wandoujiafound": False}})
                break
            elif result['get'] == 'fail' and result["content"] is not None:
                if result["content"].find("抱歉，豌豆们没有找到这个页面") > 0:
                    logger.info("App: %s is not found", apkname)
                    collection_android.update_one({"apkname": apkname}, {"$set": {"wandoujiaprocessed": True, "wandoujiafound": False}})
                    break




def start_run(concurrent_num):
    while True:
        logger.info("wandoujia start...")
        # run(appmkt, WandoujiaCrawler(), "com.ctd.m3gd")
        apps = list(collection_android.find({"wandoujiaprocessed": None},{"apkname":1}, limit=1000))
        for app in apps:
            apkname = app["apkname"]
            if apkname is None:
                continue
            APKS.append(apkname)
        # APKS.append("com.xingin.xhs")
        threads = [gevent.spawn(run, WandoujiaCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


        logger.info("wandoujia end.")
        # exit()
        if len(apps) == 0:
            gevent.sleep(30*60)

if __name__ == "__main__":
    start_run(1)