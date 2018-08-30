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
    result = conn.query('select distinct(u.id) from deal_note dn '
                        'left join user u on dn.userId = u.id '
                        'where dn.iom = %s and dn.createTime > %s', 'Y', '2016-05-01')
    list = []
    for item in result:
        info = conn.get("select * from user u "
                        "left join user_organization_rel uor on u.id = uor.userId "
                        "left join organization o on o.id = uor.organizationId"
                        " where u.id =%s ", item['id'])
        count = conn.get('select count(*) as count from  deal_note '
                         'where userId=%s and createTime > %s', item['id'], '2016-05-01')

        listItem = UserInfo(info['username'], info['name'], info['email'], count['count'])
        list.append(listItem)

    result = sorted(list, key=getCount, reverse=True)
    id =0
    for item in result:
        id += 1
        print id, item.username, item.orgName, item.email, item.count

    conn.close()

def getCount(user):
    return user.count

if __name__ == '__main__':
    stat()
