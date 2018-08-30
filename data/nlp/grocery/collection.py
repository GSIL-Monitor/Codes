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


def dump(colid):

    db = dbcon.connect_torndb()
    with codecs.open('files/%s.collection' % colid, 'w', 'utf-8') as fo:
        for item in db.query('select companyId from collection_company_rel where collectionId=%s '
                             'and (active is null or active="Y") order by createTime desc, id desc;', colid):
            info = dbutil.get_company_info(db, item.companyId)
            status = {
                2010: u'正常',
                2015: u'融资中',
                2020: u'已关闭',
                2025: u'停止更新'
            }.get(info.get('companyStatus', 2010), u'正常')
            fo.write('%s\t%s\t%s\n' % (info['code'], info['name'], status))
    db.close()


def revert():

    db = dbcon.connect_torndb()
    with codecs.open('files/collection', 'r', 'utf-8') as f:
        for line in f:
            colid, name = line.strip().split('#')[0], line.strip().split('#')[1]
            db.execute('update collection set name=%s where id=%s;', name, colid)
    db.close()

if __name__ == '__main__':

    print __file__
    # revert()
    dump(sys.argv[1])