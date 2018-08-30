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

import codecs
import fasttext
import itertools
from sklearn import metrics
import matplotlib.pyplot as plt
from datetime import datetime

db = dbcon.connect_torndb()
mongodb = dbcon.connect_mongo()
feeder, nf = Feeder(), NewsFeeder()


def dump_data(train, test):
    tags = dict()
    # mapping 1st tier tags with 2nd tier tags
    query = '''select r.tagId, s.sectorName, r.tag2Id, t.name, r.type 
    from tag as t, sector as s, tags_rel as r
    where r.type = 54041 and r.tag2Id = t.id and r.tagId = s.tagId and r.tagId not in (8, 40, 133, 578, 604330)
    '''
    for q in db.query(query):
        tags[q.tag2Id] = tags[q.tagId] = q.tagId
    query = '''select tagId, t.name as tag, c.id, c.description
    from company_tag_rel as r, company as c, tag as t
    where companyId = c.id and r.verify = 'Y' and r.active = 'Y' and tagId = t.id and r.createTime > '2017-07-01'
    '''
    # add company data for training and test, label: company tag id, content: company description
    companies = dict()
    for company in db.query(query):
        if company.tagId in tags.keys() and company.description and len(company.description) > 20:
            label, cid = tags[company.tagId], company.id
            content = ' '.join(feeder.feed_seged_fine(cid))
            if cid in companies and label not in companies[cid][0]:
                companies[cid][0].append(label)
            else:
                companies[cid] = [[label], content]
    # identify company data for test, avoid adding them to training data
    testids = []
    for line in codecs.open(test, 'rb', 'utf-8'):
        testids.append(int(line.split(' ', 1)[0]))
    with codecs.open(train, 'w', 'utf-8') as dtrain:
        for k, v in companies.items():
            cid, labels, content = k, ' '.join(['__label__%d' % l for l in v[0]]), v[1]
            if len(v[0]) < 2 and cid not in testids:
                dtrain.write('%d %s %s\n' % (cid, labels, content))
        count = _count(train)
        tid = {q.id: q.tagId for q in db.query('select id, tagId from sector where tagId is not null')}
        # boost training data with news
        mongodb.article.news.create_index([('createTime', -1)])
        for news in mongodb.article.news.find(
                {'processStatus': 1, 'modifyUser': {'$nin': [None, 139]}, 'sectors': {'$ne': None},
                 'createTime': {'$gt': datetime(2017, 1, 1)}}).sort([('createTime', -1)]):
            nid = news['_id']
            label = filter(lambda x: x in tags.keys(), [tid.get(s, -1) for s in news.get('sectors', []) if s != 999])
            label = list(set([tags.get(l) for l in label]))
            # boost each tag training data up to 3000
            if len(label) == 1 and count[str(label[0])] < 3000:
                count[str(label[0])] += 1
                content = ' '.join(nf.feed(news, granularity='fine'))
                if len(content) > 50:
                    labels = ' '.join(['__label__%s' % l for l in label])
                    dtrain.write('%s %s %s\n' % (nid, labels, content))


def _count(source):
    count = dict()
    for line in codecs.open(source, 'rb', 'utf-8'):
        for l in [w.replace(u'__label__', u'') for w in line.split(' ', 3)[1:] if w.startswith(u'__label__')]:
            count[l] = count.get(l, 0) + 1
    return count


def stat(output, *sources):
    with codecs.open(output, 'w', 'utf-8') as fo:
        for s in sources:
            count = _count(s)
            summary = '\nTagId\t\t\tTag Name\t\tCount\n'\
               + '\n'.join(['%-8s\t\t%-8s\t\t%-8d' % (k, dbutil.get_tag_name(db, k), v) for k, v in count.items()])\
               + '\nSum\t:%-8d Max\t:%-8d Min\t:%-8d' % (sum(count.values()), max(count.values()), min(count.values()))
            fo.write('%s:\n------\n' % (s.split('/')[-1]) + summary + '\n\n\n')


# def resample(source, output):
#     if os.path.exists(output):
#         print 'Resample exists.'
#         return
#     count = _count(source)
#     with codecs.open(source, encoding='utf-8') as fin, codecs.open(output, 'w', 'utf-8') as fo:
#         for line in fin:
#             num = count[line.split(' ', 2)[1].replace(u'__label__', u'')]
#             if num > 1500:
#                 fo.write(''.join([line for _ in xrange(1) if not randint(0, 2)]))
#             elif num > 800:
#                 fo.write(''.join([line for _ in xrange(1) if randint(0, 1)]))
#             elif num > 400:
#                 fo.write(''.join([line for _ in xrange(2) if randint(0, 1)]))
#             elif num > 300:
#                 fo.write(''.join([line for _ in xrange(3) if randint(0, 1)]))
#             elif num > 200:
#                 fo.write(''.join([line for _ in xrange(4) if randint(0, 1)]))
#             elif num > 150:
#                 fo.write(''.join([line for _ in xrange(6) if randint(0, 1)]))
#             else:
#                 fo.write(''.join([line for _ in xrange(12) if randint(0, 1)]))

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


def testing(test, model, path, one_label=True, pivot=True, auc=True):
    clf = fasttext.load_model(model, encoding='utf-8')
    tids, labels, contents = list(), list(), list()
    for line in codecs.open(test):
        tid, rest = line.split(' ', 1)
        tids.append(tid), labels.append([])
        while rest.startswith(u'__label__'):
            label, rest = rest.split(' ', 1)
            labels[-1].append(label.replace(u'__label__', u''))
        contents.append(rest)
    preds = [[(l.replace(u'__label__', u''), p) for l, p in lp] for lp in clf.predict_proba(contents, k=3)]
    with codecs.open(path + 'predict', 'w', 'utf-8') as fo:
        for i in xrange(len(tids)):
            ab_res = 'T' if labels[i][0] == preds[i][0][0] else 'F'
            res = 'T' if labels[i][0] in [l for l, _ in preds[i]] else 'F'
            fo.write('%-8s%s\t%s\t%-30s%-30s%-s\n'
                     % (tids[i], ab_res, res, dbutil.get_company_name(db, tids[i]),
                        '&'.join([dbutil.get_tag_name(db, l) for l in labels[i]]),
                        '\t'.join([dbutil.get_tag_name(db, l) + ' ' + str(p) for l, p in preds[i]])))

    def summary(label, pred, output):
        pt, pos, true = dict(), dict(), dict()
        for i_ in xrange(len(label)):
            for l_ in label[i_]:
                true[l_] = true.get(l_, 0) + 1
            for p_ in pred[i_]:
                pos[p_] = pos.get(p_, 0) + 1
                if p_ in label[i_]:
                    pt[p_] = pt.get(p_, 0) + 1
        with codecs.open(output, 'w', 'utf-8') as fo:
            fo.write('Tag\t\tPrecision\tRecall\t\tPredict\t\tActual\n')
            for k in true:
                precision, recall = float(pt[k]) / float(pos[k]), float(pt[k]) / float(true[k])
                fo.write('%-8s\t%-8f\t%-8f\t%-8d\t%-8d\n' % ((dbutil.get_tag_name(db, k)), precision, recall, pos[k], true[k]))

    def for_pivot(label, pred, output):
        pivot_map = dict()
        for i_ in xrange(len(label)):
            l_, p_ = label[i_][0], pred[i_][0][0]
            pivot_map[l_] = pivot_map.get(l_, dict())
            pivot_map[l_][p_] = pivot_map[l_].get(p_, 0) + 1
        with codecs.open(output, 'w', 'utf-8') as fo:
            fo.write('%-8s\t%-8s\t%s\n' % ('Actual', 'Predict', 'Count'))
            for k, v in pivot_map.items():
                for k_, v_ in v.items():
                    fo.write('%-8s\t%-8s\t%d\n' % (dbutil.get_tag_name(db, k), dbutil.get_tag_name(db, k_), v_))

    def roc_auc(label, pred):
        y_true, y_prob = list(), list()
        for i_ in xrange(len(label)):
            y_true = y_true + [1] if label[i_][0] == pred[i_][0][0] else y_true + [0]
            y_prob.append(pred[i_][0][1])
        fpr, tpr, thresholds = metrics.roc_curve(y_true, y_prob)
        auc_score = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label='ROC curve (area = %.2f)' % auc_score)
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        plt.show()
        return auc_score

    if one_label:
        summary([[l[0]] for l in labels], [[ps[0][0].replace(u'__label__', u'')] for ps in preds], path + 'one_label')
    else:
        summary(labels, [[p[0].replace(u'__label__', u'') for p in ps] for ps in preds], path + 'mul_labels')
    if pivot:
        for_pivot(labels, preds, path + 'pivot')
    if auc:
        print 'AUC: %f' % roc_auc(labels, preds)


def predict(model, k=3, cid=None, raw_info=None):
    clf = fasttext.load_model(model, encoding='utf-8')
    if cid or raw_info:
        content = dbutil.get_company_info(db, cid).description if cid else raw_info
        content = [' '.join(nf.wfilter(nf.seg.cut4search(content.replace('\n', ''))))]
        return '\n'.join(['%-8s\t%f' % (dbutil.get_tag_name(db, l.replace(u'__label__', u'')), p)
                          for l, p in clf.predict_proba(content, k=k)[0]])
    return 'No company id or text found.'


if __name__ == '__main__':
    # dump_data('tmp/data/201803.train', 'tmp/data/201803.test')
    # stat('tmp/data/summary', 'tmp/data/201803.train', 'tmp/data/201803.test')
    # ft_modeling('tmp/data/201803.train', 'tmp/data/201803.test', 'tmp/data/models/')
    testing('tmp/data/201803.test', 'tmp/data/models/20180319-2.bin', 'tmp/data/')
    # text = 'GPS三大传统医疗器械巨头不约而同地展出了人工智能相关的产品和技术，智慧和数字化成了新的基调。其中GE医疗更是独领风骚，一口气展出了16款集中体现智慧型创新的技术和数字医疗成果，甚至在展台上专门开辟了一个数字医疗体验中心，对这些成果进行场景化的展示'
    # print predict('tmp/data/models/20180316.bin', raw_info=text)

