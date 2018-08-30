# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil
from common.feed import Feeder
from common.zhtools import word_filter, hants
from common.zhtools.postagger import Tagger
from common.zhtools.segment import Segmenter
from key import Extractor

import re
import codecs

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.externals import joblib

word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                              '../embedding/models/s400w3min20_yitai.binary.w2vmodel')


def load_blockchain():

    db = dbcon.connect_torndb()
    db.execute('delete from tags_rel where id=447283;')
    t3s = [t.tag2Id for t in db.query('select tag2Id from tags_rel where tagId=175747 and type=54041;')]
    db.execute('delete from tags_rel where tagId=175747;')
    db.execute('update tag set type=11010, sectorType=null where id in %s;', t3s)
    for line in codecs.open('files/blockchain', encoding='utf-8'):
        tags = line.strip().split()
        if len(tags) == 1:
            t2id = dbutil.get_tag_id(db, tags[0])[0]
            db.execute('update tag set type=11013, sectorType=2 where name=%s;', tags[0])
            dbutil.update_tags_rel(db, 175747, t2id, 1, 54041)
        if len(tags) == 2:
            t2id = dbutil.get_tag_id(db, tags[0])[0]
            t3id = dbutil.get_tag_id(db, tags[1])[0]
            db.execute('update tag set type=11013, sectorType=3 where name=%s;', tags[1])
            dbutil.update_tags_rel(db, t2id, t3id, 1, 54041)
    db.execute('update tag set sectorType=1, type=11012 where id=175747;')
    db.execute('insert into sector (sectorName, active, level, tagid, createtime) '
               'values ("区块链", "Y", 1, 175747, now());')


def label_blockchain():

    db = dbcon.connect_torndb()
    feeder = Feeder()
    w2v = Word2Vec.load(word2vec_model)
    model_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'models')
    clf = joblib.load(os.path.join(model_dir, '175747.20180311.model'))
    for cid in dbutil.get_all_company_id(db):
        print cid
        flag = False
        try:
            content = list(feeder.feed_seged(cid))
            content = [np.mean([w2v[w] for w in content if w in w2v], axis=0)]
            if u'区块链' not in content:
                if clf.predict_proba(content)[0][1] > 0.9:
                    dbutil.update_company_tag(db, cid, 175747, 2.806, verify='N', active='Y')
                    flag = True
            else:
                if clf.predict(content)[0] == 1:
                    dbutil.update_company_tag(db, cid, 175747, 2.806, verify='N', active='Y')
                    flag = True
            if dbutil.exist_company_tag(db, cid, 175747) and not flag:
                dbutil.update_company_tag(db, cid, 175747, 0, verify='N', active='N')
        except Exception, e:
            print 'Fail to classify, due to %s', e


def load_organize():

    db = dbcon.connect_torndb()
    # 创建全部tag, 如果没有
    with codecs.open('files/xiniu.organize', encoding='utf-8') as f:
        for line in f:
            for tag in re.split('[#\(\)\+\,]', line.strip()):
                if tag and tag.strip():
                    if not dbutil.exist_tag(db, tag, True):
                        db.execute('insert into tag (name, type) values (%s, 11009);', tag.strip())
    # load关系
    db.execute('update tag set sectortype=null, type=11010 where sectortype in (2,3);')
    db.execute('delete from tags_rel where id>0 and type=54041;')
    with codecs.open('files/xiniu.organize', encoding='utf-8') as f:
        for line in f:
            line = line.strip().split('#')
            db.execute('update tag set sectorType=2, type=11013 where name=%s;', line[1].strip())
            t1 = db.get('select id from tag where name=%s;', line[0].strip()).id
            t2 = db.get('select id from tag where name=%s;', line[1].strip()).id
            dbutil.update_tags_rel(db, t1, t2, 1, 54041)
            if len(line) == 3:
                db.execute('update tag set type=11013 where name=%s;', line[2].strip())
                db.execute('update tag set sectorType=3 where name=%s and sectorType is null;', line[2].strip())
                t3 = db.get('select id from tag where name=%s;', line[2].strip()).id
                dbutil.update_tags_rel(db, t2, t3, 1, 54041)
            # line = line.strip().split('#')
            # # 只有一级tag
            # if len(line) == 1:
            #     continue
            # if len(line) == 2:
            #     db.execute('update tag set sectorType=2, type=11013 where name=%s;', line[1].strip())
            #     t1 = db.get('select id from tag where name=%s;', line[0].strip()).id
            #     t2 = db.get('select id from tag where name=%s;', line[1].strip()).id
            #     dbutil.update_tags_rel(db, t1, t2, 1, 54041)
            # if len(line) == 3:
            #     db.execute('update tag set sectorType=2, type=11013 where name=%s;', line[1].strip())
            #     db.execute('update tag set sectorType=3, type=11013 where name=%s;', line[2].strip())
            #     t1 = db.get('select id from tag where name=%s;', line[0].strip()).id
            #     t2 = db.get('select id from tag where name=%s;', line[1].strip()).id
            #     t3 = db.get('select id from tag where name=%s;', line[2].strip()).id
            #     dbutil.update_tags_rel(db, t1, t2, 1, 54041)
            #     dbutil.update_tags_rel(db, t2, t3, 1, 54041)
            # if len(line) == 4:
            #     if line[2] and line[2].strip():
            #         db.execute('update tag set sectorType=2, type=11013 where name=%s;', line[1].strip())
            #         db.execute('update tag set sectorType=3, type=11013, rule=%s '
            #                    'where name=%s;', line[3], line[2].strip())
            #         t1 = db.get('select id from tag where name=%s;', line[0].strip()).id
            #         t2 = db.get('select id from tag where name=%s;', line[1].strip()).id
            #         t3 = db.get('select id from tag where name=%s;', line[2].strip()).id
            #         dbutil.update_tags_rel(db, t1, t2, 1, 54041)
            #         dbutil.update_tags_rel(db, t2, t3, 1, 54041)
            #     else:
            #         db.execute('update tag set sectorType=2, type=11013, rule=%s '
            #                    'where name=%s;', line[3], line[1].strip())
            #         t1 = db.get('select id from tag where name=%s;', line[0].strip()).id
            #         t2 = db.get('select id from tag where name=%s;', line[1].strip()).id
            #         dbutil.update_tags_rel(db, t1, t2, 1, 54041)


def extract_pack():

    from key import Extractor
    e = Extractor()
    db = dbcon.connect_torndb()
    for line in open('files/todo.pack'):
        cid = dbutil.get_id_from_code(db, line.strip())
        e.extract(cid)
        print line.strip()


def dump_sectors():

    db = dbcon.connect_torndb()
    with codecs.open('dumps/xiniu.tag', 'w', 'utf-8') as fo:
        for t1 in dbutil.get_sectored_tags(db, 1):
            for t2id in dbutil.get_tags_by_relation(db, t1.id, 54041):
                for t3id in dbutil.get_tags_by_relation(db, t2id, 54041):
                    fo.write('%s\t%s\t%s\n' % (t1.name, dbutil.get_tag_name(db, t2id), dbutil.get_tag_name(db, t3id)))
    db.close()


def stat_qmp():

    codes = [line.strip() for line in codecs.open('files/qmp.all', encoding='utf-8')]
    db = dbcon.connect_torndb()
    print db.get('select count(*) c from company where code in %s and (active is null or active="Y");', codes).c


if __name__ == '__main__':

    print __file__
    stat_qmp()
    # dump_3rd_tag()
    # split_types()
    # dump_sectors()
    # extract_pack()
    # load_organize()
    # label_blockchain()
    # load_blockchain()
