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
import pycurl

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

def prepare_curl_socks4(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)


def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)

def request(url,callback):
    proxy = {"http_type":"Socks4"}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        #logger.info(proxy_ip)
        if proxy_ip is None:
            time.sleep(60)
    headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    headers[
        "Host"] = "itunes.apple.com"
    headers["Accept-Language"] = "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = ""

    if proxy["http_type"].lower() == "socks4":
        http_request = tornado.httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks4,
            proxy_host=proxy_ip["ip"],
            proxy_port=int(proxy_ip["port"]),
            headers=headers,
            validate_cert=False,
            request_timeout=10, connect_timeout=10
        )
    else:
        http_request = tornado.httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks5,
            proxy_host=proxy_ip["ip"],
            proxy_port=int(proxy_ip["port"]),
            headers=headers,
            request_timeout = 10, connect_timeout = 10
        )

    logger.info("Proxy: %s:%s", proxy_ip["ip"],proxy_ip["port"])
    http_client.fetch(http_request, callback)


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
                            collection_itunes.update_one({"_id": record["_id"]}, {'$set': {"checkTime": datetime.datetime.now()}})
                            if record.get("offline_itunes",None) == 'Y':
                                offrecord = {"offlineDetectTime": datetime.datetime.now(), "offline_itunes": 'N'}
                                collection_itunes.update_one({"_id": record["_id"]}, {'$set': {"offline_itunes": 'N',
                                                                                               "offlineitunesDetectTime": datetime.datetime.now()},
                                                                                      '$addToSet': {"offline_itunes_histories": offrecord}})
                            _id = record.pop("_id")
                            if LooseVersion(result["version"]) > LooseVersion(record["version"]):
                            # if 1:
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
            elif data["resultCount"] == 0:
                record = collection_itunes.find_one({"trackId": trackId}, projection={'histories': False})
                logger.info("***********Offline************")
                if record:
                    if record.get("offline_itunes",None) is None or record.get("offline_itunes",None) == 'N':
                        offrecord = {"offlineDetectTime": datetime.datetime.now(), "offline_itunes": 'Y'}
                        collection_itunes.update_one({"_id": record["_id"]}, {'$set': {"offline_itunes": 'Y',
                                                                                       "offlineitunesDetectTime": datetime.datetime.now(),
                                                                                       "checkTime": datetime.datetime.now()},
                                                                              '$addToSet': {"offline_itunes_histories": offrecord}})
                    else:
                        collection_itunes.update_one({"_id": record["_id"]},{'$set': {"checkTime": datetime.datetime.now()}})
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
        # request(response.request.url, lambda r, data=data: save_itunes(r,data))
        # return
    else:
        try:
            html = response.body
            d = pq(html)
            developer = d(".product-header__identity> a").text()
            if developer is not None:
                developer = developer.replace("开发商：", "")
            data["developer"] = developer

            supportUrl = None
            links = d('li.t-subbody>a.targeted-link.link.icon')
            for i in links:
                title = pq(i).text().strip()
                if title.endswith("支持"):
                    supportUrl = pq(i).attr('href').strip()
            data["supportUrl"] = url_helper.url_normalize(supportUrl)

            logger.info("********************Developer: %s->supportUrl: %s", data["developer"], data["supportUrl"])

            relatedApps = []
            try:
                # divs = d('div.swoosh')
                # for div in divs:
                #     e = pq(div)
                #     if e('div.title').text().strip() == "Customers Also Bought" or e('div.title').text().strip() == "用户购买的还有":
                #         apps = e('div.content> div> div.application')
                #         for app in apps:
                #             app_id = pq(app).attr('adam-id')
                #             relatedApps.append(int(app_id))
                            #logger.info("*********************%s", app_id)
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
            logger.info("*********************%s", relatedApps)
            data["relatedApps"] = relatedApps

            userComments = []
            cdivs = d('div.l-row.l-row--peek> div.ember-view')
            for cdiv in cdivs:
                c = pq(cdiv)
                try:
                    c_title = c('div.we-customer-review> div.we-customer-review__header> h3').eq(1).text().strip()
                    c_commentator = c('div.we-customer-review__user').eq(1).text().replace("评论人：","").strip()
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
        apps = conn.query("select * from artifact where type=4040 and (active is null or active='Y') and id>%s order by id limit 1000", cnt)
        # apps = conn.query("select * from artifact where id=1065719")
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
            logger.info(date_num)
            m = collection_itunes.find_one({"trackId": trackId})
            if m is None:
                continue
            if m.has_key("checkTime") is True and m["checkTime"] > datetime.datetime.now() - datetime.timedelta(hours=12):
                continue
            r = collection.find_one(({"trackId": trackId, "date": today}))
            if r is not None:
                #pass
                continue
            logger.info("%s, %s", app["name"], trackId)

            total += 1
            url = "https://itunes.apple.com/cn/lookup?id=%s" % trackId
            request(url, lambda r,app=app,date_num=date_num:handle_lookup_result(r, app, date_num))
            flag = True


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=20)
    instance=tornado.ioloop.IOLoop.instance()
    begin()
    instance.start()