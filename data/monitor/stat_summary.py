# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

from time import strftime, localtime
from datetime import timedelta, datetime, date

from bson.code import Code

#logger
loghelper.init_logger("stat_summary", stream=True)
logger = loghelper.get_logger("stat_summary")

#mongo
mongo = db.connect_mongo()
conn_sql = db.connect_torndb()
api_log = mongo.log.api_log
page_view = mongo.log.page_view
stat_page_view_users = mongo.log.stat_page_view_users
stat_page_view_urls = mongo.log.stat_page_view_urls
stat_users_daily = mongo.log.stat_users_daily
stat_visit = mongo.log.stat_visit


def stat_page_view_users_daily():
    startDate = date.today()
    endDate = date.today() + timedelta(days=1)
    start = datetime.now()
    end = datetime.now()
    start = datetime.replace(start, startDate.year, startDate.month, startDate.day, 0, 0, 0, 0)
    end = datetime.replace(start, endDate.year, endDate.month, endDate.day, 0, 0, 0, 0)
    start = start - timedelta(hours=8)
    end = end - timedelta(hours=8)

    pipeline = [
         { "$match":  {"time": {"$gte": start, "$lt": end}} },
 	     { "$group": {"_id":"$userId", "count":{"$sum":1}, "time": {"$max": "$time"}}}
    ]
    result = page_view.aggregate(pipeline)
    count_users = 0
    for item in result:
        count_users += 1
        rule = {'userId': item['_id'], "time": {"$gte": start, "$lt": end}}
        stat_result = stat_page_view_users.find_one(rule)
        insert_item = {'userId': item['_id'],
                       "count": item['count'],
                       "time": start,
                       "updateTime": datetime.now() - timedelta(hours=8)}

        if stat_result is None:
            stat_page_view_users.insert(insert_item)
        else:
            stat_page_view_users.update_one({'_id': stat_result['_id']},  {'$set': insert_item})

    daily_result = stat_users_daily.find_one({"time": {"$gte": start, "$lt": end}})
    insert_item = {"count": count_users,
                   "time": start,
                   "updateTime": datetime.now() - timedelta(hours=8)}
    if daily_result is None:
        stat_users_daily.insert(insert_item)
    else:
        stat_users_daily.update_one({'_id': daily_result['_id']},  {'$set': insert_item})


def stat_page_view_urls_daily():
    startDate = date.today()
    endDate = date.today() + timedelta(days=1)
    start = datetime.now()
    end = datetime.now()
    start = datetime.replace(start, startDate.year, startDate.month, startDate.day, 0, 0, 0, 0)
    end = datetime.replace(start, endDate.year, endDate.month, endDate.day, 0, 0, 0, 0)
    start = start - timedelta(hours=8)
    end = end - timedelta(hours=8)

    pipeline = [
         { "$match":  {"time": {"$gte": start, "$lt": end}} },
 	     { "$group": {"_id":"$visitURL", "count":{"$sum":1}, "time": {"$max": "$time"}}}
    ]
    result = page_view.aggregate(pipeline)
    count_urls = 0
    for item in result:
        count_urls += 1
        rule = {'url': item['_id'], "time": {"$gte": start, "$lt": end}}
        stat_result = stat_page_view_urls.find_one(rule)
        insert_item = {'url': item['_id'],
                       "count": item['count'],
                       "time": start,
                       "updateTime": datetime.now() - timedelta(hours=8)}

        if stat_result is None:
            stat_page_view_urls.insert(insert_item)
        else:
            stat_page_view_urls.update_one({'_id': stat_result['_id']},  {'$set': insert_item})


# 重新修改
def stat_page_view_urls_daily_new():
    startDate = date.today()
    endDate = date.today() + timedelta(days=1)
    start = datetime.now()
    end = datetime.now()
    start = datetime.replace(start, startDate.year, startDate.month, startDate.day, 0, 0, 0, 0)
    end = datetime.replace(start, endDate.year, endDate.month, endDate.day, 0, 0, 0, 0)
    start = start - timedelta(hours=8)
    end = end - timedelta(hours=8)

    rule_all = {"time": {"$gte": start, "$lt": end}}
    result = list(page_view.find(rule_all))

    url_set = set()
    for item in result:
        url_set.add(item['visitURL'])

    for url in url_set:
        count = 0
        count_investorY = 0
        count_investorN = 0
        count_ordinary = 0
        for item in result:
            if url == item['visitURL']:
                userId = item['userId']
                user = get_user(userId)
                if user is None:
                    continue
                count += 1
                userIdentify = user['userIdentify']
                verifiedInvestor = user['verifiedInvestor']
                if userIdentify == 61010:
                   if verifiedInvestor == 'Y':
                       count_investorY += 1
                   else:
                       count_investorN += 1
                else:
                    count_ordinary += 1
        rule = {'url': url, "time": {"$gte": start, "$lt": end}}
        stat_result = stat_page_view_urls.find_one(rule)
        insert_item = {'url': url,
                       "time": start,
                       "count": count,
                       "count_investorY": count_investorY,
                       "count_investorN": count_investorN,
                       "count_ordinary": count_ordinary,
                       "updateTime": datetime.now() - timedelta(hours=8)}
        if stat_result is None:
            stat_page_view_urls.insert(insert_item)
        else:
            stat_page_view_urls.update_one({'_id': stat_result['_id']},  {'$set': insert_item})

def get_user(userId):
    user = conn_sql.get("select u.* from user u left join user_organization_rel uor on u.id=uor.userId "
                 " where userId=%s and uor.organizationId not in (7,5,343)  and (uor.active='Y') limit 1", userId)
    return user

if __name__ == '__main__':
    stat_page_view_users_daily()
    # stat_page_view_urls_daily()
    stat_page_view_urls_daily_new()
