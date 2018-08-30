# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
import config as tsbconfig
from common import dbutil, dicts

from bson.objectid import ObjectId


def modify_5001():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    for cm in db.query('select * from company_message where trackDimension=5001;'):
        print cm.id
        record = list(mongo.info.gongshang.find({'_id': ObjectId(cm.relateId)}))[0]
        change = [item for item in record.get('changeInfo', []) if int(item.get('id')) == int(cm.detailId)][0]
        holder_change = []
        if change.get('diffAfter', []):
            holder_change.append(u'增加了%s' % ', '.join(change.get('diffAfter', [])))
        if change.get('diffBefore', []):
            holder_change.append(u'减少了%s' % ', '.join(change.get('diffBefore', [])))
        if holder_change:
            msg = ', '.join(holder_change)
        else:
            msg = ''
        db.execute('update company_message set message=%s where id=%s;', msg, cm.id)


def modify_5002():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    for cm in db.query('select * from company_message where trackDimension=5002;'):
        record = list(mongo.info.gongshang.find({'_id': ObjectId(cm.relateId)}))[0]
        change = [item for item in record.get('changeInfo', []) if int(item.get('id')) == int(cm.detailId)][0]
        try:
            msg = u'由%s万元变更为%s万元' % \
                  (int(float(change.get('contentBefore', ''))), int(float(change.get('contentAfter', ''))))
        except:
            print 'fail', cm.id
            msg = u'由%s万元变更为%s万元' % (change.get('contentBefore', ''), change.get('contentAfter', ''))
        db.execute('update company_message set message=%s where id=%s;', msg, cm.id)


def modify_8001():

    db = dbcon.connect_torndb()
    for tpm in db.query('select * from topic_message where relateType=80;'):
        fa = dbutil.get_company_latest_fa(db, tpm.detailId)
        if fa:
            db.execute('update topic_message set relateId=%s where id=%s;', fa, tpm.id)


if __name__ == '__main__':

    print __file__
    modify_8001()
    # modify_5001()
    # modify_5002()