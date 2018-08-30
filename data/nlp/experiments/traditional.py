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
from common.feed import Feeder

import codecs
import itertools
from random import randint

import fasttext


def dump():

    db = dbcon.connect_torndb()
    feeder = Feeder()
    mode = 'basic'
    ftrain = codecs.open('tmp/traditional.%s.train' % mode, 'w', 'utf=8')
    ftest = codecs.open('tmp/traditional.%s.test' % mode, 'w', 'utf=8')
    cids = [c.companyId for c in db.query("select distinct companyId from company_tag_rel where tagId=604330 "
                                          "and verify='Y' and (active is null or active='Y');")]
    cids.extend([dbutil.get_id_from_code(db, code.strip()) for code in codecs.open('files/traditional')])
    for cid in cids:
        content = ' '.join(feeder.feed_seged_fine(cid))
        if randint(0, 4):
            ftrain.write('__label__1 %s\n' % content)
        else:
            ftest.write('__label__1 %s\n' % content)
    print 'Positive Done'
    cids2 = [c.id for c in db.query("select id from company where modifytime>'2018-03-01' "
                                    "and modifyuser is not null order by rand() limit 15000;")]
    cids = set(cids)
    for cid in cids2:
        if cid in cids:
            continue
        content = ' '.join(feeder.feed_seged_fine(cid))
        if randint(0, 4):
            ftrain.write('__label__0 %s\n' % content)
            # ftrain.write('__label__0 %s %s\n' % (dbutil.get_company_establish_date(db, cid).year, content))
        else:
            ftest.write('__label__0 %s\n' % content)
    print 'Negetive Done'
    ftrain.close()
    ftest.close()
    db.close()


def train_(train, test, model):

    params = {'dim': [100, 150], 'lr': [0.1, 0.5, 1], 'loss': ['ns', 'hs'], 'ws': [5, 10]}
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
            best, best_score, = '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), f1
    print '%s\n%.2f' % (best, best_score)


def test_(train):

    clf = fasttext.supervised(train, 'tmp/traditional.model', dim=150, lr=0.1, loss='hs', ws=10)
    # clf = fasttext.load_model('tmp/traditional.model', encoding='utf-8')
    fo = codecs.open('tmp/analysis', 'w', 'utf-8')
    test_data = []
    with codecs.open('tmp/traditional.basic.test', encoding='utf-8') as f:
        for line in f:
            label = line.split(' ')[0].replace('__label__', '')
            if not label.strip():
                print line
            content = ' '.join(line.split(' ')[1:])
            test_data.append((label, content))
    # print clf.predict_proba([c for (_, c) in test_data, 1])
    docs = [c for (_, c) in test_data]
    for index, item in enumerate(clf.predict_proba(docs, 1)):
        fo.write('%s\t%s\t%s\n' % (test_data[index][0], item[0][0], item[0][1]))


if __name__ == '__main__':

    test_('tmp/traditional.basic.train')
    # dump()
    # train('tmp/traditional.basic.train', 'tmp/traditional.basic.test', 'tmp/')