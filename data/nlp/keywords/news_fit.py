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
from common.feed import NewsFeeder

import codecs
import json
import logging
import fasttext
import itertools
from random import randint, shuffle

# logging
logging.getLogger('nf').handlers = []
logger_nf = logging.getLogger('nf')
logger_nf.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_nf.addHandler(stream_handler)


def dump_data():

    global logger_nf
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    nf = NewsFeeder()
    mapping = {}
    for line in codecs.open('files/sector.20171221.mapping', encoding='utf-8'):
        tag, relevants = line.strip().split('#')[0], line.strip().split('#')[1].split(',')
        tag = dbutil.get_tag_id(db, tag)[0]
        for relevant in relevants:
            mapping[dbutil.get_tag_id(db, relevant)[0]] = tag
    sectors = {s.id: s.tagId for s in db.query('select * from sector where tagId is not null;')}
    ftrain = codecs.open('tmp/20171221.fine.train', 'w', 'utf-8')
    ftest = codecs.open('tmp/20171221.fine.test', 'w', 'utf-8')
    count = 0
    for news in mongo.article.news.find({'processStatus': 1, 'modifyUser': {'$ne': None}, 'sectors': {'$ne': None}}):
        labels = filter(lambda x: x in mapping.keys(),
                        [sectors.get(s, -1) for s in news.get('sectors', []) if s != 999])
        labels.extend([t for t in news.get('features', []) if t in mapping.keys()])
        labels = set([mapping.get(t) for t in labels])
        if not labels:
            continue
        labels = ['__label__%s' % t for t in labels]
        if len(labels) > 3:
            continue
        labels = ' '.join(labels)
        if not labels:
            continue
        contents = ' '.join(nf.feed(news, granularity='fine')).replace('\n', ' ')
        if not contents:
            continue
        if len(contents) < 50:
            continue
        count += 1
        if count % 10000 == 0:
            logger_nf.info('Dumping file, %s done' % count)
        if randint(1, 5) == 1:
            ftest.write('%s %s\n' % (labels, contents))
        else:
            ftrain.write('%s %s\n' % (labels, contents))
    ftrain.close()
    ftest.close()
    logger_nf.info('All news dumped')


def resample():

    global logger_nf
    input_file = 'tmp/20171221.fine.train'
    dist = {}
    for line in codecs.open(input_file, encoding='utf-8'):
        for l in [w for w in line.split(' ') if w.startswith(u'__label__')]:
            dist[l] = dist.get(l, 0) + 1
    need2add = []
    with codecs.open('tmp/20171221.resample.train', 'w', 'utf-8') as fre:
        for line in codecs.open(input_file, encoding='utf-8'):
            fre.write(line)
            chance_buff = 2 if not line.split(' ')[1].startswith('__label__') else 1
            if dist.get(line.split(' ')[0]) > 1000:
                __random_add(need2add, line, 8*chance_buff)
            elif dist.get(line.split(' ')[0]) > 500:
                __random_add(need2add, line, 10*chance_buff)
            elif dist.get(line.split(' ')[0]) > 200:
                __random_add(need2add, line, 12*chance_buff)
            elif dist.get(line.split(' ')[0]) > 100:
                __random_add(need2add, line, 16*chance_buff)
            else:
                __random_add(need2add, line, 20*chance_buff)
        shuffle(need2add)
        fre.write(''.join(need2add))
    logger_nf.info('Resampled')


def __random_add(seq, item, chance):

    for _ in xrange(int(chance)):
        if randint(1, 2) == 2:
            seq.append(item)


def test():

    # input_file = 'tmp/fasttext.train'
    # test_file = 'tmp/fasttext.fine.test'
    global logger_nf
    input_file = 'tmp/20171221.resample.train'
    test_file = 'tmp/20171221.fine.test'
    output = 'tmp/classifier'

    # dim=10
    # lr=0.005
    # epoch=1
    # min_count=1
    # word_ngrams=3
    # bucket=2000000
    # thread=4
    # silent=1
    # label_prefix='__label__'
    parameters = {
        'dim': [80, 100, 120],
        'lr': [0.05, 0.06],
        'loss': ['ns', 'hs']
        # 'word_ngrams': [1, 2, 3],
    }
    keys, values = parameters.keys(), parameters.values()
    for parameter in itertools.product(*values):
        ps = {keys[i]: parameter[i] for i in xrange(3)}
        classifier = fasttext.supervised(input_file, output, **ps)
        # results = {}
        # with codecs.open(test_file, encoding='utf-8') as f:
        #     for li, line in enumerate(f):
        #         words = line.split(' ')
        #         manual_labels = [word.replace(u'__label__', '') for word in words if word.startswith(u'__label__')]
        #         content_start = len(manual_labels) + 1
        #         predict_label = classifier.predict([' '.join(words[content_start:])])[0][0]
        #         if predict_label in manual_labels:
        #             results[(predict_label, predict_label)] = results.get((predict_label, predict_label), 0) + 1
        #         else:
        #             results[(predict_label, manual_labels[0])] = results.get((predict_label, manual_labels[0]), 0) + 1
        #             # print li+1, predict_label, manual_labels[0]
        # all_labels = list(set([item[0] for item in results.keys()]) | set([item[1] for item in results.keys()]))
        # print '\t'.join(all_labels)
        # for i in all_labels:
        #     line = []
        #     for j in all_labels:
        #         line.append(results.get((i, j), 0))
        #     print '\t'.join([str(count) for count in line])

        result = classifier.test(test_file)
        logger_nf.info('Parameters: %s, P: %s, R: %s, F2: %s' % (json.dumps(ps), round(result.precision, 4),
                                                                 round(result.recall, 4),
                                                                 round(2*result.recall*result.precision/(result.precision+result.recall), 4)))


def statistic():

    global logger_nf
    input_file = 'tmp/20171221.resample.train'
    logger_nf.info('Printing statistics')
    duzhan, total = {}, {}
    for line in codecs.open(input_file, encoding='utf-8'):
        labels = [w.replace(u'__label__', u'') for w in line.split(' ') if w.startswith(u'__label__')]
        if len(labels) == 1:
            duzhan[labels[0]] = duzhan.get(labels[0], 0) + 1
            total[labels[0]] = total.get(labels[0], 0) + 1
        else:
            for l in labels:
                total[l] = total.get(l, 0) + 1
    for k, v in total.items():
        logger_nf.info('Label: %s, total %s, duzhan %s' % (k, v, duzhan.get(k, 0)))


def train():

    input_file = 'tmp/20171221.tag.train'
    output = 'tmp/20171221.fasttext'
    clf = fasttext.supervised(input_file, output, dim=120, lr=0.05, loss='ns')
    # output_file = 'tmp/fasttext.tag.train'
    # db = dbcon.connect_torndb()
    # tags = {str(item.id): str(item.tagId)
    #         for item in db.query('select id, tagId from sector where level=1 and active="Y";')}
    # with codecs.open(output_file, 'w', 'utf-8') as fo:
    #     for line in codecs.open(input_file, encoding='utf-8'):
    #         line = line.replace('__label__18 ', '')
    #         for sid, tid in tags.items():
    #             line = line.replace('__label__%s ' % sid, '__label__%s ' % tid)
    #         if not line.startswith('__label'):
    #             continue
    #         fo.write(line)


if __name__ == '__main__':

    print __file__
    dump_data()
    # resample()
    # statistic()
    # test()
    # train()
    # if sys.argv[1] == 'dump':
    #     dump_data()
    # if sys.argv[1] == 'test':
    #     test()
