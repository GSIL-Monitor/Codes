# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pymongo import MongoClient
import datetime, time
import json
import urllib
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util
import proxy_pool
import db


#logger
loghelper.init_logger("appstore_rank", stream=True)
logger = loghelper.get_logger("appstore_rank")

#mongo

mongo = db.connect_mongo()
appstore_rank_collection = mongo.trend.appstore_rank

total = 0


headers = {
    'x-auth-token': 'eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE1NDE3NTYzODIsInN1YiI6IjVhMDQyMjVlMDhkMGI0NTIzMDFkMTljNiIsImNyZWF0ZWQiOjE1MTAyMjAzODIzNzF9.YSoQa6SCW5662X9zxu_Z_vk0Q355-vH9uvbvlnUUUKEbxLfHBO9UpwggXNOVrPcGNRwRmW69hvJdtUR4kUo36A'
}
def request(url,callback):
    #proxy = {'type': 'http', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)
    #logger.info(url)

    http_client.fetch(url, callback, headers=headers, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)



types = {
    # "free": 27,
    "charge": 30,
    # "grossing": 38,
}

genres = [
    # {"name":"商务",       "id":6000,  "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
#      {"name":"商品指南",    "id":6022,  "url":"https://itunes.apple.com/cn/genre/ios-shang-pin-zhi-nan/id6022?mt=8"},
#     {"name":"教育",       "id":6017,  "url":"https://itunes.apple.com/cn/genre/ios-jiao-yu/id6017?mt=8"},
#     {"name":"娱乐",       "id":6016,  "url":"https://itunes.apple.com/cn/genre/ios-yu-le/id6016?mt=8"},
#     {"name":"财务",       "id":6015,  "url":"https://itunes.apple.com/cn/genre/ios-cai-wu/id6015?mt=8"},
#     {"name":"美食佳饮",    "id":6023,   "url":"https://itunes.apple.com/cn/genre/ios-mei-shi-jia-yin/id6023?mt=8"},
#     {"name":"健康健美",    "id":6013,   "url":"https://itunes.apple.com/cn/genre/ios-jian-kang-jian-mei/id6013?mt=8"},
#     {"name":"生活",       "id":6012,  "url":"https://itunes.apple.com/cn/genre/ios-sheng-huo/id6012?mt=8"},
#     {"name":"医疗",       "id":6020,  "url":"https://itunes.apple.com/cn/genre/ios-yi-liao/id6020?mt=8"},
#     {"name":"音乐",       "id":6011,  "url":"https://itunes.apple.com/cn/genre/ios-yin-le/id6011?mt=8"},
#     {"name":"导航",       "id":6010,  "url":"https://itunes.apple.com/cn/genre/ios-dao-hang/id6010?mt=8"},
#     {"name":"新闻",       "id":6009,  "url":"https://itunes.apple.com/cn/genre/ios-xin-wen/id6009?mt=8"},
#     {"name":"摄影与录像",  "id":6008,    "url":"https://itunes.apple.com/cn/genre/ios-she-ying-yu-lu-xiang/id6008?mt=8"},
#    {"name":"效率",       "id":6007,  "url":"https://itunes.apple.com/cn/genre/ios-xiao-lu/id6007?mt=8"},
{"name":"报刊杂志",    "id":6021,},
#     {"name":"参考",       "id":6006,  "url":"https://itunes.apple.com/cn/genre/ios-can-kao/id6006?mt=8"},
#     {"name":"购物",       "id":6024,  "url":"https://itunes.apple.com/cn/genre/ios-gou-wu/id6024?mt=8"},
#     {"name":"社交",       "id":6005,  "url":"https://itunes.apple.com/cn/genre/ios-she-jiao/id6005?mt=8"},
#     {"name":"体育",       "id":6004,  "url":"https://itunes.apple.com/cn/genre/ios-ti-yu/id6004?mt=8"},
#     {"name":"旅游",       "id":6003,  "url":"https://itunes.apple.com/cn/genre/ios-lu-you/id6003?mt=8"},
#     {"name":"工具",       "id":6002,  "url":"https://itunes.apple.com/cn/genre/ios-gong-ju/id6002?mt=8"},
#     {"name":"天气",       "id":6001,  "url":"https://itunes.apple.com/cn/genre/ios-tian-qi/id6001?mt=8"},
]


def handle_result(response, data):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,data=data:handle_result(r, data))
        return
    else:
        try:
            result = json.loads(response.body)

            logger.info(response.request.url)
            dt = datetime.datetime.strptime(str(data["date"]), '%Y-%m-%d')
            #logger.info(response.body)
            if result.has_key("total") and result["total"] > 0:
                logger.info("****offset %s->%s**************Type: %s, Genre: %s, number of app: %s, real number: %s",
                            result['offset'], data["offset"],data["type"], data["genre"], result["total"], len(result["contents"]))
                
                # if len(result["contents"]) < 500 and result["total"] > len(result["contents"]) + 30 + data["offset"]:
                if len(result["contents"]) < 70 and result["total"] > len(result["contents"]) + 10 + data["offset"]:
                    logger.info("missing data, re-fetch %s" % (response.request.url))
                    request(response.request.url, lambda r, data=data: handle_result(r, data))
                    return
                elif int(result['offset']) != int(data["offset"]):
                    logger.info("***************wrong offset")
                    # logger.info("missing data, re-fetch %s" % (response.request.url))
                    request(response.request.url, lambda r, data=data: handle_result(r, data))
                    return
                else:
                    rank = data["offset"]
                    for list in result["contents"]:
                        rank += 1
                        try:
                            trackId = list["appId"]
                            logger.info("%s, %s, %s, %s, %s" % (data["type"], data["genre"], list.get("name"), list["appId"], rank))

                            r = appstore_rank_collection.find_one({"date":dt, "type":data["type"], "genre":data["genre"], "trackId":trackId})
                            if r is None:
                                appstore_rank_collection.insert_one({"date":dt, "type":data["type"], "genre":data["genre"], "trackId":trackId, "rank":rank})
                            else:
                                # appstore_rank_collection.replace_one({"_id":r["_id"]},{"date":dt, "type":data["type"], "genre":data["genre"], "trackId":trackId, "rank":rank})
                                pass
                        except:
                            continue

                    if result["total"] > len(result["contents"]) + 10 + data["offset"]:
                        if data["genre"] is None:
                            # newurl = "http://backend.cqaso.com/topList/36/%s?limit=70&offset=%s&country=CN"  % \
                            #          (types[data["type"]], str(data["offset"]+70))
                            newurl = "http://backend.cqaso.com/topList/snapshot/20170802:0854:36:%s?limit=70&offset=%s&country=CN" % \
                                     (types[data["type"]], str(data["offset"] + 70))
                        else:
                            # newurl = "http://backend.cqaso.com/topList/%s/%s?limit=70&offset=%s&country=CN" % \
                            #          (data["genre"], types[data["type"]], str(data["offset"]+70))
                            newurl = "http://backend.cqaso.com/topList/%s/%s?limit=70&offset=%s&country=CN" % \
                                     (data["genre"], types[data["type"]], str(data["offset"] + 70))
                        ndata = {"type": data["type"], "genre": data["genre"], "date": data["date"], "offset": data["offset"]+70}
                        total += 1
                        request(newurl, lambda r, ndata=ndata: handle_result(r, ndata))



        except:
            traceback.print_exc()
            request(response.request.url, lambda r, data=data: handle_result(r, data))
            return

    total -= 1
    if total <=0:
        logger.info("End.")
        exit(0)

def begin():
    global total

    t = datetime.datetime.strptime("2017-12-15", "%Y-%m-%d").date()
    #datestr = datetime.date.strftime(t,'%Y%m%d')

    for type in types:
        logger.info("Type: %s" % type)
        # for offset in [0]:
        #     total += 1
        #     # url = "http://backend.cqaso.com/topList/36/%s?limit=500&offset=%s&country=CN" % (types[type], str(offset))
        #     url = "http://backend.cqaso.com/topList/snapshot/20170802:0854:36:%s?limit=70&offset=%s&country=CN" % (types[type], str(offset))
        #     data = {"type":type, "genre": None, "date":t, "offset": offset}
        #     request(url, lambda r,data=data:handle_result(r, data))
        #
        for genre in genres:
            #logger.info("Type: %s, Genre: %s" % (type,genre["id"]))
            for offset in [0]:
                total += 1
                url = "http://backend.cqaso.com/topList/%s/%s?limit=500&offset=%s&country=CN" % (genre["id"], types[type], str(offset))
                data = {"type":type, "genre": genre["id"], "date":t, "offset": offset}
                request(url, lambda r,data=data:handle_result(r, data))

if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=1)
    begin()
    tornado.ioloop.IOLoop.instance().start()
    # begin()