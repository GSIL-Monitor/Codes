# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
from pymongo import MongoClient
import pymongo
import datetime, time
import json
import urllib
import traceback
from distutils.version import LooseVersion

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, url_helper, name_helper
import config
import util
import proxy_pool
import db

#logger
loghelper.init_logger("itunes_trends", stream=True)
logger = loghelper.get_logger("itunes_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.itunes

collection_itunes = mongo.market.itunes


cnt = 0
total = 0


def request(url,callback):
    # proxy = {'type': 'https', 'anonymity':'high', 'ping':1, 'transferTime':5}
    if url.find("https") >= 0:
        proxy = {'type': 'https', 'anonymity':'high'}
    else:
        proxy = {'type': 'http', 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    # logger.info("Getting :%s",url)
    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10, connect_timeout=10)


def handle_lookup_result(response, app, date_num):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        logger.info("Last Total number of current patch: %s", total)
        request(response.request.url, lambda r,app=app,date_num=date_num:handle_lookup_result(r, app, date_num))
        return
    else:
        logger.info("Getting result from url: %s", response.request.url)
        trackId = int(app["domain"])
        try:
            data = json.loads(response.body)
            if data["resultCount"] > 0:
                for result in data["results"]:
                    if result.get("trackId") == trackId:
                        score = result.get("averageUserRating")
                        comment = result.get("userRatingCount")
                        logger.info("companyId=%s, artifactId=%s, score=%s, comment=%s, date_num=%s"
                                            % (app["companyId"],app["id"],score, comment, date_num))

                        if score is not None or comment is not None:
                            save_comment(app["trackId"],score, comment)

                        logger.info("Last Total number of current patch: %s", total)

                        if result.has_key("sellerUrl") and result["sellerUrl"] is not None:
                            result["sellerUrl"] = url_helper.url_normalize(result["sellerUrl"])
                            flag, domain = url_helper.get_domain(result["sellerUrl"])
                            if flag:
                                result["sellerDomain"] = domain
                            else:
                                result["sellerDomain"] = None

                        short_name = name_helper.get_short_name(result["trackName"])
                        result["trackShortName"] = short_name

                        record = collection_itunes.find_one({"trackId": result["trackId"]},projection={'histories': False})
                        if record:
                            _id = record.pop("_id")
                            if LooseVersion(result["version"]) > LooseVersion(record["version"]):

                                page_url = result.get("trackViewUrl").replace("&uo=4", "")

                                if date_num == 6 and page_url is not None and page_url.strip() != "":
                                    # only do it when date is 6/16/226
                                    logger.info("Need to crawler page data: %s",page_url)
                                    total += 1
                                    request(page_url, lambda r, appdata=result: save_itunes(r, appdata))
                                else:
                                    logger.info(json.dumps(result, ensure_ascii=False, cls=util.CJsonEncoder))
                                    result["createTime"] = record["createTime"]
                                    result["modifyTime"] = datetime.datetime.now()
                                    collection_itunes.update_one({"_id": _id},{'$set': result, '$addToSet': {"histories": record}})
                        else:
                            result["createTime"] = datetime.datetime.now()
                            result["modifyTime"] = result["createTime"]
                            collection_itunes.insert(result)

                        break
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        # exit(0)

def save_itunes(response, data):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error, response.request.url))
        request(response.request.url, lambda r, data=data: save_itunes(r,data))
        return
    else:
        try:
            html = response.body
            d = pq(html)
            developer = d("div.intro> div.left> h2").text()
            if developer is not None:
                developer = developer.replace("开发商：", "")
            data["developer"] = developer

            supportUrl = None
            links = d('div.app-links').find('a.see-all')
            for i in links:
                title = pq(i).text().strip()
                if title.endswith("支持"):
                    supportUrl = pq(i).attr('href').strip()
            data["supportUrl"] = url_helper.url_normalize(supportUrl)

            logger.info("********************Developer: %s->supportUrl: %s", data["developer"], data["supportUrl"])

            relatedApps = []
            try:
                divs = d('div.swoosh')
                for div in divs:
                    e = pq(div)
                    if e('div.title').text().strip() == "Customers Also Bought" or e('div.title').text().strip() == "用户购买的还有":
                        apps = e('div.content> div> div.application')
                        for app in apps:
                            app_id = pq(app).attr('adam-id')
                            relatedApps.append(int(app_id))
                            #logger.info("*********************%s", app_id)
            except:
                pass
            logger.info("*********************%s", relatedApps)
            data["relatedApps"] = relatedApps

            userComments = []
            cdivs = d('div.customer-reviews> div.customer-review')
            for cdiv in cdivs:
                c = pq(cdiv)
                try:
                    c_title = c('span.customerReviewTitle').text().strip()
                    c_commentator = c('span.user-info').text().replace("评论人：","").strip()
                    c_content = c('p.content').text().strip()

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

            if data["supportUrl"] is not None:
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

            record = collection_itunes.find_one({"trackId": data["trackId"]}, projection={'histories': False})
            if record:
                _id = record.pop("_id")
                if LooseVersion(data["version"]) > LooseVersion(record["version"]):
                    data["createTime"] = record["createTime"]
                    data["modifyTime"] = datetime.datetime.now()
                    collection_itunes.update_one({"_id": _id}, {'$set': data, '$addToSet': {"histories": record}})
                # elif LooseVersion(data["version"]) == LooseVersion(record["version"]):
                #     data["modifyTime"] = datetime.datetime.now()
                #     collection_itunes.update_one({"_id": _id}, {'$set': data})
            else:
                data["createTime"] = datetime.datetime.now()
                data["modifyTime"] = data["createTime"]
                collection_itunes.insert(data)

        except:
            traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()
        # exit(0)



def save_comment(trackId, score, comment):
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    r = collection.find_one(({"trackId":trackId, "date": today}))

    if r is None:
        result = {
            "trackId": trackId,
            "date":today,
            "comment": comment,
            "score":score
        }
        collection.insert_one(result)
    else:
        result = {
            "comment": comment,
            "score":score
        }
        collection.update_one({"_id": r["_id"]}, {'$set': result})


@gen.engine
def begin():
    global total, cnt

    flag = False
    while flag is False:
        logger.info("Getting new patch artifacts")
        conn = db.connect_torndb()
        apps = conn.query("select * from artifact where type=4040 and id>%s order by id limit 1000", cnt)
        conn.close()

        if len(apps) <= 0:
            while True:
                if total <= 0:
                    logger.info("Finish.")
                    #time.sleep(60*60*6)  # 6hours
                    exit()
                yield gen.Task(instance.add_timeout, time.time() + 10)

        for app in apps:
            logger.info(app["id"])
            if app["id"] > cnt:
                cnt = app["id"]

            if app["domain"] is None or app["domain"].strip() == "":
                continue

            trackId = int(app["domain"].strip())
            app["trackId"] = trackId
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            datestr = datetime.date.strftime(dt, '%Y%m%d')
            date_num = int(datestr)%10

            m = collection_itunes.find_one({"trackId": trackId})
            if m is None:
                continue

            r = collection.find_one(({"trackId": trackId, "date": today}))
            if r is not None:
                #pass
                continue
            logger.info("%s, %s", app["name"], trackId)

            total += 1
            url = "http://itunes.apple.com/cn/lookup?id=%s" % trackId
            request(url, lambda r,app=app,date_num=date_num:handle_lookup_result(r, app, date_num))
            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()