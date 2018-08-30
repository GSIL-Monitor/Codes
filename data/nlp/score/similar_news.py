# -*- encoding=utf-8 -*-

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common.algorithm import edit_distance

import datetime
import simhash
from bson import ObjectId


class ScorerNews(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.collection = self.mongo.article.news

    def get_similar_news(self, newsId):

        original_news = self.collection.find_one({'_id': newsId})
        candidates = list(self.collection.find({'type': 60001, "simhashValue": {'$exists': True},
                                                "date": {'$gt': original_news['date'] - datetime.timedelta(days=3)}},
                                               {'title': 1, 'companyIds': 1, 'simhashValue': 1}))
        results = []
        for news in candidates:
            if news['_id'] == original_news['_id']:
                continue
            # from title comparation
            title_source, title_candidate = original_news.get('title', ''), news.get('title', '')
            edit = float(edit_distance(title_source, title_candidate, (1, 1, 3)))
            if edit / len(set(title_source) | set(title_candidate)) < 0.3:
                # print news['_id'], edit / len(set(title_source) | set(title_candidate))
                results.append(news['_id'])
                continue
            # from content comparation
            # simhash1 = simhash.Simhash(news['simhashValue'])
            # simhash2 = simhash.Simhash(original_news['simhashValue'])
            # distance = simhash1.distance(simhash2)
            # if distance <= 1:
            #     # relevant_news['distance'] = distance
            #     # relevant_news['newsId'] = news['_id']
            #     results.append(news['_id'])
        return results

    def get_distance(self, newsId1, newsId2):
        news1 = self.collection.find_one({'_id': newsId1})
        news2 = self.collection.find_one({'_id': newsId2})

        def get_simhash_value(contents):
            main = ""
            for content in contents:
                if content["content"].strip() != "":
                    main = main + content["content"]
            a = simhash.Simhash(simhash.get_features(main))
            # logger.info("*****%s", a.value)
            return str(a.value)

        # logger.info('sim1:%s | sim2:%s',get_simhash_value(news1['contents']),get_simhash_value(news2['contents']))

        simhash1 = simhash.Simhash(get_simhash_value(news1['contents']))
        simhash2 = simhash.Simhash(get_simhash_value(news2['contents']))
        distance = simhash1.distance(simhash2)
        return distance


if __name__ == '__main__':

    scorerNews = ScorerNews()
    if len(sys.argv) > 1:
        param = sys.argv[1]
    else:
        param = '59bf3fa3deb471157879bebb'
    print scorerNews.get_similar_news(ObjectId(param))
