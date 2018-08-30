# -*- coding: utf-8 -*-
import os, sys
import pandas as pd

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db
from bson.objectid import ObjectId

# logger
loghelper.init_logger("news_summary", stream=True)
logger = loghelper.get_logger("news_summary")


def get_organizationUsers(organizationIds):
    users = []
    conn = db.connect_torndb()
    for oid in organizationIds:
        # conn = db.connect_torndb()
        uos = conn.query("select * from user_organization_rel where organizationId=%s", oid)
        users.extend([int(uo["userId"]) for uo in uos if uo.has_key("userId") and int(uo["userId"]) not in users])
    conn.close()
    return users


def news_view():
    exids = get_organizationUsers([7, 51, 343])
    pipeline = [
        {"$match": {"visitURL": {'$regex': 'news'}, "userId": {"$nin": exids}}},
        {"$group": {"_id": "$visitURL", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        # {"$group": {"_id":"$count", "count2":{"$sum":1}}}
    ]
    mongo = db.connect_mongo()
    page_view = mongo.log.page_view
    result = list(page_view.aggregate(pipeline))
    mongo.close()

    news_view_dict = {}
    for news in result:
        newsId = news['_id'].split('/')[-1]
        if len(newsId) == 0: continue
        # print news['count'], newsId,news['_id']
        if news_view_dict.has_key(newsId):
            news_view_dict[newsId] = news_view_dict[newsId] + news['count']
        else:
            news_view_dict[newsId] = news['count']

    df = pd.DataFrame(list(news_view_dict.iteritems()), columns=['newsId', 'cnt'])
    # print df.sort('cnt',ascending=0)
    # print df.groupby('cnt').count()
    # print df.values.tolist()
    return df.values.tolist()


def merge_news_detail():
    newsList = news_view()
    file_object = open('news_summary', 'w')
    fileContent = ''
    for news in newsList:
        # print 'before ? ',news[0]
        newsId = news[0].split('?')[0]
        # print newsId
        viewCnt = news[1]
        # if viewCnt>4:
        if viewCnt > 0:
            try:
                obj = ObjectId(newsId)
            except Exception, ex:
                print Exception, ":", ex
                continue
            newsDetail = get_news_detail(newsId)
            # news has been deleted
            if len(newsDetail) == 0: continue
            newsDetail = newsDetail[0]
            title = newsDetail['title']
            link = newsDetail['link']
            date = newsDetail['date'].strftime("%Y-%m-%d %H:%M:%S") if not newsDetail['date'] is None else ''
            newsHref = 'http://www.xiniudata.com/#/news/%s' % newsId

            sector = get_sector_name(newsDetail['sectors'][0]) if newsDetail.has_key('sectors') else ''
            category = str(int(newsDetail['category'])) if newsDetail.has_key('category') and not newsDetail['category'] is None else ''
            type = str(int(newsDetail['type'])) if newsDetail.has_key('type') and not newsDetail['type'] is None else ''

            print '\t'.join([title,str(viewCnt),link,newsHref,date,sector,category])
            fileContent += '\t'.join([title, str(viewCnt), link, newsHref, date, sector, category,type]) + '\n'

    file_object.writelines(fileContent)
    file_object.close()
    print 'done'


def get_news_detail(newsId):
    # newsId = url.split('/')[-1]
    mongo = db.connect_mongo()
    news = mongo.article.news
    result = list(news.find({'_id': ObjectId(newsId)}, {'contents': 0}))
    mongo.close()
    # print result
    return result
    # result['sectors'][0]


def get_sector_name(sectorId):
    conn = db.connect_torndb()
    results = conn.query('''select * from sector where id = %s ''',
                         sectorId)
    conn.close()
    return results[0]['sectorName']


# db.page_view.aggregate({$match:{visitURL:{$regex:'http://www.xiniudata.com/#/news/'}}},{$group: {_id:'$visitURL',cnt:{$sum:1}}},{$match:{cnt:{$gt:10}}})

if __name__ == '__main__':
    # news_view()
    # get_news_detail('5864ad934877af2331987f57')
    # print get_sector_name(20000)
    merge_news_detail()
