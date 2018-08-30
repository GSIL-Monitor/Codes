# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import datetime, time
import json, re, copy

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

# logger
loghelper.init_logger("modify_locationId", stream=True)
logger = loghelper.get_logger("modify_locationId")


def modify_corporate_locationId():
    sql = '''update corporate set locationId=%s'''
    conn.update


def location_patch():
    conn = db.connect_torndb()
    mongo = db.connect_mongo()

    sql = ''' select c.corporateid,c.id,c.code,c.name,c.locationId,co.locationId,co.fullName
    from company c join corporate co 
    on co.id=c.corporateid
    where (c.active!='N' or c.active is null)
    and (co.active!='N' or co.active is null)
    and  co.locationId!=c.locationId and co.locationId>0 and c.locationId>0
    '''
    results = conn.query(sql)
    cnt = 0
    for i in results:
        if len(conn.query('''select * from company where corporateid=%s and (active!='N' or active is null)''',
                          i['corporateid'])) > 1:
            logger.info('multi companies coid:%s', i['corporateid'])
            continue

        if mongo.info.gongshang.find_one({'name': i['fullName']}) is not None:
            logger.info('can do coid:%s|%s', i['corporateid'],i['name'])
            cnt += 1

            # conn.update('''update corporate set locationId = null where id=%s''', i['corporateid'])

    print cnt
