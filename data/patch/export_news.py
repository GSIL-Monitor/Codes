# -*- coding: utf-8 -*-
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

def main():
    mongo = db.connect_mongo()
    tasks = mongo.article.task_news.find()
    for task in tasks:
        news = mongo.article.news.find_one({"_id":task["news_id"]})
        mongo.article.news_temp.insert(news)
    mongo.close()

if __name__ == "__main__":
    main()
