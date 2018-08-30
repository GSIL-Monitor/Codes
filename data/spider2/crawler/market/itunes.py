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
import loghelper, db, util, url_helper, name_helper

#logger
loghelper.init_logger("itunes", stream=True)
logger = loghelper.get_logger("itunes")

APPS = []

class ItunesCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url, content):
        if url.startswith("https://itunes.apple.com/cn/lookup"):
            if content.find('resultCount') > 0:
                return True
        if content.find("400-666-8800") > 0:
            return True
        if content.find("正在连接到 iTunes Store。") > 0:
            return True
        if content.find("support@chinacache.com") > 0:  #您所请求的网址（URL）无法获取
            return True

        return False


def run():
    crawler = ItunesCrawler()
    while True:
        if len(APPS) == 0:
            return

        item = APPS.pop(0)

        mongo = db.connect_mongo()
        record = mongo.market.itunes.find_one({"trackId":item["trackId"]}, projection={'histories': False})
        mongo.close()
        if record is not None:
            mongo = db.connect_mongo()
            mongo.market.itunes_index.update({"_id":item["_id"]},{"$set":{"processed": True}})
            mongo.close()
            continue

        url = "https://itunes.apple.com/cn/lookup?id=%s" % item["trackId"]
        data = None
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                rjson = json.loads(result["content"])
                if rjson["resultCount"] > 0:
                    data = rjson["results"][0]
                break
        if data is None:
            mongo = db.connect_mongo()
            mongo.market.itunes_index.update({"_id":item["_id"]},{"$set":{"processed": True}})
            mongo.close()
            continue

        #url = item["trackViewUrl"].replace("https://","http://")
        url = item["trackViewUrl"]
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                d = pq(result["content"])


                # developer = d("div.intro> div.left> h2").text()
                # if developer is not None:
                #     developer = developer.replace("开发商：","")
                # data["developer"] = developer
                developer = d(".product-header__identity> a").text()
                if developer is not None:
                    developer = developer.replace("开发商：", "")
                data["developer"] = developer



                # supportUrl = None
                # links = d('li.t-subbody>a.targeted-link.link.icon')
                # for i in links:
                #     title = pq(i).text().strip()
                #     if title.endswith("支持"):
                #         supportUrl = pq(i).attr('href').strip()
                #         break
                # data["supportUrl"] = url_helper.url_normalize(supportUrl)

                supportUrl = None
                links = d('li.t-subbody>a.targeted-link.link.icon')
                for i in links:
                    title = pq(i).text().strip()
                    if title.endswith("支持"):
                        supportUrl = pq(i).attr('href').strip()
                        break
                data["supportUrl"] = url_helper.url_normalize(supportUrl)




                relatedApps = []
                # try:
                #     divs = d('div.swoosh')
                #     for div in divs:
                #         e = pq(div)
                #         if e('div.title').text().strip() == "Customers Also Bought" or e('div.title').text().strip() == "用户购买的还有":
                #             apps = e('div.content> div> div.application')
                #             for app in apps:
                #                 app_id = pq(app).attr('adam-id')
                #                 relatedApps.append(int(app_id))
                #                 # logger.info("*********************%s", app_id)
                # except:
                #     pass

                try:
                    apps = d('div.l-row.l-row--peek> a')
                    for app in apps:
                        appurl = pq(app).attr('href')
                        r = util.re_get_result('/id(\d*)', appurl)
                        if r is not None:

                            track_id, = r
                            try:
                                app_id = int(track_id)
                                relatedApps.append(int(app_id))
                            except:
                                pass
                except:
                    pass
                #logger.info("*********************%s", relatedApps)
                data["relatedApps"] = relatedApps



                userComments = []
                # cdivs = d('div.customer-reviews> div.customer-review')
                # for cdiv in cdivs:
                #     c = pq(cdiv)
                #     try:
                #         c_title = c('span.customerReviewTitle').text().strip()
                #         c_commentator = c('span.user-info').text().replace("评论人：", "").strip()
                #         c_content = c('p.content').text().strip()
                #
                #         comment = {
                #             "title": c_title,
                #             "commentator": c_commentator,
                #             "content": c_content
                #         }
                #         userComments.append(comment)
                #
                #     except:
                #         pass

                cdivs = d('div.l-row.l-row--peek> div.ember-view')
                for cdiv in cdivs:
                    c = pq(cdiv)
                    try:
                        c_title = c('div.we-customer-review> div.we-customer-review__header> h3').eq(1).text().strip()
                        c_commentator = c('div.we-customer-review__user').eq(1).text().replace("评论人：", "").strip()
                        c_content = c('p.we-customer-review__body').attr("aria-label")

                        comment = {
                            "title": c_title,
                            "commentator": c_commentator,
                            "content": c_content
                        }
                        userComments.append(comment)

                    except:
                        pass

                logger.info(json.dumps(userComments, ensure_ascii=False, cls=util.CJsonEncoder))
                data["userComments"] = userComments

                break
            elif result['get'] == 'fail' and result["content"] is not None:
                if result["content"].find("Your request produced an error.") >= 0:
                    break

        if data.has_key("supportUrl") and data["supportUrl"] is not None:
            flag, domain = url_helper.get_domain(data["supportUrl"])
            if flag:
                data["supportDomain"] = domain
            else:
                data["supportDomain"] = None
        if data.has_key("sellerUrl") and data["sellerUrl"] is not None:
            data["sellerUrl"] = url_helper.url_normalize(data["sellerUrl"])
            flag, domain = url_helper.get_domain(data["sellerUrl"])
            if flag:
                data["sellerDomain"] = domain
            else:
                data["sellerDomain"] = None

        short_name = name_helper.get_short_name(data["trackName"])
        data["trackShortName"] = short_name
        logger.info(json.dumps(data, ensure_ascii=False, cls=util.CJsonEncoder))

        mongo = db.connect_mongo()
        record = mongo.market.itunes.find_one({"trackId":data["trackId"]}, projection={'histories': False})
        if record:
            _id = record.pop("_id")
            if LooseVersion(data["version"]) > LooseVersion(record["version"]):
                data["createTime"] = record["createTime"]
                data["modifyTime"] = datetime.datetime.now()
                mongo.market.itunes.update_one({"_id":_id},{'$set':data, '$addToSet':{"histories":record}})
            # elif LooseVersion(data["version"]) == LooseVersion(record["version"]):
            #     data["modifyTime"] = datetime.datetime.now()
            #     collection.update_one({"_id": _id}, {'$set': data})
        else:
            data["createTime"] = datetime.datetime.now()
            data["modifyTime"] = data["createTime"]
            mongo.market.itunes.insert(data)
        mongo.market.itunes_index.update({"_id":item["_id"]},{"$set":{"processed": True}})
        mongo.close()


def start_run(concurrent_num):
    while True:
        logger.info("Itunes start...")
        mongo = db.connect_mongo()
        apps = list(mongo.market.itunes_index.find({"processed": None}, limit=1000))
        mongo.close()
        for app in apps:
            APPS.append(app)
        threads = [gevent.spawn(run) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


        logger.info("end.")

        if len(apps) == 0:
            gevent.sleep(5*60)


if __name__ == "__main__":
    start_run(10)