# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil

import codecs


def assign2col(uid, colid, cids):

    db = dbcon.connect_torndb()
    dbutil.update_collection_user(db, colid, uid)
    for cid in cids:
        dbutil.update_collection(db, colid, cid)
    db.close()


def assign_verify(file):

    db = dbcon.connect_torndb()
    waits = [int(line.strip()) for line in open(file)]
    uids = [c.userId for c in db.query('select userId from user_organization_rel where organizationId=51;')]
    colids = []
    for uid in uids:
        colid = db.execute('insert into collection (name, type, active) '
                           'values (%s, 39030, "Y");', 'desc2check_%s' % uid)
        print colid
        colids.append(colid)
    for index, cid in enumerate(waits):
        i = index % len(uids)
        assign2col(uids[i], colids[i], [cid])
    db.close()


def resign():

    db = dbcon.connect_torndb()
    waits = [c.companyId for c in db.query('select companyId from collection_company_rel '
                                           'where collectionId in (1638)')]
    uids = [c.userId for c in db.query('select userId from user_organization_rel where organizationId=51;')]
    uids = [uid for uid in uids if uid not in (222, 223, 224, 1077)]
    colids = []
    for uid in uids:
        colid = db.get('select id from collection where name=%s;', 'website2check_%s' % uid).id
        print colid
        colids.append(colid)
    for index, cid in enumerate(waits):
        i = index % len(uids)
        assign2col(uids[i], colids[i], [cid])
    db.close()


def assign_investor():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    start, end = 31, 72
    iids = [line.strip().split('\t')[1] for line in
            codecs.open('template/collection.task', encoding='utf-8')][start-1: end]
    print 'iids', iids

    uids = [c.userId for c in db.query('select userId from user_organization_rel where organizationId=51;')]
    colids = []
    for uid in uids:
        # colid = db.execute('insert into collection (name, type, active) '
        #                    'values (%s, 39030, "Y");', 'investor2check_w1_%s' % uid)
        colid = db.get('select id from collection where name=%s;', 'investor2check_w1_%s' % uid).id
        colids.append(colid)

    # done = set(int(line.strip()) for line in open('template/collection.investor.done'))
    donecolids = [col.id for col in db.query('select id from collection where name like "investor2check_%%";')]
    done = set(c.companyId for c in db.query('select distinct companyId from collection_company_rel '
                                             'where collectionId in %s;', donecolids))
    print 'done', len(done)

    waits = [item.cid for item in db.query('select distinct companyId cid from audit_investor_company '
                                           'where investorId in %s and companyId is not null', iids)
             if (item.cid not in done)]
    waits = [cid for cid in waits if not __dup_gongshang(db, mongo, cid)]
    print 'waits', len(waits)
    for index, cid in enumerate(waits):
        i = index % len(uids)
        assign2col(uids[i], colids[i], [cid])
    db.close()


def dump():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    uids = [c.userId for c in db.query('select userId from user_organization_rel where organizationId=51;')]
    colids = []
    for uid in uids:
        colid = db.get('select id from collection where name=%s', 'investor2check_%s' % uid).id
        colids.append(colid)

    daichuli = 1783
    for colid in colids:
        cids = [c.cid for c in db.query('select companyId cid from collection_company_rel '
                                        'where collectionId=%s', colid)]
        for cid in cids:
            alias = [item.name for item in db.query('select * from company_alias '
                                                    'where companyId=%s and type=12010 '
                                                    'and (active is null or active="Y");', cid)]
            if len(list(mongo.info.gongshang.find({'name': {'$in': alias}}))) > 1:
                db.execute('delete from collection_company_rel where collectionId=%s and companyId=%s', colid, cid)
                dbutil.update_collection(db, daichuli, cid)
    db.close()


def __dup_gongshang(db, mongo, cid):

    alias = [item.name for item in db.query('select * from company_alias '
                                            'where companyId=%s and type=12010 '
                                            'and (active is null or active="Y");', cid)]
    return len(list(mongo.info.gongshang.find({'name': {'$in': alias}}))) > 1

if __name__ == '__main__':

    print __file__
    # dump()
    db = dbcon.connect_torndb()
    uids = [c.userId for c in db.query('select userId from user_organization_rel where organizationId=51;')]
    uids = [uid for uid in uids]
    for uid in uids:
        colid = db.get('select id from collection where name=%s;', 'investor2check_w1_%s' % uid).id
        dbutil.update_collection_user(db, colid, 1091)
    db.close()
    # 汪甜 1091
    # assign_investor()
    # resign()
    # assign_verify('files/20170210.cids')