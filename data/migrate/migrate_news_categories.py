# -*- coding: utf-8 -*-
import os, sys
from bson.objectid import ObjectId

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("migrate_news_categories", stream=True)
logger = loghelper.get_logger("migrate_news_categories")

# task.news categories 两个删除的标签迁移
# article.news.categories还原
mongo = db.connect_mongo()

def main():
    # step1()
    # step2()
    step3()

def step1():
    REPLACEMENT = [
        # 汇总性新闻->其他新闻类型
        (578358, 578359),
        # 竞争格局->行业研究
        (578355, 578356)
    ]
    for old_tag_id, new_tag_id in REPLACEMENT:
        items = list(mongo.task.news.find({"categories": old_tag_id}))
        for item in items:
            logger.info("%s, %s", item["_id"], item["categories"])
            if new_tag_id not in item["categories"]:
                mongo.task.news.update({"_id":item["_id"]},{"$addToSet":{"categories": new_tag_id}})
                #exit()
            mongo.task.news.update({"_id":item["_id"]},{"$pull":{"categories": old_tag_id}})
            # exit()


def step3():
    REPLACEMENT = [
        # 汇总性新闻->其他新闻类型
        (578358, 578359),
        # 竞争格局->行业研究
        (578355, 578356),
        # 电子商务->消费
        (8,758),
        # 游戏->文化娱乐
        (40,1713),
        # 广告营销->企业服务
        (133,81),
        # 招聘->企业服务
        (578,81)
    ]
    for old_tag_id, new_tag_id in REPLACEMENT:
        items = list(mongo.article.news.find({"features": old_tag_id}))
        for item in items:
            logger.info("%s, %s", item["_id"], item["features"])
            if new_tag_id not in item["features"]:
                mongo.article.news.update({"_id": item["_id"]}, {"$addToSet": {"features": new_tag_id}})
            mongo.article.news.update({"_id": item["_id"]}, {"$pull": {"features": old_tag_id}})
            # exit()


def step2():
    item = mongo.task.news.find_one({},limit=1,sort=[("_id", 1)])
    _id = item["_id"]
    dup(item)
    #logger.info("_id: %s", _id)

    cnt = 0
    while True:
        items = list(mongo.task.news.find({"_id":{"$gt": _id}},limit=100,sort=[("_id", 1)]))
        if len(items) == 0:
            break
        for item in items:
            _id = item["_id"]
            # logger.info("%s", _id)
            dup(item)
            cnt += 1
    logger.info("total: %s", cnt)


def dup(item):
    if item.get("news_id") is None:
        return

    news_id = item["news_id"]
    logger.info("newsId: %s", news_id)
    # news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
    # if news is not None:
    #     logger.info(news["title"])
    if item.get("section") is None:
        mongo.task.news.update({"_id": item["_id"]}, {"$set":{"section": "step1"}})

    if item.get("categories") is None:
        mongo.article.news.update({"_id": ObjectId(news_id)}, {"$set": {"categories": []}})
    else:
        mongo.article.news.update({"_id": ObjectId(news_id)}, {"$set":{"categories":item["categories"]}})
    # exit()


if __name__ == '__main__':
    main()