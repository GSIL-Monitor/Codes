# coding=utf-8
__author__ = 'victor'

import sys
reload(sys)
sys.path.append('..')
sys.setdefaultencoding('utf-8')

import torndb
import os
import codecs
import time
import re
from random import random
from common import nlpconfig
from common.zhtools import stopword
from common.zhtools import hants
from common.zhtools.postagger import Tagger


tagger = Tagger('ltp')
doc_len_threshold = 10
year = re.compile(u'\d+年')
month = re.compile(u'\d+月')
day = re.compile(u'\d+日')
stopwords = stopword.get_standard_stopwords()


class Corpus(object):

    def __init__(self, extrc_func=None, dirs=None):

        self.extract = extrc_func if extrc_func else lambda x: x.strip()
        self.dirs = dirs

    def __iter__(self):

        for subdir in self.dirs:
            for f in os.listdir(subdir):
                if u'DS_Store' in f:
                    continue
                with codecs.open(os.path.join(subdir, f), encoding='utf-8') as fin:
                    yield ' '.join(filter(lambda x: x, [self.extract(line.strip()) for line in fin]))


def build_corpus(outdir):

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    query = 'select companyId, companyDesc from company;'
    # query = 'select newsId, content from news_content;'
    db = torndb.Connection(**nlpconfig.get_mysql_config_tshbao())
    # conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='tsb', port=3306, charset='utf8')
    # cur = conn.cursor()
    # cur.execute(query)
    # results = cur.fetchall()
    # cur.close()
    # conn.close()
    print 'db connected'

    for result in iter(db.query(query)):
        id, content = result.companyId, result.companyDesc.strip()
        # id, content = result.newsId, result.content
        if os.path.exists(os.path.join(outdir, str(id).strip())):
            continue
        if int(id) < 37000 and random() < 0.9:
            continue
        with codecs.open(os.path.join(outdir, str(id).strip()), 'w', 'utf-8') as fo:
            content = hants.translate(content)
            text = ''
            for c in ' '.join(filter(lambda x: x.strip() and len(x) > 1, content.split('\n'))).split(u'，'):
                text += c
                if len(text) > 50:
                    text = text.replace(c, '')
                    __dump(fo, text)
                    text = c
            __dump(fo, text)


def __dump(fo, text):

    global tagger
    text = text.decode('utf-8', errors='ignore')
    results = tagger.tag(text.strip())
    for result in results:
        fo.write('%s\t%s\n' % (result[0].strip().encode('utf-8'), result[1].strip()))
    time.sleep(0.005)


def clean_corpus(dir, ff=lambda x: '.' not in x, ls=lambda x: x.strip()):

    global doc_len_threshold
    for f in os.listdir(dir):
        if not ff(f):
            continue
        valid = True
        with codecs.open(os.path.join(dir, f+'.temp'), 'w', 'utf-8') as fo:
            words = words_filtering([line.lower().strip()
                                     for line in codecs.open(os.path.join(dir, f), encoding='utf-8')], ls)
            if len(words) > doc_len_threshold:
                fo.write(hants.translate('\n'.join(words)))
            else:
                valid = False
        os.remove(os.path.join(dir, f))
        if valid:
            os.rename(os.path.join(dir, f+'.temp'), os.path.join(dir, f))
        else:
            os.remove(os.path.join(dir, f+'.temp'))


def words_filtering(words, lf=lambda x: x.strip()):
    global stopwords, year, month, day
    return filter(lambda x:
                  (len(lf(x)) > 1) and
                  (not year.findall(lf(x))) and
                  (not month.findall(lf(x))) and
                  (not day.findall(lf(x))) and
                  (lf(x).lower() not in stopwords) and
                  (not lf(x).replace('.', '').isnumeric()), words)


if __name__ == '__main__':

    print 'main', __file__
    outdir = '../data/tsb/company/ltp_cut'
    build_corpus(outdir)
    line_spliter = lambda x: x.split('\t')[0].strip()
    clean_corpus(outdir, ls=line_spliter)
