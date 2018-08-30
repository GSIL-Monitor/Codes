# -*- coding: utf-8 -*-
import os, sys
import datetime, json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import config

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import db

#logger
loghelper.init_logger("fellowPlus_investor_aggregator", stream=True)
logger = loghelper.get_logger("fellowPlus_investor_aggregator")

from pymongo import MongoClient
import gridfs
import pymongo
mongo = db.connect_mongo()
collection_investor = mongo.fellowPlus.investor
collection_field = mongo.fellowPlus.field
collection_org = mongo.fellowPlus.org
imgfs = gridfs.GridFS(mongo.gridfs)

def process():
    users = collection_investor.find({})
    conn = db.connect_torndb()
    for user in users:
        if 'info' in user:
            info = user['info']
            org_item = conn.get('select * from organization where name = %s', info['org_name'])
            if org_item is None:
                insert_sql ="insert organization(name, type, status, grade, createTime, verify, active) values (%s, 17020, 31010, 33020, now(),'N', 'N')"
                org_id = conn.insert(insert_sql, info['org_name'] )
            else:
                org_id = org_item['id']

            user_item = conn.get('select * from user where username = %s', info['name'])
            if user_item is None:
                user_id = conn.insert('insert into user(username, active, createTime, usingStatus)'\
                            ' values(%s, "N", now(), "N")', info['name'] )

                conn.insert('insert into user_organization_rel(organizationId, userId, createTime) '
                            'values(%s, %s, now())', org_id, user_id)
            else:
                user_id = user_item['id']

            user_role = conn.get('select * from user_role where userId = %s limit 1', user_id)
            if user_role is None:
                insert_sql = 'insert user_role(userId, role, createTime) values(%s, %s, now())'
                if u'合伙人' in info['org_position']:
                    conn.insert(insert_sql, user_id, 25030)
                else:
                    conn.insert(insert_sql, user_id, 25040)

    conn.close()


if __name__ == '__main__':
    process()

