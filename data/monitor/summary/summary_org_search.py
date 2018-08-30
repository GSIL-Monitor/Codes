# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
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

def get_searches(organizationIds):
    users = []
    conn = db.connect_torndb()
    for oid in organizationIds:
        users = conn.query("select u.* from user u left join user_organization_rel uor on "
                          "u.id = uor.userId where organizationId=%s ", oid)
        filename = 'org_searches_%s' % oid
        if os.path.exists(filename):
            os.remove(filename)
        print filename
        file_object = open(filename, 'w')
        fileContent = ''
        for user in users:
            print user['id'], user['username']
            items = api_log.find({'requestURL': '/api/search/general', 'userId': user['id']})
            for item in items:
                d = item['data']
                username = user['username']
                input = d['input']
                if len(input) > 0:
                    fileContent += '姓名：%s, time: %s, search: %s' % (username, item['time'], input)
                    fileContent+= '\n'
        file_object.writelines(fileContent)
        file_object.close()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) > 0:
        print '请输入机构ID'

    list = []
    for id in sys.argv:
        list.append(id)
    get_searches(list)
