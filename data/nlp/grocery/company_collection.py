# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
import time

import db as dbcon
from common import dbutil


def update_list(listname, colid):

    db = dbcon.connect_torndb()
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'template/%s' % listname)
    cids = [line.strip() for line in codecs.open(path, encoding='utf-8')]
    cids.reverse()
    for line in cids:
        # code, sortv = line.split('#')[0], round(float(line.split('#')[2]), 2)
        cid = line.strip()
        # try:
        #     cid = db.get('select id from company where code=%s', code).id
        #     # cid = db.get('select id from company where id=%s;', code).id
        # except Exception, e:
        #     print code, e
        #     continue
        dbutil.update_collection(db, colid, cid, 0.5, "Y")
        time.sleep(0.001)
    db.close()


def update_collection_from_list(listid, colid):

    db = dbcon.connect_torndb()
    cids = [item.companyId for item in db.query('select companyId from mylist_company_rel where mylistId=%s '
                                                'order by createTime asc;', listid)]
    for cid in cids:
        dbutil.update_collection(db, colid, cid, 0.5, "Y")
        time.sleep(0.05)
    db.close()


def update_collection_from_topic(tpid, colid):

    db = dbcon.connect_torndb()
    cids = [item.companyId for item in db.query('select * from topic_company where topicId=%s and '
                                                '(active is null or active="Y");', tpid)]
    for cid in cids:
        dbutil.update_collection(db, colid, cid, 0.5, "Y")
        time.sleep(0.05)
    db.close()


def rm_collection(listname, colid):

    db = dbcon.connect_torndb()
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'template/%s' % listname)
    for line in codecs.open(path, encoding='utf-8'):
        # code, sortv = line.split('#')[0], round(float(line.split('#')[2]), 2)
        code = line.strip()
        try:
            cid = db.get('select id from company where code=%s', code).id
        except Exception, e:
            print code, e
            continue
        dbutil.rm_collection_company(db, colid, cid)
    db.close()


def merge_collection(colfrom, colto):

    db = dbcon.connect_torndb()
    cids = [item.companyId for item in db.query('select companyId from collection_company_rel where collectionId=%s '
                                                'and (active is null or active="Y");', colfrom)]
    for cid in cids:
        dbutil.update_collection(db, colto, cid)
    db.close()


def dump(colid):

    db = dbcon.connect_torndb()
    cids = [item.companyId for item in db.query('select companyId from collection_company_rel where collectionId=%s '
                                                'and (active is null or active="Y");', colid)]
    with codecs.open('files/%s' % colid, 'w', 'utf-8') as fo:
        for cid in cids:
            name = dbutil.get_company_name(db, cid)
            url = 'http://www.xiniudata.com/#/company/%s/overview' % dbutil.get_company_code(db, cid)
            fo.write('%s, %s\n' % (name, url))
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'clist':
        update_list(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'ucl':
        # list, collection
        update_collection_from_list(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'uct':
        update_collection_from_topic(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'rm':
        rm_collection(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'merge':
        merge_collection(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'dump':
        dump(sys.argv[2])