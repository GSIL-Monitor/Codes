# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
# import loghelper
import db

from time import strftime, localtime
from datetime import timedelta, datetime, date

from bson.code import Code

#logger
# loghelper.init_logger("stat_person_summary", stream=True)
# logger = loghelper.get_logger("stat_person_summary")

#mongo
mongo = db.connect_mongo()
conn_sql = db.connect_torndb()
# source table
user_log = mongo.log.user_log
# 每日用户统计
stat_person_daily_users = mongo.log.stat_person_daily_users

stat_person_daily = mongo.log.stat_person_daily

EXCLUDE_IP = "116.226.185.172"

def stat_person_users_daily():
    startDate = date.today()
    endDate = date.today() + timedelta(days=1)
    start = datetime.now()
    end = datetime.now()
    start = datetime.replace(start, startDate.year, startDate.month, startDate.day, 0, 0, 0, 0)
    end = datetime.replace(start, endDate.year, endDate.month, endDate.day, 0, 0, 0, 0)
    start = start - timedelta(hours=8)
    end = end - timedelta(hours=8)

    pipeline = [
         { "$match":  {"userId": {"$exists": True}, "url_type": "front", "time": {"$gte": start, "$lt": end}}},
 	     { "$group": {"_id": "$userId", "count":{"$sum": 1}, "time": {"$max": "$time"}}}
    ]

    pipeline_cookie = [
         { "$match":  {"ip": {"$ne": EXCLUDE_IP}, "userId": {"$exists": False}, "url_type": "front", "time": {"$gte": start, "$lt": end}}},
 	     { "$group": { "_id": "$userCookie", "count":{"$sum": 1}, "time": {"$max": "$time"}}}
    ]
    result = user_log.aggregate(pipeline)
    result_cookie = user_log.aggregate(pipeline_cookie)
    count_users = 0
    for item in result:
        count_users += 1
        rule = {'userId': item['_id'], "time": {"$gte": start, "$lt": end}}
        stat_result = stat_person_daily_users.find_one(rule)
        insert_item = {'userId': item['_id'],
                       "count": item['count'],
                       "time": start,
                       "type": "user",
                       "updateTime": datetime.now() - timedelta(hours=8)}

        if stat_result is None:
            stat_person_daily_users.insert(insert_item)
        else:
            stat_person_daily_users.update_one({'_id': stat_result['_id']},  {'$set': insert_item})

    for item in result_cookie:
        count_users += 1
        rule = {'userId': item['_id'], "time": {"$gte": start, "$lt": end}}
        stat_result = stat_person_daily_users.find_one(rule)
        insert_item = {'userId': item['_id'],
                       "count": item['count'],
                       "time": start,
                       "type": "cookie",
                       "updateTime": datetime.now() - timedelta(hours=8)}

        if stat_result is None:
            stat_person_daily_users.insert(insert_item)
        else:
            stat_person_daily_users.update_one({'_id': stat_result['_id']},  {'$set': insert_item})



    daily_result = stat_person_daily.find_one({"time": {"$gte": start, "$lt": end}})
    insert_item = {"count": count_users,
                   "time": start,
                   "updateTime": datetime.now() - timedelta(hours=8)}
    if daily_result is None:
        stat_person_daily.insert(insert_item)
    else:
        stat_person_daily.update_one({'_id': daily_result['_id']},  {'$set': insert_item})





if __name__ == '__main__':
    stat_person_users_daily()
