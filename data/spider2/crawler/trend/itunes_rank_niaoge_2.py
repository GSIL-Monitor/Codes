# -*- coding: utf-8 -*-
import sys, os
from lxml import html
from pyquery import PyQuery as pq
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
loghelper.init_logger("appstore_rank_2", stream=True)
logger = loghelper.get_logger("appstore_rank_2")

#mongo

mongo = db.connect_mongo()
appstore_rank_collection = mongo.trend.appstore_rank

total = 0


headers = {
    'x-auth-token': 'eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE1NDA0NTgzNDgsInN1YiI6IjU5ZjA1M2VjODlkZTI2NjE0MWQ1NzM4YyIsImNyZWF0ZWQiOjE1MDg5MjIzNDg2OTB9.GrGTMTrC5JHhu8du9CpEo_zvsuYmzidlreUeZUpgp2iepAcMTPLB2aTX-QJ77dmt6lW8bBokJLUbc53x-80p6g'
}

headers[
    "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"


def request(url,callback):
    #proxy = {'type': 'http', 'anonymity':'high', 'ping':1, 'transferTime':5}
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)
    logger.info("crawler: %s",url)

    http_client.fetch(url, callback, headers=headers, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),
                      request_timeout=15.0, connect_timeout=15.0)



types = {
    "free": 27,
    "charge": 30,
    "grossing": 38,
}

genres = [
    {"name":"商务",       "id":6000,  "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
    # {"name":"商品指南",    "id":6022,  "url":"https://itunes.apple.com/cn/genre/ios-shang-pin-zhi-nan/id6022?mt=8"},
    {"name":"教育",       "id":6017,  "url":"https://itunes.apple.com/cn/genre/ios-jiao-yu/id6017?mt=8"},
    {"name":"娱乐",       "id":6016,  "url":"https://itunes.apple.com/cn/genre/ios-yu-le/id6016?mt=8"},
    {"name":"财务",       "id":6015,  "url":"https://itunes.apple.com/cn/genre/ios-cai-wu/id6015?mt=8"},
    {"name":"美食佳饮",    "id":6023,   "url":"https://itunes.apple.com/cn/genre/ios-mei-shi-jia-yin/id6023?mt=8"},
    {"name":"健康健美",    "id":6013,   "url":"https://itunes.apple.com/cn/genre/ios-jian-kang-jian-mei/id6013?mt=8"},
    {"name":"生活",       "id":6012,  "url":"https://itunes.apple.com/cn/genre/ios-sheng-huo/id6012?mt=8"},
    {"name":"医疗",       "id":6020,  "url":"https://itunes.apple.com/cn/genre/ios-yi-liao/id6020?mt=8"},
    {"name":"音乐",       "id":6011,  "url":"https://itunes.apple.com/cn/genre/ios-yin-le/id6011?mt=8"},
    {"name":"导航",       "id":6010,  "url":"https://itunes.apple.com/cn/genre/ios-dao-hang/id6010?mt=8"},
    {"name":"新闻",       "id":6009,  "url":"https://itunes.apple.com/cn/genre/ios-xin-wen/id6009?mt=8"},
    {"name":"摄影与录像",  "id":6008,    "url":"https://itunes.apple.com/cn/genre/ios-she-ying-yu-lu-xiang/id6008?mt=8"},
    {"name":"效率",       "id":6007,  "url":"https://itunes.apple.com/cn/genre/ios-xiao-lu/id6007?mt=8"},
    {"name":"参考",       "id":6006,  "url":"https://itunes.apple.com/cn/genre/ios-can-kao/id6006?mt=8"},
    {"name":"购物",       "id":6024,  "url":"https://itunes.apple.com/cn/genre/ios-gou-wu/id6024?mt=8"},
    {"name":"社交",       "id":6005,  "url":"https://itunes.apple.com/cn/genre/ios-she-jiao/id6005?mt=8"},
    {"name":"体育",       "id":6004,  "url":"https://itunes.apple.com/cn/genre/ios-ti-yu/id6004?mt=8"},
    {"name":"旅游",       "id":6003,  "url":"https://itunes.apple.com/cn/genre/ios-lu-you/id6003?mt=8"},
    {"name":"工具",       "id":6002,  "url":"https://itunes.apple.com/cn/genre/ios-gong-ju/id6002?mt=8"},
    {"name":"天气",       "id":6001,  "url":"https://itunes.apple.com/cn/genre/ios-tian-qi/id6001?mt=8"},
    # {"name":"贴纸",       "id":6025,  },
    {"name":"游戏",       "id":6014,  },
    {"name":"动作游戏",    "id":7001,},
    {"name":"探险游戏",    "id":7002,},
    {"name":"街机游戏",    "id":7003,},
    {"name":"桌面游戏",    "id":7004,},
    {"name":"扑克牌游戏",    "id":7005,},
    {"name":"娱乐场游戏",   "id":7006,},
    # {"name":"骰子游戏",    "id":7007,},
    {"name":"教育游戏",    "id":7008,},
    {"name":"家庭游戏",    "id":7009,},
    {"name":"音乐",    "id":7011,},
    {"name":"智力游戏",    "id":7012,},
    {"name":"赛车游戏",    "id":7013,},
    {"name":"角色扮演游戏",   "id":7014,},
    {"name":"模拟游戏",    "id":7015,},
    {"name":"体育",    "id":7016,},
    {"name":"策略游戏",    "id":7017,},
    {"name":"小游戏",    "id":7018,},
    {"name":"文字游戏",    "id":7019,},
    {"name":"报刊杂志",    "id":6021,},
    # {"name":"报刊杂志-新闻及政治",   "id":13001,},
    # {"name":"报刊杂志-流行与时尚",    "id":13002,},
    # {"name":"报刊杂志-家居与园艺", "id": 13003, },
    # {"name":"报刊杂志-户外与自然", "id": 13004, },
    # {"name":"报刊杂志-运动与休闲", "id": 13005, },
    # {"name":"报刊杂志-汽车", "id": 13006, },
    # {"name":"报刊杂志-艺术与摄影", "id": 13007, },
    # {"name":"报刊杂志-新娘与婚礼", "id": 13008, },
    # {"name":"报刊杂志-商务与投资", "id": 13009, },
    # {"name":"报刊杂志-儿童杂志", "id": 13010, },
    # {"name":"报刊杂志-电脑与网络", "id": 13011, },
    # {"name":"报刊杂志-烹饪与饮食", "id": 13012, },
    # {"name":"报刊杂志-手工艺与爱好",   "id":13013,},
    # {"name":"报刊杂志-电子产品与音响",   "id":13014,},
    # {"name":"报刊杂志-娱乐", "id": 13015, },
    # {"name":"报刊杂志-健康、心理与生理", "id": 13017, },
    # {"name":"报刊杂志-历史", "id": 13018, },
    # {"name":"报刊杂志-文学杂志与期刊", "id": 13019, },
    # {"name":"报刊杂志-男士兴趣",  "id":13020,},
    # {"name":"报刊杂志-电影与音乐",   "id":13021,},
    # {"name":"报刊杂志-子女教养与家庭", "id": 13023, },
    # {"name":"报刊杂志-宠物", "id": 13024, },
    # {"name":"报刊杂志-职业与技能", "id": 13025, },
    # {"name":"报刊杂志-地方新闻", "id": 13026, },
    # {"name":"报刊杂志-科学", "id": 13027, },
    # {"name":"报刊杂志-青少年",  "id":13028,},
    # {"name":"报刊杂志-旅游与地域",   "id":13029,},
    # {"name":"报刊杂志-女士兴趣", "id": 13030, },

]

def has_content(content, offset, ranktitle, total):
    try:
        if content is None or content.strip() == "":
            logger.info("here : total %s, offset %s", total, offset)
            if abs(int(total) - int(offset)) < 100:
                return True

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        # if title.find("实时排名")>=0 and content.find("rank-list") >= 0:
        if content.find('/app/rank') >= 0:
            lis = d('div.thumbnaill')
            datatotal = d('div.thumbnaill').eq(0).attr("data-total")
            logger.info("**********total: %s <-> %s", datatotal, total)
            if lis is not None and isinstance(lis, list) is True and len(lis)>0:
                namelong = d(lis[0])('a> div.caption> p').eq(0).text()

                name = namelong.split(".")[0].strip()
                logger.info("here check: %s |  %s---- %s", namelong, name, offset+1)
                if name != str(offset+1):

                    return False
            # else:
            #     logger.info("wrong lis for content")
            #     return False
            if offset == 0:
                rtitle = d('div.title').text()
                if rtitle is None or rtitle.find(ranktitle) == -1:
                    logger.info("here check: wrong title： %s",rtitle)
                    return False
            elif total is not None and datatotal is not None:
                if total == datatotal or abs(int(total)- int(datatotal)) <=130:
                    pass
                else:
                    logger.info("here check: wrong total： %s/%s", total, datatotal)
                    return False


            return True
        else:
            return False
    except:
        return False

def process(content):
    r = {}
    if content is None or content.strip() == "":
        return r
    r["contents"] = []
    d = pq(html.fromstring(content.decode("utf-8","ignore")))
    datatotal = d('div.thumbnaill').eq(0).attr("data-total")
    r["total"] = datatotal
    for li in d('div.thumbnaill'):
        try:
            href = d(li)('a').attr("href").strip()
            name = d(li)('a> div.caption> p').eq(0).text()
            appId = href.split("=")[-1]
            # logger.info("%s, %s", name, appId)
            r["contents"].append({"name": name,"appId":appId})
        except:
            logger.info("herere")
            logger.info(li)
            pass
    return r

def handle_result(response, data):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(response.request.url, lambda r,data=data:handle_result(r, data))
        return
    elif has_content(response.body, data["offset"], data["genreName"], data["total"]) is False:
        logger.info("Error content:%s, %s" % (response.body, response.request.url))
        request(response.request.url, lambda r, data=data: handle_result(r, data))
        return
    else:
        try:

            result = process(response.body)

            dt = datetime.datetime.strptime(str(data["date"]), '%Y-%m-%d')

            if result.has_key("contents") is True:
                logger.info("****offset %s->%s**************Type: %s, Genre: %s, real number: %s",
                            data["offset"],response.request.url,data["type"], data["genre"], len(result["contents"]))

                rank = data["offset"]
                for list in result["contents"]:
                    rank += 1
                    try:
                        trackId = int(list["appId"])
                        logger.info("%s, %s, %s, %s, %s" % (data["type"], data["genre"], list.get("name"), list["appId"], rank))

                        r = appstore_rank_collection.find_one({"date":dt, "type":data["type"], "genre":data["genre"], "trackId":trackId})
                        if r is None:
                            appstore_rank_collection.insert_one({"date":dt, "type":data["type"], "genre":data["genre"], "trackId":trackId, "rank":rank})
                        else:
                            pass
                    except:
                        continue

                if len(result["contents"]) == 200:
                    if data["genre"] is None:
                        newurl = "http://aso.niaogebiji.com/rank/index?pop=%s&genre=36&date=%s&page=%s" % \
                                 (types[data["type"]], data["datestr"], str((data["offset"]+200)/200+1))
                    else:
                        newurl = "http://aso.niaogebiji.com/rank/index?pop=%s&genre=%s&date=%s&page=%s" % \
                                 (types[data["type"]], data["genre"], data["datestr"], str((data["offset"]+200)/200+1))
                    ndata = {"type": data["type"], "genre": data["genre"], "date": data["date"],
                             "offset": data["offset"]+200, "datestr": data["datestr"], "genreName": data["genreName"],
                             "total": result["total"]}
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
    else:
        logger.info("still on %s left",total)

def begin():
    global total

    # t = datetime.datetime.strptime("2018-01-06", "%Y-%m-%d").date()
    t = datetime.date.today()
    datestr = datetime.date.strftime(t,'%Y-%m-%d')

    for type in types:
        logger.info("Type: %s" % type)
        for offset in [0]:
            total += 1
            url = "http://aso.niaogebiji.com/rank/index?pop=%s&genre=36&date=%s" % (types[type], datestr)
            data = {"type":type, "genre": None, "date":t, "offset": offset, "datestr": datestr, "genreName": "总榜",
                    "total": None}
            request(url, lambda r,data=data:handle_result(r, data))

        for genre in genres:
            #logger.info("Type: %s, Genre: %s" % (type,genre["id"]))
            for offset in [0]:
                total += 1
                url = "http://aso.niaogebiji.com/rank/index?pop=%s&genre=%s&date=%s" % (types[type],genre["id"],datestr)
                data = {"type":type, "genre": genre["id"], "date":t, "offset": offset, "datestr": datestr,
                        "genreName": genre["name"], "total": None}
                request(url, lambda r,data=data:handle_result(r, data))

if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=1)
    begin()
    tornado.ioloop.IOLoop.instance().start()