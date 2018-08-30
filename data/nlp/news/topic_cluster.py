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
from common.zhtools.postagger import Tagger
from common.zhtools.word_filter import get_default_filter
from embedding.words import WordExtender

import codecs
import numpy as np
from copy import deepcopy
from itertools import chain
from gensim.models import HdpModel
from gensim import corpora, models, similarities
from gensim.models import Word2Vec
from sklearn import cluster
from sklearn.cluster import DBSCAN


def feed_doc(tag=u'金融'):

    mongo = dbcon.connect_mongo()
    segmenter = Segmenter(tag=True)
    wfilter = get_default_filter()
    for record in mongo.article.news.find({'tags': tag}):
        yield chain(*[wfilter(segmenter.cut(piece['content'].strip()))
                      for piece in record['contents'] if piece['content'].strip()])


def feed_doc_n(tag=u'金融'):

    mongo = dbcon.connect_mongo()
    tagger = Tagger(tags=True)
    wfilter = get_default_filter()
    for record in mongo.article.news.find({'tags': tag}):
        yield chain(*[wfilter([w[0] for w in tagger.tag(piece['content'].strip()) if w[1] in ('tag', 'itag')])
                      for piece in record['contents'] if piece['content'].strip()])


def feed_doc_s(sid):

    mongo = dbcon.connect_mongo()
    tagger = Tagger(tags=True)
    wfilter = get_default_filter()
    for record in mongo.article.news.find({'sectors': sid}):
        yield chain(*[wfilter([w[0] for w in tagger.tag(piece['content'].strip()) if w[1] in ('tag', 'itag')])
                      for piece in record['contents'] if piece['content'].strip()])


def try_news_cluster():

    docs = feed_doc()
    df_threshold_lower = 50
    df_threshold_upper = 500
    dictionary = corpora.Dictionary(doc for doc in docs)
    print 'dictionary ready'
    low_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= df_threshold_lower]
    high_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq > df_threshold_upper]
    dictionary.filter_tokens(low_df + high_df)
    dictionary.compactify()
    corpus = [dictionary.doc2bow(doc) for doc in feed_doc()]
    print 'corpus ready'
    hdp = HdpModel(corpus, dictionary)
    for topic in hdp.print_topics(num_topics=50, num_words=20):
        print topic


def try_news_w2v():

    docs = feed_doc()
    df_threshold_lower = 200
    df_threshold_upper = 800
    dictionary = corpora.Dictionary(doc for doc in docs)
    print 'dictionary ready'
    low_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq <= df_threshold_lower]
    high_df = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq > df_threshold_upper]
    dictionary.filter_tokens(low_df + high_df)
    dictionary.compactify()

    # word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
    #                               '../embedding/models/s400w4min20.binary.w2vmodel')
    w2v = Word2Vec.load('../embedding/models/s400w4min20.binary.w2vmodel')

    words = []
    id2words = {}
    for k, v in dictionary.iteritems():
        if v in w2v:
            id2words[len(words)] = v
            words.append(w2v[v])

    spectral = cluster.SpectralClustering(n_clusters=10)
    spectral.fit(words)
    y = spectral.labels_.astype(np.int)
    centers = {}
    for index, label in enumerate(y):
        centers.setdefault(label, []).append(id2words.get(index))
    for k, v in centers.iteritems():
        print k, ','.join(v[:10])


def try_w2v():

    db = dbcon.connect_torndb()
    # tids = [t.id for t in db.query('select id from tag where name in ("汽车", "汽车交通", "交通");')]
    # tags = db.query('select distinct tagId from company_tag_rel where (active is null or active="Y") and companyId in '
    #                 '(select distinct companyId from company_tag_rel '
    #                 'where tagId in %s and (active is null or active="Y"));', tids)
    # tags = [db.get('select name from tag where id=%s;', tag.tagId).name for tag in tags]

    w2v = Word2Vec.load('../embedding/models/s400w4min20.binary.w2vmodel')
    # tags = w2v.most_similar(positive=[u"汽车", u"汽车交通", u"交通"], topn=100)
    extender = WordExtender(50, 0.3)
    tags = extender.extend4tag(u'金融')

    words = []
    id2words = {}
    for tag in tags:
        if tag in w2v:
            id2words[len(words)] = tag
            words.append(w2v[tag])


def try_mix():

    # word2vec
    w2v = Word2Vec.load('../embedding/models/s400w4min20.binary.w2vmodel')
    # tags = w2v.most_similar(positive=[u"汽车", u"汽车交通", u"交通"], topn=100)
    extender = WordExtender(50, 0.3)
    target, tid = u'旅游', 10
    tags = extender.extend4tag(target)
    outpath = '/data/task-201606/nlp/news/files/%s.task' % target

    existed = set()
    words = []
    id2words = {}
    for tag in tags:
        if tag in w2v:
            id2words[len(words)] = tag
            words.append(w2v[tag])
            existed.add(tag)

    # coherence
    db = dbcon.connect_torndb()
    tag = db.get('select id from tag where name=%s;', target).id
    cids = [c.companyId for c in db.query('select distinct companyId from company_tag_rel '
                                          'where tagId=%s and (active is null or active="Y");', tag)]
    coherence = [t.tagId for t in db.query('select tagId, count(*) as c from company_tag_rel '
                                           'where companyId in %s and (active is null or active="Y") '
                                           'group by tagId having c > 20;', cids)]
    coherence = [t.name for t in db.query('select name from tag '
                                          'where id in %s and type not in (11100, 11012);', coherence)]
    for t in coherence:
        if t in w2v and t not in existed:
            id2words[len(words)] = t
            words.append(w2v[t])
            existed.add(t)
        elif t not in w2v:
            print 'w2v error', t

    # news
    # docs = feed_doc_s(tid)
    # dictionary = corpora.Dictionary(doc for doc in docs)
    # dictionary2 = deepcopy(dictionary)
    # df_threshold_lower = 220
    # df_threshold_upper = 800
    # low_df = [tokenid for tokenid, docfreq in dictionary2.dfs.iteritems() if docfreq <= df_threshold_lower]
    # high_df = [tokenid for tokenid, docfreq in dictionary2.dfs.iteritems() if docfreq > df_threshold_upper]
    # dictionary2.filter_tokens(low_df + high_df)
    # dictionary2.compactify()
    # for k, v in dictionary2.iteritems():
    #     if v in w2v and v not in existed:
    #         id2words[len(words)] = v
    #         words.append(w2v[v])


    y = DBSCAN(min_samples=2, metric='cosine', algorithm='brute').fit_predict(words).astype(np.int)
    show(y, id2words, outpath)


def show(y, id2words, outpath):

    centers = {}
    for index, label in enumerate(y):
        centers.setdefault(label, []).append(id2words.get(index))
    with codecs.open(outpath, 'w', 'utf-8') as fo:
        for k, v in centers.iteritems():
            fo.write('%s\n' % ','.join(v))
            print k, ','.join(v[:10])


def divide():

    w2v = Word2Vec.load('../embedding/models/s400w4min20.binary.w2vmodel')
    with codecs.open('files/finiance.1.task', 'w', 'utf-8') as fo:
        for line in codecs.open(u'files/金融.task', encoding='utf-8'):
            words = [w for w in line.split(',') if w and w.strip()]
            __divide(w2v, words, fo, 0)


def __divide(w2v, words, fo, tries=0):

    print 'number of iteration', tries, len(words)
    print words
    if len(words) <= 10:
        fo.write('%s\n' % ','.join(words))
    elif tries == 5:
        fo.write('%s\n' % ','.join(words))
    else:
        vectors, id2words = [], {}
        for w in words:
            if w in w2v:
                vectors.append(w2v[w])
                id2words[len(vectors)] = w
        y = DBSCAN(min_samples=2, metric='cosine', algorithm='brute').fit_predict(vectors).astype(np.int)

        centers = {}
        for index, label in enumerate(y):
            if not id2words.get(index):
                print index, 'not in vocab'
            centers.setdefault(label, []).append(id2words.get(index, ''))
        for k, v in centers.iteritems():
            __divide(w2v, v, fo, tries+1)


def try_top500():

    db = dbcon.connect_torndb()
    with codecs.open('files/top500.tag', 'w', 'utf-8') as fo:
        tags = set()
        for tag in db.query('select * from tag where type in (11011, 11012)'):
            fo.write('%s\t%s\n' % (tag.name, tag.novelty))
            tags.add(tag.name)
        for tag in db.query('select tagId, count(*) as c from company_tag_rel where (active is null or active="Y") '
                            'and (createUser is not null and createUser!=139) having c>3;'):
            tag = db.get('select * from tag where id=%s;', tag.tagId)
            if tag.name not in tags:
                fo.write('%s\t%s\n' % (tag.name, tag.novelty))
                tags.add(tag.name)
        for tag in db.query('select * from tag where createTime>"2016-10-01" '
                            'and (createUser is not null and createUser!=139)'):
            if tag.name not in tags:
                fo.write('%s\t%s\n' % (tag.name, tag.novelty))
                tags.add(tag.name)


if __name__ == '__main__':

    print __file__
    try_top500()
    # divide()
    # try_mix()
    # try_news_w2v()
    # try_news_cluster()
