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


def insertcol():

    db = dbcon.connect_torndb()
    cids = [int(line.strip()) for line in open('cachs/ai.candidates.ids')]
    dups = [db.get('select id from company where code=%s;', line.strip()).id for line in open('cachs/ai.dup')]
    for cid in cids:
        if cid in dups:
            continue
        dbutil.update_collection(db, 327, cid, user=19)
    dbutil.update_collection_user(db, 327, 19)
    db.close()

if __name__ == '__main__':
    insertcol()