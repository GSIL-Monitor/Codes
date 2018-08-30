# coding=utf-8
__author__ = 'wangqc'


import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
reload(sys)
sys.setdefaultencoding('utf-8')


import db as dbcon
from common import dbutil
from common.feed import Feeder, NewsFeeder
from common.zhtools.segment import Segmenter

import codecs
import fasttext
import itertools
from random import randint
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt
from datetime import datetime


db = dbcon.connect_torndb()
mongodb = dbcon.connect_mongo()
feeder = Feeder()
seg = Segmenter()

# tag size as 1800(sector 1, 2 & 3) or 2700(type 11011, 11012, 11013, 11014)
def dump_data(train, test, tag_size=2700):
    if os.path.exists(train):
        print 'data exists.'
        return
    sql_1800 = ''' 
    select c.id cid, t.id tid from company_tag_rel ct join company c on ct.companyId = c.id join tag t on ct.tagId = t.id
    where ct.verify = "Y" and (ct.active = "Y" or ct.active is null) and ct.modifyTime > "2017-06-01" and c.verify = "Y"
    and (c.active = "Y" or c.active is null) and t.sectorType is not null;
    '''
    sql_2700 = '''
    select c.id cid, t.id tid from company_tag_rel ct join company c on ct.companyId = c.id join tag t on ct.tagId = t.id
    where ct.verify = "Y" and (ct.active = "Y" or ct.active is null) and ct.modifyTime > "2017-06-01"'
    and c.verify = "Y" and (c.active = "Y" or c.active is null) and t.type in (11011, 11012, 11013, 11014);'''

    sql = {1800: sql_1800, 2700: sql_2700}
    data = defaultdict(set)
    for record in db.query(sql[tag_size]):
        data[record.cid].add(record.tid)
    with codecs.open(train, 'w', 'utf-8') as dtrain, codecs.open(test, 'w', 'utf-8') as dtest:
        for cid, tids in data.iteritems():
            content = ' '.join(feeder.feed_seged_fine(cid))
            label = ' '.join('__label__%d' % tid for tid in tids)
            dtrain.write('%d %s %s\n' % (cid, label, content)) if randint(0, 4) else dtest.write('%d %s %s\n' % (cid, label, content))

# fasttext params tuning on dim, lr, loss and ws, params input format as 'key=[*values]'
def ft_modeling(train, test, model, **kwargs):
    params = {'dim': [100, 150], 'lr': [0.1, 0.5, 1], 'loss': ['ns', 'hs'], 'ws': [5, 10]}
    for k, v in kwargs.items():
        params[k] = v
    keys, values = params.keys(), params.values()
    best, best_score = '', 0
    for p in itertools.product(*values):
        ps = {keys[i]: p[i] for i in xrange(4)}
        clf = fasttext.supervised(train, model + '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), **ps)
        result = clf.test(test)
        print '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3])
        print 'Precision: %.2f%%' % (result.precision * 100)
        print 'Recall Rate: %.2f%%\n' % (result.recall * 100)
        f1 = float(2.0 * result.precision * result.recall) / float(result.precision + result.recall)
        if best_score < f1:
            best, best_score,  = '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), f1
    print '%s\n%.2f' % (best, best_score)


def predict(model, data_path=None, out_path=None, text=None):
    if not text and not data_path:
        print('Input at least one of valid text or data path')
        raise ValueError
    clf = fasttext.load_model(model, encoding='utf-8')
    if text:
        content = [' '.join(seg.cut4search(i)) for i in text]
    else:
        df = pd.read_csv(data_path, index_col='ID', encoding='utf_8_sig')
        content = [' '.join(seg.cut4search(i)) for i in df[u'原文本']]
    preds = clf.predict_proba(content, k=10)
    tags = []
    for pred in preds:
        pred_sum = sum(p[1] for p in pred)
        tags.append(' '.join(dbutil.get_tag_name(db, int(p[0].replace(u'__label__', ''))) for p in pred if p[1] > 0.05 * pred_sum))
    if text:
        return tags
    df['tag'] = tags
    df.to_csv(out_path, encoding='utf_8_sig')

def sample(data_path, out_path):
    df = pd.read_csv(data_path, encoding='utf_8_sig')
    df_sample = df.sample(30)
    df_sample.to_csv(out_path, encoding='utf_8_sig')

if __name__ == '__main__':
    # dump_data('tmp/data/fulltag.train', 'tmp/data/fulltag.test')
    # ft_modeling('tmp/data/fulltag.train', 'tmp/data/fulltag.test', 'tmp/data/models/')
    # predict('tmp/data/models/2700tags.bin', 'tmp/for_test.csv', 'tmp/tag2700.csv')
    sample('tmp/tag2700.csv', 'tmp/sample2.csv')

