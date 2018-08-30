# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common.zhtools.segment import Segmenter

import codecs
import random
import numpy as np


def load_data_l1_sources():

    with codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config/sector_name'),
                     encoding='utf-8') as f:
        config = {int(line.split('#')[0].strip()): line.split('#')[1].split(',') for line in f if line.strip()}
    db = dbcon.connect_torndb()
    seg = Segmenter()
    trainx, trainy = [], []
    for sid, names in config.iteritems():
        for name in names:
            ids = db.query('select distinct id from source_company where field=%s;', name)
            for scid in ids:
                content = db.query('select content from source_context '
                                   'where sourceCompanyId=%s and char_length(content)>20 and type=30020 '
                                   'and confidence>0.7 '
                                   'order by confidence desc;', scid.id)
                if len(content) > 0:
                    trainx.append(' '.join(seg.cut(content[0].content.strip())))
                    trainy.append(sid)
    db.close()
    print set(trainy)
    return trainx, np.array(trainy)


def load_data_l1_sources_tags():

    with codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config/sector'),
                     encoding='utf-8') as f:
        config = {int(line.split('#')[0].strip()): line.split('#')[1].split(',') for line in f}
    db = dbcon.connect_torndb()
    trainx, trainy = [], []
    for sid, names in config.iteritems():
        for name in names:
            cids = db.query('select distinct companyId from source_company where field=%s;', name)
            for cid in cids:
                cid = cid.companyId
                tags = db.query('select tag.name from tag, company_tag_rel where company_tag_rel.companyId=%s '
                                'and company_tag_rel.tagId=tag.id;', cid)
                if len(tags) > 1:
                    trainx.append(' '.join([tag.name for tag in tags]))
                    trainy.append(sid)
    db.close()
    return trainx, np.array(trainy)


def load_data_l1():

    db = dbcon.connect_torndb()
    seg = Segmenter()
    # tfidf = TfIdfExtractor()
    trainx, trainy = [], []
    resutls = db.query('select company_sector.companyId, company_sector.sectorId from company_sector, sector '
                       'where company_sector.verify="Y" and sector.id=company_sector.sectorId and sector.level=1 ')
                       # 'and sector.id not in (6, 9, 10, 12, 13, 15, 16, 17, 18, 19, 999);')
    for result in resutls:
        desc = db.get('select description from company where id=%s', result.companyId)
        sid = result.sectorId
        if desc and desc.description.strip():
            # trainx.append(desc.strip())
            trainx.append(' '.join(seg.cut(desc.description.strip())))
            trainy.append(int(sid))
    # trainx, trainy = tfidf.train(trainx, trainy)
    db.close()
    return trainx, np.array(trainy)
    # return trainx, trainy, tfidf


def analyze(sety):

    counts = {di: list(sety).count(di) for di in set(sety)}
    print 'count', counts


def down_sample(setx, sety):

    counts = {di: list(sety).count(di) for di in set(sety)}
    min_sample = min(counts.values())
    min_sample = 1000

    counter = {}
    newx, newy = [], []
    for index, x in enumerate(setx):
        counter.setdefault(sety[index], []).append(x)

    # for k, v in counter.iteritems():
    #     samples = vip.random.1.sample(v, min_sample) if len(v) > min_sample else v
    #     for x in samples:
    #         newx.append(x)
    #         newy.append(k)
    # print 'new sample', len(newx), len(newy), min_sample
    # return newx, np.array(newy)


def up_sample(setx, sety):

    counts = {di: list(sety).count(di) for di in set(sety)}
    # min_sample = min(counts.values())
    max_sample = 500

    counter = {}
    newx, newy = [], []
    for index, x in enumerate(setx):
        counter.setdefault(sety[index], []).append(x)

    for k, v in counter.iteritems():
        samples = [] if len(v) < max_sample else v
        while len(samples) < max_sample:
            if (max_sample-len(samples)) >= len(v):
                samples.extend(v)
            else:
                samples.extend(random.sample(v, (max_sample-len(samples))))
        for x in samples:
            newx.append(x)
            newy.append(k)
    print 'new sample', len(newx), len(newy), max_sample
    return newx, np.array(newy)