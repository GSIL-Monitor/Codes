# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon

import codecs


def clean_dup_comps():

    db = dbcon.connect_torndb()
    for dup in db.query('select companyId cid, company2Id cid2, count(*) c from companies_rel '
                        'group by companyId, company2Id having c>1;'):
        relids = [rel.id for rel in db.query('select id from companies_rel where companyId=%s and company2Id=%s;',
                                             dup.cid, dup.cid2)][1:]
        db.execute('delete from companies_rel where id in %s', relids)


if __name__ == '__main__':

    print __file__
    clean_dup_comps()
