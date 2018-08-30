# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db
from UserInfo import UserInfo

#logger
loghelper.init_logger("stat_using_iom_users", stream=True)
logger = loghelper.get_logger("stat_using_iom_users")

#mongo
mongo = db.connect_mongo()
api_log = mongo.log.api_log
page_view = mongo.log.page_view
stat_using_iom_users = mongo.log.stat_using_iom_users

def stat():
    conn = db.connect_torndb()
    result = conn.query("select * from user u "
                    "left join user_organization_rel uor on u.id = uor.userId "
                    "left join organization o on o.id = uor.organizationId"
                    " where u.loginIp is null and (u.active is null or u.active = %s )"
                    " and o.name is not null", 'Y')
    id =0
    for item in result:
        id += 1
        print id, item['username'], item['name'], item['email'], item['createTime']

    conn.close()

def getCount(user):
    return user.count

if __name__ == '__main__':
    stat()
