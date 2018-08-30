import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil

import time
import codecs


def get_hot_tags():

    db = dbcon.connect_torndb()
    hots = db.query('select id, name, novelty from tag where novelty is not null order by novelty limit 10;')
    db.execute('delete from hot_tag;')
    for hot in hots:
        db.execute('insert into hot_tag (id, name, sort, createTime) '
                   'values (%s, %s, %s, now());', hot.id, hot.name, round(hot.novelty, 2))
    db.close()

    print time.ctime(), 'Hot tag updated'


def dump_hots():

    db = dbcon.connect_torndb()
    hots = [x.name for x in
            db.query('select name, novelty from tag where novelty is not null order by novelty limit 150;')]
    sectors = [x.sectorName for x in db.query('select sectorName from sector') if x.sectorName not in hots]
    with codecs.open('cach/hots', 'w', 'utf-8') as fo:
        fo.write('\n'.join(sectors))
        fo.write('\n')
        fo.write('\n'.join(hots))
    db.close()


def load_hots(name='hots', type=10010):

    db = dbcon.connect_torndb()

    with codecs.open('thesaurus/%s' % name, encoding='utf-8') as f:
        for line in f:
            tid = dbutil.get_tag_id(db, line.strip())
            db.execute('update tag set hot="Y", type=%s, modifyTime=now() where name=%s;', type, line.strip())
            try:
                hot = db.get('select id, novelty from tag where name=%s;', line.strip())
                if len(db.query('select * from hot_tag where name=%s;', line.strip())) > 0:
                    continue
                db.execute('insert into hot_tag (id, name, sort, createTime) values (%s, %s, %s, now())',
                           hot.id, line.strip(), round(hot.novelty or 0, 2))
            except Exception, e:
                print line.strip(), e

    db.close()


if __name__ == '__main__':

    print __file__