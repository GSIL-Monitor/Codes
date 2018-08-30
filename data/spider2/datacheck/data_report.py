# -*- coding: utf-8 -*-
import os, sys
import datetime
import gridfs
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db
import loghelper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("Data_report", stream=True)
logger = loghelper.get_logger("Data_report")

#mongo
mongo = db.connect_mongo()

collection_proxy = mongo.raw.proxy
collection_proxy2 = mongo.xiniudata.proxy

collection_projectdata = mongo.raw.projectdata
collection_itunes =  mongo.market.itunes
collection_android = mongo.market.android
collection_android_market = mongo.market.android_market
collection_goshang = mongo.info.gongshang
collection_news = mongo.article.news
collection_website = mongo.info.website
collection_job_company = mongo.job.company
collection_job = mongo.job.job
collection_zhihu = mongo.zhihu.raw
collection_alexa_raw = mongo.trend.alexa_raw
collection_alexa = mongo.trend.alexa
collection_appmini_market = mongo.market.appmini_market
collection_appmini = mongo.market.appmini
appstore_rank_collection = mongo.trend.appstore_rank
tkdataApp_rank_collection = mongo.trend.tkdataApp_rank


idmap ={
    1: "crawler",2: "parser",3: "trend",
    13030: "It桔子",13032: "It桔子f", 13020: "36氪", 13022: "36氪创投助手", 13050: "拉勾网", 13055: "boss直聘", 13056:'猎聘网',13130: "crunchbase",
    13511: "feixiaohao",
    13090: "天眼查", 13800: "铅笔道", 13801: "鸵鸟FM", 13802: "微链", 13803: "猎云网",
    13804: "活动行", 13805: "速途", 13806: "创业邦", 13807: "拓扑社", 13808: "艾瑞研究", 13809: "极客公园", 13810: "Pingwest", 13811: "爱范儿",
    13091: "量子", 13092: "元素", 13093: "启信宝", 13095: "知果果",
    13630: "amacmanager", 13631: "amacfund",
    13812: "创投时报", 13813: "小饭桌", 13814: "少数派", 13815: "TechCrunch", 13816: "亿欧网", 13817: "亿邦动力", 13818: "投中", 13819: "i黑马",
    13820: "芥末堆", 13821: "Xtecher", 13822: "环球旅讯", 13823: "虎嗅", 13824: "多知网", 13825: "健康界",13828:'懒熊体育',13827:'一鸣网',
    13829: "百家接招", 13830: "智东西", 13832: "钛媒体",13831: "机器之心", 13833: "雷锋网", 13834: "TechWeb", 13840: "微信公众号",
    13835: "it199", 13836: "useit", 13837: "今日头条",
    13838: "天天投",13610:'知乎日报',13611:'知乎回答',13612:'知乎文章',13613:'烯牛数据', 13841: "新榜热门", 13839: "投资界", 13842: "新芽",
    13843: "鲸媒体",13844: "hrtech", 13845: "vrzinc", 13846: "游戏陀螺", 13850: "网易", 13847: "搜狗微信",13848:'私募通', 13849:"三文娱",13851:"车云网",13852:'火石创造',
    13853: "零壹财经", 13854: "DoNews",13855:'动脉网',13856:'创头条',13857:'华丽志', 13858: "极客帮", 13859: "腾讯科技",13860: "金色财经",
    13861: "白鲸出海", 13862: "晨哨君", 13863: "竺道", 13864: "数据猿", 13866: "金融界",
    13865: "每日经济",13867:"btc123",13868:"未来财经",13869:'人民网创投',
    13870: "巴比特", 13871:"火星财经", 13872: "链财经", 13873: "映维网", 13874: "未央网",13875:"药明康德",13876:"动点科技",13877:"至顶网",
    13878: "品途商业",13879:'和讯网',13880:'中国证券网', 13888: "科技猎", 13891: "中证网",
    13881: "kr-asia", 13884: "dealstreetasia", 13882:'techinasia', 13883:'forbes', 13885:"digitalns",13886:'vilcanpost', 13887:'scmp',13889:'businessinsider', 13890:'dailysocial',
    13892: "e27", 13893: "Bloomberg",
    13021: "36氪Next", 13031: "It桔子Next", 13111: "MindStore",13400: "Neeq",13401: "sse",13402: "szse",
    16010: "360助手", 16020: "百度应用", 16030: "豌豆荚", 16040: "应用宝",16060: "魅族",16070: "小米",16080:'七麦',16090:'华为',
    36001: "公司信息", 36002: "融资事件", 36003: "投资公司", 36004: "投资个人", 36005: "公司成员", 36006: "公司新闻", 36007: "专辑", 36008: "工商",
    36009: "新产品", 36010: "招聘信息", 36011: "商标", 36012: "版权",
    60001: "新闻", 60002: "活动", 60003: "行研", 60004: "海外", 60005: "新闻2",
    60006: "报告",60007: "知乎", 60008:"短讯", 60009:"次要新闻",60010:"超次要新闻",
    36100: "App", 36101: "AppRank", 13901: "AndroidApp", 13902: "ItunesApp", 13900: "Proxy", 36102: "AppRankforAndroid", 13903: "talkingData",
    13904: "Website", 13905: "alexa",13906: "MiniApp",
}
def save(source, type, categoryId, statsDate, cnt, flag):
    conn = db.connect_torndb_crawler()
    #conn = db.connect_torndb()
    stats = conn.get("select * from spider_stats where source=%s and type=%s and categoryId=%s and statsDate=%s limit 1", source, type, categoryId, statsDate)
    if stats is None:
        if flag == 'create':
            sql = "insert spider_stats(statsDate,categoryId,categoryName,source,sourceName,type,typeName,createNum) \
                    values(%s,%s,%s,%s,%s,%s,%s,%s)"
        else:
            sql = "insert spider_stats(statsDate,categoryId,categoryName,source,sourceName,type,typeName,updateNum) \
                    values(%s,%s,%s,%s,%s,%s,%s,%s)"
        conn.insert(sql,statsDate,categoryId,idmap[categoryId],source,idmap[source],type,idmap[type],cnt)
    else:
        stats_id = stats["id"]
        if flag == 'create':
            conn.update("update spider_stats set createNum=%s where id=%s", cnt, stats_id)
        else:
            conn.update("update spider_stats set updateNum=%s where id=%s", cnt, stats_id)
    conn.close()

def gongshang_check(date):
    cnt =  collection_goshang.find({"modifyTime": {"$gt": date}}).count()
    logger.info("qixin, cnt: %s", cnt)
    save(13093, 36008, 2, date, cnt, 'create')

def job_check(source, date, type):
    if type == "company":
        cnt =  collection_job_company.find({"source": source, "modifyTime": {"$gt": date}}).count()
    else:
        cnt = collection_job.find({"source": source, "modifyTime": {"$gt": date}}).count()
    logger.info("source: %s, type: %s, cnt: %s", source, type, cnt)
    # save(13090, 36008, 2, date, cnt, 'create')

def projectdata_check(source,type,date):
    cnt = collection_projectdata.find({"source":source, "type":type, "date": {"$gt":date}}).count()
    logger.info("source: %s, type: %s, cnt: %s", source, type, cnt)
    save(source, type, 1, date, cnt, 'create')

def alexa_check(source, date):
    cnt = collection_alexa_raw.find({"date": date}).count()
    logger.info("alexa raw: cnt: %s", cnt)
    save(source, source, 1, date, cnt, 'create')
    cnt = collection_alexa.find({"date": date}).count()
    logger.info("alexa parser: cnt: %s", cnt)
    save(source, source, 2, date, cnt, 'create')

def stock_announce_check(source,date):
    collection_announce=None
    if source==13400:
        collection_announce = mongo.stock.neeq_announcement
    elif source==13401:
        collection_announce = mongo.stock.sse_announcement

    if collection_announce is not None:
        cnt = collection_announce.find({"source":source, "createTime": {"$gt":date}}).count()
        logger.info("source: %s, cnt: %s", source, cnt)

def stock_announce_check2(source,date):
    collection_announce=mongo.stock.announcement
    if source==13400:
        se = 1
    elif source==13401:
        se = 2
    else:
        se = 3

    if collection_announce is not None:
        cnt = collection_announce.find({"stockExchangeId":se, "createTime": {"$gt":date}}).count()
        logger.info("source: %s, cnt: %s", source, cnt)

def stock_parser_check(source,date, new=False):
    collection_stock=None
    if source==13400:
        collection_stock = mongo.stock.neeq
    elif source==13401:
        collection_stock = mongo.stock.sse
    elif source==13402:
        collection_stock = mongo.stock.szse
    elif source==13630:
        collection_stock = mongo.amac.manager
    elif source==13631:
        collection_stock = mongo.amac.fund

    if collection_stock is not None:
        if new:
            cnt = collection_stock.find({"source":source, "createTime": {"$gt":date}}).count()
            logger.info("source: %s, cnt: %s, new: %s", source, cnt, new)
            save(source, 36001, 2, date, cnt, 'create')
        else:
            cnt = collection_stock.find({"source": source, "modifyTime": {"$gt":date}, "createTime": {"$lt": date}}).count()
            logger.info("source: %s, cnt: %s, new: %s", source, cnt, new)
            save(source, 36001, 2, date, cnt, 'update')

def stock_status_check(source):
    collection_stock=None
    if source==13400:
        collection_stock = mongo.stock.neeq
    elif source==13401:
        collection_stock = mongo.stock.sse
    elif source==13402:
        collection_stock = mongo.stock.szse

    if source == 13400:
        pps = [0,1,2,3,-1,-2]
    else:
        pps = [0,1,2,3,-1]
    if collection_stock is not None:
        for processStatus in pps:
            cnt = collection_stock.find({"source":source, "processStatus": processStatus}).count()
            logger.info("source: %s, cnt: %s, processStatus: %s", source, cnt, processStatus)

def blockchain_check(source,date, new=False):
    collection_blockchain = mongo.raw.blockchain
    if new:
        cnt = collection_blockchain.find({"source": source, "createTime": {"$gt": date}}).count()
        logger.info("source: %s, cnt: %s, new: %s", source, cnt, new)
        save(source, 36001, 2, date, cnt, 'create')
    else:
        cnt = collection_blockchain.find(
            {"source": source, "modifyTime": {"$gt": date}, "createTime": {"$lt": date}}).count()
        logger.info("source: %s, cnt: %s, new: %s", source, cnt, new)
        save(source, 36001, 2, date, cnt, 'update')


def blockchain_status_check(source):
    collection_blockchain = mongo.raw.blockchain


    pps = [0,1,2]
    if collection_blockchain is not None:
        for processStatus in pps:
            cnt = collection_blockchain.find({"source":13511, "processStatus": processStatus}).count()
            logger.info("source: %s, cnt: %s, processStatus: %s", source, cnt, processStatus)

def mysql_check(source, table, type, date, new= False):
    conn = db.connect_torndb()
    if new:
        sql = "select count(*) from " + table + " where source=%s and createTime>%s"
        cnt = conn.get(sql, source, date)
        save(source, type, 2, date, cnt["count(*)"], 'create')
    else:
        sql = "select count(*) from "+table+" where source=%s and modifyTime>%s and createTime<%s"
        cnt = conn.get(sql, source, date, date)
        save(source, type, 2, date, cnt["count(*)"], 'update')
    logger.info("source: %s, table: %s, cnt: %s, new: %s", source, table, cnt["count(*)"], new)
    conn.close()

def mysql_blockchain_check(source, table, type, date, new= False):
    conn = db.connect_torndb()
    if new:
        sql = "select count(*) from " + table + " where createTime>%s"
        cnt = conn.get(sql, date)
        # save(source, type, 2, date, cnt["count(*)"], 'create')
    else:
        sql = "select count(*) from "+table+" where modifyTime>%s and createTime<%s"
        cnt = conn.get(sql, date, date)
        # save(source, type, 2, date, cnt["count(*)"], 'update')
    logger.info("source: %s, table: %s, cnt: %s, new: %s", source, table, cnt["count(*)"], new)
    conn.close()

def mysql_job_check(source, table, date):
    conn = db.connect_torndb()
    sql = "select count(*) from "+table+" where modifyTime>%s and source=13050"
    cnt = conn.get(sql, date)
    logger.info("table: %s, cnt: %s", table, cnt["count(*)"])
    save(source, 36010, 3, date, cnt["count(*)"], 'update')
    conn.close()

def android_market_check(market,date, new=False):
    if new:
        cnt = collection_android_market.find({"appmarket": market, "createTime": {"$gt": date}}).count()
        save(market, 36100, 1, date, cnt, 'create')
    else:
        cnt = collection_android_market.find({"appmarket": market, "modifyTime": {"$gt":date}, "createTime": {"$lt": date}}).count()
        save(market, 36100, 3, date, cnt, 'update')
    logger.info("appmarket: %s, cnt: %s", market, cnt)

def android_check(date, new=False):
    if new:
        cnt = collection_android.find({"createTime": {"$gt": date}}).count()
        save(13901, 36100, 1, date, cnt, 'create')
    else:
        cnt = collection_android.find({"modifyTime": {"$gt":date}, "createTime": {"$lt": date}}).count()
        save(13901, 36100, 3, date, cnt, 'update')
    logger.info("android all new: %s, cnt: %s", new, cnt)


def appmini_market_check(market,date,new=False):
    if new:
        cnt = collection_appmini_market.find({"source": market, "createTime": {"$gt": date}}).count()
        save(market, 36100, 1, date, cnt, 'create')
    else:
        cnt = collection_appmini_market.find({"source": market, "modifyTime": {"$gt":date}, "createTime": {"$lt": date}}).count()
        save(market, 36100, 3, date, cnt, 'update')
    logger.info("appminimarket: %s, cnt: %s", market, cnt)

def appmini_check(date,new=False):
    if new:
        cnt = collection_appmini.find({"createTime": {"$gt": date}}).count()
        save(13906, 36100, 1, date, cnt, 'create')
    else:
        cnt = collection_appmini.find({"modifyTime": {"$gt":date}, "createTime": {"$lt": date}}).count()
        save(13906, 36100, 3, date, cnt, 'update')
    logger.info("appmini all new: %s, cnt: %s", new, cnt)

def ituns_check(date, new=False):
    if new:
        cnt = collection_itunes.find({"createTime": {"$gt": date}}).count()
        save(13902, 36100, 1, date, cnt, 'create')
    else:
        cnt = collection_itunes.find({"modifyTime": {"$gt": date}, "createTime": {"$lt": date}}).count()
        save(13902, 36100, 3, date, cnt, 'update')
    logger.info("itunes all new: %s, cnt: %s", new, cnt)

def itunes_rank_check(date):
    results = list(appstore_rank_collection.aggregate([{"$match":{"date":date}},{"$group":{"_id":{"type":"$type","genre":"$genre"},"count":{"$sum":1}}}]))
    total = 0
    for result in results:
        logger.info("Itunes rank for type: %s, genre: %s, cnt: %s", result["_id"]["type"], result["_id"]["genre"], result["count"])
        total += result["count"]
    logger.info("Itunes rank for %s categories, total: %s", total, len(results))
    save(13902, 36101, 1, date, total, 'create')

def news_check(source,type,date):
    cnt = collection_news.find({"source":source, "type":type, "createTime": {"$gt":date}}).count()
    save(source, type, 1, date, cnt, 'create')
    logger.info("source: %s:%s,\t type: %s, cnt: %s", source, idmap[source], type, cnt)

def stock_daily_check(date):
    collection_sd = mongo.stock.dailyData
    for se in [2,3]:
        if se == 2:
            source = 13401
        else:
            source = 13402
        for t in [1, 2]:
            cnt = collection_sd.find({"type":t, "stockExchangeId":se, "date":date}).count()
            logger.info("source: %s, type: %s, cnt: %s", source,t, cnt)

def news_total_check(type, date):
    if type > 60100:
        cnt = collection_news.find({"category": type, "createTime": {"$gt": date}}).count()
    elif type == 60000:
        cnt = collection_news.find({"type":{"$ne":61000},"createTime": {"$gt": date}}).count()
    else:
        cnt = collection_news.find({"type": type, "createTime": {"$gt": date}}).count()
    logger.info("source: all, type: %s, cnt: %s", type, cnt)

def talkingdata_check():
    newestDateResults = list(tkdataApp_rank_collection.aggregate([{"$group":{"_id":{"freqId":"$freqId"},"max":{"$max":'$startDate'}}}]))
    total=0
    for newestDateResult in newestDateResults:
        freqId = newestDateResult['_id']['freqId']
        newestDate = newestDateResult['max']
        logger.info('Talkingdata: newestDate of type %s is %s'%(freqId,newestDate))

        results = list(tkdataApp_rank_collection.aggregate([{"$match": {"freqId": freqId,'startDate':newestDate}}, {
            "$group": {"_id": {"freqId": "$freqId"}, "count": {"$sum": 1}}}]))

        cnt=results[0]['count']
        logger.info('Talkingdata for reqId:%s,  cnt: %s' % (freqId,cnt))
        total+=cnt
    logger.info('Talkingdata totally %s'%total)

def feixiaohao_market_check(date):
    cnt = mongo.raw.feixiaohao_market.find({'date': {'$gt': date}}).count()
    logger.info("feixiaohao_market for %s  total: %s", today, cnt)

def website_check(date):
    cnt = collection_website.find({"websiteCheckTime": {"$gt": date}}).count()
    save(13904, 13904, 3, date, cnt, 'update')
    logger.info("website check, cnt: %s", cnt)

def zhihu_check(type,date):
    source = 13610
    cnt = collection_zhihu.find({"source":source, "type":type, "date": {"$gt":date}}).count()
    # save(source, type, 1, date, cnt, 'create')
    logger.info("source: %s:%s,\t type: %s, cnt: %s", source, idmap[source], type, cnt)


def proxy_check(source_domain, date):
    cnt = collection_proxy2.find({"source":source_domain,  "createTime": {"$gt":date}}).count()
    logger.info("source: %s,\t cnt: %s", source_domain,  cnt)

if __name__ == '__main__':
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    logger.info(today)
    strtoday = str(dt.year)+str(dt.month)+str(dt.day)+"000000"
    cnt_proxy = collection_proxy.find({"check_dtime":{"$gt": long(strtoday)}}).count()
    logger.info("Proxy on %s/%s: %s", dt,strtoday, cnt_proxy)
    save(13900,13900,1,today,cnt_proxy,'create')

    proxy_check("kuaidaili.com", today)
    proxy_check("daxiangip.com", today)
    proxy_check("mimvp.com", today)
    logger.info("")

    #alexa check
    alexa_check(13905, today)
    logger.info("")

    #news check
    logger.info("News crawler for %s  ***************************", today)
    news_check(13030, 60001, today)
    news_check(13020, 60001, today)
    news_check(13020, 60002, today)
    news_check(13020, 60003, today)
    news_check(13020, 60006, today)
    news_check(13020, 60008, today)
    news_check(13800, 60001, today)
    news_check(13801, 60001, today)
    news_check(13801, 60003, today)
    news_check(13802, 60002, today)
    news_check(13803, 60001, today)
    news_check(13803, 60003, today)
    news_check(13804, 60002, today)
    news_check(13805, 60003, today)
    news_check(13805, 60006, today)
    news_check(13806, 60001, today)
    news_check(13806, 60008, today)
    news_check(13807, 60001, today)
    news_check(13807, 60003, today)
    news_check(13808, 60003, today)
    news_check(13809, 60001, today)
    news_check(13809, 60003, today)
    news_check(13810, 60001, today)
    news_check(13811, 60001, today)
    news_check(13812, 60001, today)
    news_check(13812, 60003, today)
    news_check(13813, 60001, today)
    news_check(13814, 60001, today)
    news_check(13816, 60001, today)
    news_check(13816, 60003, today)
    news_check(13816, 60008, today)
    news_check(13817, 60001, today)
    news_check(13818, 60001, today)
    news_check(13819, 60001, today)
    news_check(13820, 60001, today)
    news_check(13820, 60003, today)
    news_check(13821, 60001, today)
    news_check(13822, 60001, today)
    news_check(13823, 60001, today)
    news_check(13824, 60005, today)
    news_check(13825, 60005, today)
    news_check(13827, 60005, today)
    news_check(13828, 60001, today)
    news_check(13828, 60003, today)
    news_check(13829, 60001, today)
    news_check(13830, 60001, today)
    news_check(13830, 60003, today)
    news_check(13831, 60001, today)
    news_check(13831, 60003, today)
    news_check(13832, 60001, today)
    news_check(13833, 60001, today)
    news_check(13834, 60001, today)
    news_check(13835, 60006, today)
    news_check(13836, 60006, today)
    news_check(13837, 60001, today)
    news_check(13839, 60001, today)
    news_check(13842, 60001, today)
    news_check(13843, 60001, today)
    news_check(13844, 60001, today)
    news_check(13845, 60001, today)
    news_check(13846, 60005, today)
    news_check(13848, 60005, today)
    news_check(13849, 60001, today)
    news_check(13851, 60001, today)
    news_check(13851, 60008, today)
    news_check(13852, 60001, today)
    news_check(13853, 60001, today)
    news_check(13854, 60001, today)
    news_check(13854, 60005, today)
    news_check(13855, 60001, today)
    news_check(13856, 60005, today)
    news_check(13857, 60001, today)
    news_check(13857, 60005, today)
    news_check(13858, 60005, today)
    news_check(13859, 60005, today)
    news_check(13860, 60001, today)
    news_check(13860, 60008, today)
    news_check(13861, 60001, today)
    news_check(13861, 60005, today)
    news_check(13862, 60001, today)
    news_check(13863, 60001, today)
    news_check(13863, 60005, today)
    news_check(13864, 60001, today)
    news_check(13864, 60005, today)
    news_check(13865, 60005, today)
    news_check(13866, 60005, today)
    news_check(13867, 60001, today)
    news_check(13868, 60001, today)
    news_check(13869, 60001, today)
    news_check(13870, 60001, today)
    news_check(13871, 60001, today)
    news_check(13872, 60001, today)
    news_check(13872, 60008, today)
    news_check(13873, 60005, today)
    news_check(13874, 60005, today)
    news_check(13875, 60005, today)
    news_check(13876, 60005, today)
    news_check(13877, 60005, today)
    news_check(13878, 60001, today)
    news_check(13878, 60005, today)
    news_check(13879, 60001, today)
    news_check(13879, 60010, today)
    news_check(13880, 60001, today)
    news_check(13880, 60010, today)
    news_check(13891, 60001, today)
    news_check(13891, 60010, today)
    news_check(13888, 60005, today)
    news_check(13881, 60004, today)
    news_check(13882, 60004, today)
    news_check(13883, 60004, today)
    news_check(13884, 60004, today)
    news_check(13885, 60004, today)
    news_check(13886, 60004, today)
    news_check(13887, 60004, today)
    news_check(13889, 60004, today)
    news_check(13890, 60004, today)
    news_check(13892, 60004, today)
    news_check(13893, 60004, today)
    news_check(13850, 60009, today)
    news_check(13840, 60001, today)
    news_check(13841, 60001, today)
    news_check(13847, 60005, today)
    news_check(13815, 60004, today)
    news_check(13610, 60005, today)
    news_check(13611, 60007, today)
    news_check(13612, 60007, today)
    news_check(13613, 60007, today)

    logger.info("")
    news_total_check(60001, today)
    news_total_check(60002, today)
    news_total_check(60003, today)
    news_total_check(60004, today)
    news_total_check(60005, today)
    news_total_check(60006, today)
    news_total_check(60007, today)
    news_total_check(60008, today)
    news_total_check(60009, today)
    news_total_check(60010, today)
    news_total_check(60101, today)
    news_total_check(60000, today)
    logger.info("")

    #tianyancha crawler
    logger.info("Tianyancha crawler for %s  ***************************", today)
    projectdata_check(13090, 36008, today)
    logger.info("")

    # tianyancha crawler
    logger.info("liangzi crawler for %s  ***************************", today)
    projectdata_check(13091, 36008, today)
    logger.info("")

    # elements crawler
    logger.info("elements crawler for %s  ***************************", today)
    projectdata_check(13092, 36008, today)
    logger.info("")

    # qixin crawler
    logger.info("qixin crawler for %s  ***************************", today)
    projectdata_check(13093, 36008, today)
    logger.info("")

    # zhigugoguo crawler
    logger.info("zhiguoguo crawler for %s  ***************************", today)
    projectdata_check(13095, 36011, today)
    projectdata_check(13095, 36012, today)
    logger.info("")

    # tianyancha parser
    logger.info("Gongshang parser for %s  ***************************", today)
    gongshang_check(today)
    logger.info("")

    #itjuzi crawler
    #today = datetime.datetime.strptime("2016-06-29", "%Y-%m-%d")
    logger.info("Itjuzi crawler for %s  ***************************", today)
    projectdata_check(13030, 36001, today)
    projectdata_check(13030, 36002, today)
    projectdata_check(13030, 36003, today)
    projectdata_check(13030, 36005, today)
    projectdata_check(13032, 36002, today)
    logger.info("")

    #kr36 crawler
    logger.info("Kr36 crawler for %s  ***************************", today)
    # projectdata_check(13020, 36001, today)
    # projectdata_check(13020, 36003, today)
    projectdata_check(13022, 36001, today)
    logger.info("")

    #lagou crawler
    logger.info("Lagou crawler for %s  ***************************", today)
    projectdata_check(13050, 36001, today)
    # projectdata_check(13050, 36005, today)
    logger.info("")

    logger.info("boss crawler for %s  ***************************", today)
    projectdata_check(13055, 36001, today)
    logger.info("")

    logger.info("liepin crawler for %s  ***************************", today)
    projectdata_check(13056, 36001, today)
    logger.info("")

    logger.info("Crunchbase crawler for %s  ***************************", today)
    projectdata_check(13130, 36001, today)
    logger.info("")

    #Next crawler
    # logger.info("Next crawler for %s  ***************************", today)
    # projectdata_check(13021, 36009, today)
    # projectdata_check(13031, 36009, today)
    # projectdata_check(13111, 36009, today)
    # logger.info("")

    # amac crawler
    logger.info("amac crawler for %s  ***************************", today)
    projectdata_check(13630, 36001, today)
    projectdata_check(13631, 36001, today)
    logger.info("")

    #stock crawler
    logger.info("stock crawler for %s  ***************************", today)
    projectdata_check(13400, 36001, today)
    projectdata_check(13401, 36001, today)
    projectdata_check(13402, 36001, today)
    logger.info("")

    logger.info("stock dailyData for %s  ***************************", today)
    stock_daily_check(today)
    logger.info("")

    # stock crawler
    # logger.info("stock announcement crawler for %s  ***************************", today)
    # stock_announce_check(13400, today)
    # stock_announce_check(13401, today)

    #blockchain crawler
    logger.info("blockchain crawler for %s  ***************************", today)
    blockchain_check(13511, today, new=True)
    blockchain_check(13511, today)
    logger.info("")

    # stock crawler
    logger.info("stock announcement2 crawler for %s  ***************************", today)
    stock_announce_check2(13400, today)
    stock_announce_check2(13401, today)
    stock_announce_check2(13402, today)
    logger.info("")


    # xtecher crawler
    logger.info("xtecher crawler for %s  ***************************", today)
    projectdata_check(13821, 36001, today)
    logger.info("")

    # evervc crawler
    logger.info("evervc crawler for %s  ***************************", today)
    projectdata_check(13838, 36001, today)
    logger.info("")

    #itjuzi parser
    logger.info("Itjuzi parser for %s  ***************************", today)
    mysql_check(13030, "source_company", 36001, today, new=True)
    mysql_check(13030, "source_investor", 36003, today, new=True)
    mysql_check(13030, "source_member", 36005, today, new=True)
    mysql_check(13030, "source_company", 36001, today)
    # mysql_check(13030, "source_investor", today)
    # mysql_check(13030, "source_member", today)
    logger.info("")

    #kr36 parser
    logger.info("Kr36 parser for %s  ***************************", today)
    # mysql_check(13020, "source_company", 36001, today, new=True)
    # mysql_check(13020, "source_investor", 36003, today, new=True)
    # mysql_check(13020, "source_member", 36005, today, new=True)
    mysql_check(13020, "source_company", 36001, today)
    mysql_check(13020, "source_investor", 36003, today)
    mysql_check(13020, "source_member", 36005, today)
    logger.info("")
    mysql_check(13022, "source_company", 36001, today, new=True)
    mysql_check(13022, "source_company", 36001, today)
    logger.info("")

    #lagou parser
    logger.info("Lagou parser for %s  ***************************", today)
    mysql_check(13050, "source_company", 36001, today, new=True)
    mysql_check(13050, "source_member", 36005, today, new=True)
    mysql_check(13050, "source_company", 36001, today)
    logger.info("")

    # crunchbase parser
    logger.info("Crunchbase parser for %s  ***************************", today)
    mysql_check(13130, "source_company", 36001, today, new=True)
    mysql_check(13130, "source_company", 36001, today)
    logger.info("")

    # stock parser
    logger.info("stock parser for %s  ***************************", today)
    stock_parser_check(13400, today, new=True)
    stock_parser_check(13400, today)
    stock_parser_check(13401, today, new=True)
    stock_parser_check(13401, today)
    stock_parser_check(13402, today, new=True)
    stock_parser_check(13402, today)
    logger.info("")

    # amac parser
    logger.info("amac parser for %s  ***************************", today)
    stock_parser_check(13630, today, new=True)
    stock_parser_check(13630, today)
    stock_parser_check(13631, today, new=True)
    stock_parser_check(13631, today)
    logger.info("")


    # xtecher parser
    logger.info("xtecher parser for %s  ***************************", today)
    mysql_check(13821, "source_company", 36001, today, new=True)
    mysql_check(13821, "source_company", 36001, today)
    logger.info("")

    # evervc parser
    logger.info("evervc parser for %s  ***************************", today)
    mysql_check(13838, "source_company", 36001, today, new=True)
    mysql_check(13838, "source_company", 36001, today)
    logger.info("")

    #lagou trend
    logger.info("Lagou trend for %s  ***************************", today)
    mysql_job_check(13050, "job", today)
    logger.info("")

    # lagou trend
    logger.info("Lagou mongo trend for %s  ***************************", today)
    job_check(13050, today, "company")
    job_check(13050, today, "job")
    logger.info("")

    #boss trend
    logger.info("Boss mongo trend for %s  ***************************", today)
    job_check(13055, today, "company")
    job_check(13055, today, "job")
    logger.info("")

    #liepin trend
    logger.info("Liepin mongo trend for %s  ***************************", today)
    job_check(13056, today, "company")
    job_check(13056, today, "job")
    logger.info("")


    # website trend
    logger.info("Website trend for %s  ***************************", today)
    website_check(today)
    logger.info("")

    # zhihu_daily crawler
    logger.info("zhihu_daily crawler for %s  ***************************", today)
    zhihu_check('story', today)
    logger.info("")

    # stock parser
    logger.info("stock status for %s  ***************************", today)
    stock_status_check(13400)
    stock_status_check(13401)
    stock_status_check(13402)
    logger.info("")

    # stock parser
    logger.info("blockchain mongo status for %s  ***************************", today)
    blockchain_status_check(13511)
    logger.info("")

    # stock parser
    logger.info("blockchain mysql status for %s  ***************************", today)
    mysql_blockchain_check(13511, "digital_token", 36001, today, new=True)
    mysql_blockchain_check(13511, "digital_token", 36001, today)
    logger.info("")

    # android market crawler
    logger.info("android app crawler for %s  ***************************", today)
    android_market_check(16010, today, new=True)
    android_market_check(16020, today, new=True)
    android_market_check(16030, today, new=True)
    android_market_check(16040, today, new=True)
    android_market_check(16060, today, new=True)
    android_market_check(16070, today, new=True)
    android_market_check(16090, today, new=True)
    android_check(today, new=True)
    logger.info("")

    #android market trend
    logger.info("android app trend for %s  ***************************", today)
    android_market_check(16010, today)
    android_market_check(16020, today)
    android_market_check(16030, today)
    android_market_check(16040, today)
    android_market_check(16060, today)
    android_market_check(16070, today)
    android_market_check(16090, today)
    android_check(today)
    logger.info("")

    # appmini market ctrawler
    logger.info("appmini app crawler for %s  ***************************", today)
    appmini_market_check(16080, today, new=True)
    appmini_check(today, new=True)
    logger.info("")

    # appmini market trend
    logger.info("miniapp app trend for %s  ***************************", today)
    appmini_market_check(16080, today)
    appmini_check(today)
    logger.info("")

    # itunes market crawler
    logger.info("itunes app crawler for %s  ***************************", today)
    ituns_check(today, new=True)
    logger.info("")

    # itunes market trend
    logger.info("itunes app trend for %s  ***************************", today)
    ituns_check(today)
    logger.info("")

    # itunes rank trend
    logger.info("itunes rank trend for %s  ***************************", today)
    itunes_rank_check(today)
    logger.info("")

    # talkingdata crawler
    logger.info("talkingdata for %s  ***************************", today)
    talkingdata_check()
    logger.info("")

    # feixiaohao_market crawler
    logger.info("feixiaohao_market for %s  ***************************", today)
    feixiaohao_market_check(today)
    logger.info("")




