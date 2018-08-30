# coding=utf-8
__author__ = 'wangqc'

import db as dbcon
from common import dbutil
from common.feed import Feeder


import pandas as pd
import fasttext
import numpy as np
import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
#




def sample(source, output, n):
    df = pd.read_csv(source)
    df.fillna('', inplace=True)
    mask = np.random.choice(df.id.size, n, replace=False)
    df.loc[mask].set_index('id').to_csv(output, encoding='utf_8_sig')


def tag(source, output):
    df = pd.read_csv(source)
    df.fillna('', inplace=True)
    n = df.id.size
    (tag1, tag1p, tag2, tag2p) = ([''] * n for _ in range(4))
    clf = fasttext.load_model('tmp/data/models/20180319.bin', encoding='utf-8')
    for i in range(n):
        if df.id[i] and dbutil.get_company_info(db, df.id[i]).description:
            predict = clf.predict_proba([' '.join(feeder.feed_seged_fine(df.id[i]))], k=2)[0]
            tag1[i], tag1p[i] = dbutil.get_tag_name(db, predict[0][0].replace(u'__label__', u'')), predict[0][1]
            tag2[i], tag2p[i] = dbutil.get_tag_name(db, predict[1][0].replace(u'__label__', u'')), predict[1][1]
    df['tag1'], df['tag1p'], df['tag2'], df['tag2p'] = tag1, tag1p, tag2, tag2p
    df.to_csv(output, encoding='utf_8_sig')


if __name__ == '__main__':
    db = dbcon.connect_torndb()
    mongodb = dbcon.connect_mongo_local()
    feeder = Feeder()
    # sample('tmp/tag/to_tag.csv', 'tmp/tag/sample.csv', 50)
    tag('tmp/tag/e100.0124.csv', 'tmp/tag/result.csv')