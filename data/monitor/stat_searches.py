# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db
import json

from time import strftime, localtime
from datetime import timedelta, datetime, date

from bson.code import Code

#logger
loghelper.init_logger("stat_summary", stream=True)
logger = loghelper.get_logger("stat_summary")

#mongo
mongo = db.connect_mongo()
api_log = mongo.log.api_log
page_view = mongo.log.page_view
stat_page_view_users = mongo.log.stat_page_view_users
stat_page_view_urls = mongo.log.stat_page_view_urls
stat_users_daily = mongo.log.stat_users_daily

def get_organizationUsers(organizationIds):
    users = []
    conn = db.connect_torndb()
    for oid in organizationIds:
    # conn = db.connect_torndb()
        uos = conn.query("select * from user_organization_rel where organizationId=%s", oid)
        users.extend([int(uo["userId"]) for uo in uos if uo.has_key("userId") and int(uo["userId"]) not in users])
    conn.close()
    return users

def stat_page_view_searches():
    exids = get_organizationUsers([7,51,343])
    pipeline = [
         { "$match":  {"router": "search", "userId": {"$nin": exids}} },
 	     { "$group": {"_id":"$visitURL", "count":{"$sum":1}}},
         {"$sort": {"count": -1}}
    ]
    result = list(page_view.aggregate(pipeline))
    count_users = 0
    file_object = open('stat_searches', 'w')
    fileContent = ''
    id = 0
    for item in result:
        id +=1
        if item["count"]>1:
            uus = []
            logs = list(page_view.find({"visitURL": item["_id"], "userId":{"$nin": exids}}))
            uus.extend([int(log["userId"]) for log in logs if log.has_key("userId") and log["userId"] is not None and int(log["userId"]) not in uus ])
        print item['_id']

        fileContent += str(id)+'  count: '+ str(item['count'])+ ',   search: '+ item['_id']+ '\n'
    logger.info(len(result))
    file_object.writelines(fileContent)
    file_object.close()



if __name__ == '__main__':
    stat_page_view_searches()
