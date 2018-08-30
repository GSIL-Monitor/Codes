# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
from pypinyin import pinyin, Style

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_industry", stream=True)
logger = loghelper.get_logger("migrate_industry")

conn = db.connect_torndb()
mongo = db.connect_mongo()


def migrate_comps():
    items = conn.query("select * from comps where active is null or active !='N' order by id")
    for item in items:
        name = "[comps]%s" % item["name"]
        logger.info(name)
        industry_id = gen_industry(name)
        rels = conn.query("select * from comps_company_rel where compsId=%s order by sort,id", item["id"])
        for rel in rels:
            gen_industry_company(industry_id, rel["companyId"])
            gen_industry_company_news(industry_id, rel["companyId"])
        # exit(0)

def migrate_collection():
    collections = conn.query("select id,name from collection where type!=39030 and subtype=39110 order by id")
    for collection in collections:
        if collection["id"] in [20,21,157,409,844,1906,2697]:
            continue
        name = "[collection]%s" % collection["name"]
        logger.info(name)
        industry_id = gen_industry(name)
        rels = conn.query("select * from collection_company_rel where collectionId=%s "
                          "and (active is null or active='Y') "
                          "order by sort, id",
                          collection["id"])
        for rel in rels:
            gen_industry_company(industry_id, rel["companyId"])
            gen_industry_company_news(industry_id, rel["companyId"])
        # exit(0)


def migrate_topic():
    topics = [
        ("热门行业 - 便利店",       47),
        ("热门行业 - 迷你健身仓",    51),
        ("行业动向 - S2b",          53),
        ("热门行业 - 充电宝租赁",    23),
        ("热门行业 - 共享单车",     40),
        ("热门行业 - 直播平台",     41),
        ("共享电动车",              24),
        ("热门行业 - 教育",         48),
        ("热门行业 - 电竞",         50),
        # ("行业新动态 - Web3.0",     54),
        ("热门行业 - 短视频",      56),
        # ("超级物流枢纽",          58),
        ("行业动向 - PPP",          60),
        # ("行业趋势 - 量子计算",     64),
        # ("EWTP",                  67),
        ("出海专辑",                74),
        ("逆天的无人零售",         75),
        ("情绪营销",                76),
        ("行业发现 - 粉红经济",     82),
        ("走近科学 - 风水占卜星座学", 62),
        ("共享经济 - 共享雨伞",      79),
        ("消费升级 - 个护美妆新时代", 80),
        ("热门行业 - 智能医疗",       57),
        ("量子计算",                63),
        ("汽车出行 - 电瓶车充电",    77),
        ("汽车出行 - 新车电商B2B平台", 78),
        ("测试 - 婚恋社交",          81),
        ("人工智能 - 智能助理",      83),
        ("人工智能 - 深度学习",      85),
        ("无人零售 - 自助贩卖机",    101),
        ("无人零售 - 办公室货柜",    106),
        ("无人零售 - 无人便利店",    109),
        ("智能安防",                105),
        ("智慧物流",                107),
        ("智能包装",                108),
        ("冷链物流",                110),
        ("智能零售系统",            100),
        ("掌纹识别",                102),
        ("人脸识别",                104),
        ("虹膜识别",                111),
        ("零售大数据",               98),
        ("智能仓储机器人",           95),
        ("无人零售技术支持 - RFID",  97),
        ("无人自助结算",            86)
    ]

    for _,topic_id in topics:
        topic = conn.get("select * from topic where id=%s", topic_id)
        if topic is None:
            continue
        name = "[topic]%s" % topic["name"]
        logger.info(name)
        industry_id = gen_industry(name, logo=topic["logo"], background=topic["background"], description=topic["description"])
        rels = conn.query("select * from topic_company where topicId=%s "
                          "and (active is null or active='Y') "
                          "order by id",
                          topic_id)
        for rel in rels:
            gen_industry_company(industry_id, rel["companyId"])
            gen_industry_company_news(industry_id, rel["companyId"])

        rels = conn.query("select * from topic_message where topicId=%s "
                          "and (active is null or active='Y') "
                          "and relateType=10 "
                          "order by id", topic_id)
        for rel in rels:
            gen_industry_news(industry_id, ObjectId(rel["relateId"]))
        # exit(0)


def gen_industry(name, logo=None, background=None, description=None):
    industry = conn.get("select * from industry where name=%s", name)
    if industry is not None:
        industry_id = industry["id"]
    else:
        industry_id = conn.insert("insert industry(name,logo,background,description,createTime,modifyTime) "
                                  "values(%s,%s,%s,%s,now(),now())",
                                  name, logo, background, description)
    return industry_id


def gen_industry_company(industry_id, company_id):
    rel = conn.get("select * from industry_company where industryId=%s and companyId=%s",
                   industry_id, company_id)
    if rel is None:
        conn.insert("insert industry_company(industryId, companyId, createTime,modifyTime, active) "
                    "values(%s,%s,now(),now(),'Y')",
                    industry_id, company_id)


def gen_industry_company_news(industry_id, company_id):
    items = mongo.article.news.find({"companyIds":company_id, "processStatus":1 , "type":{"$ne":61000}})
    for news in items:
        logger.info("newsId: %s", news["_id"])
        gen_industry_news(industry_id, news["_id"])


def gen_industry_news(industry_id, news_id):
    news = mongo.article.news.find_one({"_id": news_id})
    if news is None:
        return
    rel = conn.get("select * from industry_news where industryId=%s and newsId=%s",
                   industry_id, str(news_id))
    if rel is not None:
        if rel["active"] == 'P':
            logger.info("P")
            conn.update("update industry_news set active='Y' where id=%s", rel["id"])
        return
    news_date = news["date"]
    if news_date is None:
        return

    # logger.info("%s", type(news_date))
    if type(news_date) == float:
        news_date = datetime.datetime.fromtimestamp(news_date/1000)
        if news_date.year > 2017 or news_date.year < 2000:
            logger.info("Wrong date: %s, newsId: %s", news_date, news_id)
            exit(0)

    news_date += datetime.timedelta(hours=8)
    industry_news_id = conn.insert("insert industry_news(industryId,newsId,newsTime, createTime,modifyTime,active) "
                                   "values(%s,%s,%s,now(),now(),'Y')",
                                   industry_id, str(news_id), news_date)
    features = news.get("features")
    if features is not None:
        for tag_id in features:
            rel = conn.get("select * from industry_news_tag_rel where industryNewsId=%s and tagId=%s",
                           industry_news_id, tag_id)
            if rel is None:
                conn.insert("insert industry_news_tag_rel(industryNewsId,tagId,createTime,modifyTime) "
                            "values(%s,%s,now(),now())",
                            industry_news_id, tag_id)


def patch_first_letter():
    industries = conn.query("select * from industry where firstLetter is null or firstLetter=''")
    for industry in industries:
        name = industry["name"].replace('[comps]','').replace('[collection]','').replace('[topic]','')
        py = pinyin(name, style=Style.FIRST_LETTER)
        first_letter = py[0][0][0].upper()
        logger.info("%s - %s", first_letter, name)
        conn.update("update industry set firstLetter=%s where id=%s", first_letter, industry["id"])


def patch_industry_news():
    items = conn.query("select * from industry_news where newsTime is null")
    for item in items:
        news = mongo.article.news.find_one({"_id": ObjectId(item["newsId"])})
        if news is not None:
            logger.info(item["newsId"])
            news_date = news.get("date")
            if news_date is None:
                continue
            logger.info(type(news_date))
            if type(news_date) == float:
                news_date = datetime.datetime.fromtimestamp(news_date / 1000)
                if news_date.year > 2017 or news_date.year < 2000:
                    logger.info("Wrong date: %s, newsId: %s", news_date, item["newsId"])
                    exit(0)
            elif type(news_date) == unicode:
                continue
            news_date += datetime.timedelta(hours=8)
            conn.update("update industry_news set newsTime=%s where id=%s", news_date, item["id"])


def patch_industry_news2():
    industries = conn.query("select * from industry")
    for industry in industries:
        logger.info("%s", industry["name"])
        patch_news(industry["id"])


def patch_news(industry_id):
    rels = conn.query("select * from industry_company where active='Y' and industryId=%s", industry_id)
    for rel in rels:
        logger.info("companyId: %s", rel["companyId"])
        gen_industry_company_news(industry_id, rel["companyId"])


if __name__ == '__main__':
    # migrate_comps()
    # migrate_collection()
    # migrate_topic()
    patch_first_letter()
    # patch_industry_news()
    # patch_industry_news2()
    #patch_news(260)