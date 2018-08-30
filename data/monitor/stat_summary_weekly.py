# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db
import pymongo

from time import strftime, localtime
from datetime import timedelta, datetime, date

from bson.code import Code

#logger
loghelper.init_logger("stat_summary_weekly", stream=True)
logger = loghelper.get_logger("stat_summary_weekly")

#mongo
mongo = db.connect_mongo()
api_log = mongo.log.api_log
page_view = mongo.log.page_view
stat_page_view_users = mongo.log.stat_page_view_users
stat_page_view_urls = mongo.log.stat_page_view_urls
stat_users_daily = mongo.log.stat_users_daily

stat_page_view_users_weekly = mongo.log.stat_page_view_users_weekly
stat_users_weekly = mongo.log.stat_users_weekly


def stat_page_view_users():
    # stat_page_view_users_weekly.remove({})

    startDate = date.today() - timedelta(days=6)
    endDate = date.today()+timedelta(days=1)
    start = datetime.now()
    end = datetime.now()
    start = datetime.replace(start, startDate.year, startDate.month, startDate.day, 0, 0, 0, 0)
    end = datetime.replace(start, endDate.year, endDate.month, endDate.day, 0, 0, 0, 0)
    # start = datetime.replace(start, 2018, 1, 8, 0, 0, 0, 0)
    # end = datetime.replace(start, 2018, 1, 14, 0, 0, 0, 0)
    start = start - timedelta(hours=8)
    end = end - timedelta(hours=8)

    pipeline = [
         { "$match":  {"time": {"$gte": start, "$lt": end}} },
 	     { "$group": {"_id":"$userId", "count":{"$sum":1}, "time": {"$max": "$time"}}}
    ]
    # print pipeline
    result = page_view.aggregate(pipeline)
    count_users = 0
    for item in result:
        # print item
        count_users += 1
        rule = {'userId': item['_id'], "time": {"$gte": start, "$lt": end}}
        insert_item = {'userId': item['_id'],
                       "count": item['count'],
                       "time": start,
                       "updateTime": datetime.now() - timedelta(hours=8)}

        stat_result = stat_page_view_users_weekly.find_one(rule)
        if stat_result is None:
            stat_page_view_users_weekly.insert(insert_item)
        else:
            stat_page_view_users_weekly.update_one({'_id': stat_result['_id']},  {'$set': insert_item})

    daily_result = stat_users_weekly.find_one({"time": {"$gte": start, "$lt": end}})
    insert_item = {"count": count_users,
                   "time": start,
                   "updateTime": datetime.now() - timedelta(hours=8)}
    if daily_result is None:
        stat_users_weekly.insert(insert_item)
    else:
        stat_users_weekly.update_one({'_id': daily_result['_id']},  {'$set': insert_item})

    conn = db.connect_torndb()
    result = stat_page_view_users_weekly.find().sort("count", pymongo.DESCENDING)
    id = 0
    for item in result:
        id += 1
        info = conn.get("select * from user u "
                        "left join user_organization_rel uor on u.id = uor.userId "
                        "left join organization o on o.id = uor.organizationId"
                        " where u.id =%s limit 1", item['userId'])
        if info is not None:
            print id, info['username'], info['name'], info['email'], item['count']
        info = None

    conn.close()

if __name__ == '__main__':
    stat_page_view_users()
