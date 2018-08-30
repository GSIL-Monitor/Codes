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



types = {
    "free": 27,
    "charge": 30,
    "grossing": 38,
}

genres = [
    {"name":"商务",       "id":6000,  "url":"https://itunes.apple.com/cn/genre/ios-shang-wu/id6000?mt=8"},
    {"name":"商品指南",    "id":6022,  "url":"https://itunes.apple.com/cn/genre/ios-shang-pin-zhi-nan/id6022?mt=8"},
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
    {"name":"冒险游戏",    "id":7002,},
    {"name":"街机游戏",    "id":7003,},
    {"name":"桌面游戏",    "id":7004,},
    {"name":"卡牌游戏",    "id":7005,},
    {"name":"娱乐场游戏",   "id":7006,},
    {"name":"骰子游戏",    "id":7007,},
    {"name":"教育类游戏",    "id":7008,},
    {"name":"聚会游戏",    "id":7009,},
    {"name":"音乐",    "id":7011,},
    {"name":"益智解谜",    "id":7012,},
    {"name":"赛车游戏",    "id":7013,},
    {"name":"角色扮演游戏",   "id":7014,},
    {"name":"模拟游戏",    "id":7015,},
    {"name":"体育",    "id":7016,},
    {"name":"策略游戏",    "id":7017,},
    {"name":"问答游戏",    "id":7018,},
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


def begin():
    global total

    t = datetime.datetime.strptime("2018-01-06", "%Y-%m-%d").date()
    # t = datetime.date.today()
    datestr = datetime.date.strftime(t,'%Y-%m-%d')
    dt = datetime.datetime.strptime(str(t), '%Y-%m-%d')

    for type in types:
        # logger.info("Type: %s" % types[type])
        r = appstore_rank_collection.find_one({"date": dt, "type": type, "genre": None, "rank": 1})
        if r is None:
            logger.info("%s|None is missing",type)

        #
        for genre in genres:
            #logger.info("Type: %s, Genre: %s" % (type,genre["id"]))
            r = appstore_rank_collection.find_one({"date": dt, "type": type, "genre": genre["id"], "rank": 1})
            if r is None:
                logger.info("%s|%s is missing",type, genre["id"])

if __name__ == "__main__":
    begin()