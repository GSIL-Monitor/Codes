# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from common.mail import send_mail

import time


def deliver_push():

    receivers = ['victor@xiniudata.com']
    subject = u'推送情况总结 %s年%s月%s日' % (time.localtime()[:3])

    db = dbcon.connect_torndb()
    results = []
    for oid in dbutil.get_all_organizations(db):
        volumn, zero, assigned, scored, cared = 0, 0, 0, 0, 0
        for uid in dbutil.get_organization_watcher_users(db, oid):
            uvol = dbutil.get_user_task_volumn(db, uid)
            zero += 1 if uvol == 0 else 0
            volumn += uvol
            dids = [x.dealId for x in db.query('select dealId from deal_user_rel where userId=%s and type=23030 and '
                                               'createTime>date_add(curdate(), interval -7 day);')]
            assigned += len(dids)

    db.close()