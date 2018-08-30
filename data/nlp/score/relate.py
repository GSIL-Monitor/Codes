# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))


import db as dbcon
from common import dbutil
from common.dsutil import weighted_jaccard
from common.zhtools.postagger import Tagger
from common.zhtools import stopword

import codecs
import json
import urlparse
from random import choice
from bson.objectid import ObjectId
from collections import Counter
from sklearn import cross_validation
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression


def dump_domain():

    count = {}
    mongo = dbcon.connect_mongo()
    for item in mongo.article.news.find({}):
        netloc = urlparse.urlparse(item['link']).netloc
        count[netloc] = count.get(netloc, 0) + 1
    results = {item[0]: item[1] for item in count.iteritems() if item[1] > 1}
    with codecs.open('dumps/news.domain', 'w', 'utf-8') as fo:
        fo.write(json.dumps(results))


class NewsFeatures(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.tagger = Tagger()
        self.stopwords = stopword.get_standard_stopwords()
        self.source = json.load(codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                         'dumps/news.domain'), encoding='utf-8'))
        self.failed = 0

    def featurize(self, cid, **kwargs):

        features = {}
        instance = dict(**kwargs)
        if instance.get('name') and instance.get('name_update', True):
            self.tagger.add_word(instance.get('name'), tag='cn')
        name, title, content, link = instance.get('name'), instance.get('title'), instance.get('content'), \
                                     instance.get('link')

        if title and title.strip():
            title = self.tagger.tag(title)
            matches = [x[0] for x in title if x[1] == 'cn']
            features['title_ne'] = matches.count(name)
        if content and content.strip():
            content = list(self.tagger.tag(content))
            # content ne
            matches = [x[0] for x in content if x[1] == 'cn']
            features['content_ne'] = round(float(matches.count(name))/len(content), 4)
            # features['content_length'] = len(content)
            # content similarity
            try:
                odesc = Counter([item[0] for item in self.tagger.tag(dbutil.get_company_solid_description(self.db, cid))
                                 if item[0].strip() and item[0] not in self.stopwords and len(item[0]) > 1 and
                                 not item[0].isnumeric()])
                idesc = Counter([item[0] for item in content if item[0].strip() and item[0] not in self.stopwords
                                 and len(item[0]) > 1 and not item[0].isnumeric()])
                length = max(min(50, len(idesc), len(odesc)), 20)
                odesc, idesc = odesc.most_common(length), idesc.most_common(length)
                odesc.extend([(x[1], x[2]*5) for x in dbutil.get_company_tags_idname(self.db, cid)])

                simi = weighted_jaccard(odesc, idesc)
                # if simi > 0.05:
                #     print simi, cid, instance
                features['content_simi'] = simi
            except:
                self.failed += 1
        # if link and link.strip():
        #     features['source'] = self.source.get(urlparse.urlparse(link).netloc, 0)

        return features


def train():

    nf = NewsFeatures()
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    vec = DictVectorizer()
    random_source = [item[0] for item in nf.source.items() if item[1] <= 20]
    setx, sety = [], []

    print 'init'

    for index, item in enumerate(mongo.article.news.find({'source': 13030}).limit(2000)):

        if index % 50 == 0:
            print index

        link = item.get('link')
        cid = item.get('companyId')
        name = dbutil.get_company_name(db, cid)
        title = item.get('title')
        content = []
        for v in item.get('contents'):
            if v.get('content') and v.get('content').strip():
                content.append(v.get('content').strip())
        content = '\n'.join(content)

        if len(content) > 50:
            normal = nf.featurize(cid, name=name, title=title, content=content, link=link)
            setx.append(normal)
            sety.append(1)

            # rcid = dbutil.random_company_id(db)
            # rname = name[:-1]
            # makeup = nf.featurize(rcid, name=rname, title=title, content=content,
            #                       link=choice(random_source), name_update=False)
            # # print makeup
            # if makeup.get('content_simi', 0) > 0.02:
            #     print 'makeup', makeup, rcid
            # print 'mongo', cid, item.get('_id'), normal
            # setx.append(makeup)
            # sety.append(0)

    # load bad cases
    with codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'corpus/news.badcase'),
                     encoding='utf-8') as f:
        for line in f:
            try:
                cid = dbutil.get_id_from_code(db, line.split('\t')[0])
                nids = [nid for nid in line.strip().split('\t')[1:] if nid.strip()]
            except Exception, e:
                print 'fail to load bad case', line
                continue
            for nid in nids:
                try:
                    item = mongo.article.news.find({'_id': ObjectId(nid)})[0]
                    link = item.get('link')
                    name = dbutil.get_company_name(db, cid)
                    title = item.get('title')
                    content = []
                    for v in item.get('contents'):
                        if v.get('content') and v.get('content').strip():
                            content.append(v.get('content').strip())
                    content = '\n'.join(content)
                    setx.append(nf.featurize(cid, name=name, title=title, content=content, link=link, name_update=False))
                    sety.append(0)
                except Exception, e:
                    print 'nid', nid, e

    print 'failed', nf.failed
    print 'size', len(setx), len(sety)

    setx = vec.fit_transform(setx).toarray()
    clf = LogisticRegression()

    print 'cross', cross_validation.cross_val_score(clf, setx, sety, cv=5)

    clf.fit(setx, sety)
    print clf._get_param_names()
    print clf.decision_function(setx)
    joblib.dump(clf, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.score.0824.lrmodel'))
    joblib.dump(vec, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.0824.featurizer'))


def test():

    nf = NewsFeatures()
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    vec = DictVectorizer()
    random_source = [item[0] for item in nf.source.items() if item[1] <= 20]
    setx, sety = [], []

    # print 'init'
    #
    # for index, item in enumerate(mongo.article.news.find({'source': 13030}).limit(2000)):
    #
    #     if index % 50 == 0:
    #         print index
    #
    #     link = item.get('link')
    #     cid = item.get('companyId')
    #     name = dbutil.get_company_name(db, cid)
    #     title = item.get('title')
    #     content = []
    #     for v in item.get('contents'):
    #         if v.get('content') and v.get('content').strip():
    #             content.append(v.get('content').strip())
    #     content = '\n'.join(content)
    #
    #     if len(content) > 50:
    #         normal = nf.featurize(cid, name=name, title=title, content=content, link=link)
    #         setx.append(normal)
    #         sety.append(1)
    #
    #         rcid = dbutil.random_company_id(db)
    #         rname = name[:-1]
    #         makeup = nf.featurize(rcid, name=rname, title=title, content=content,
    #                               link=choice(random_source), name_update=False)
    #         # print makeup
    #         if makeup.get('content_simi', 0) > 0.02:
    #             print 'makeup', makeup, rcid
    #         print 'mongo', cid, item.get('_id'), normal
    #         setx.append(makeup)
    #         sety.append(0)
    #
    # print 'failed', nf.failed
    # print 'size', len(setx), len(sety)
    #
    # setx = vec.fit_transform(setx).toarray()
    # clf = LogisticRegression()
    #
    # print 'cross', cross_validation.cross_val_score(clf, setx, sety, cv=5)
    #
    # clf.fit(setx, sety)
    # print clf._get_param_names()
    # print clf.decision_function(setx)
    # joblib.dump(clf, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.score.lrmodel'))
    # joblib.dump(vec, os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.featurizer'))

    # clf.fit(setx, sety)
    #

    clf = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.score.lrmodel'))
    vec = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.featurizer'))

    testx, prints = [], []
    for item in mongo.article.news_test_1.find().limit(20):

        link = item.get('url')
        cid = item.get('company_id')
        name = item.get('search_name').lower()
        title = item.get('title').lower()
        content = []
        for v in item.get('parsed_contents'):
            if v.get('data') and v.get('data').strip():
                content.append(v.get('data').strip())
        content = '\n'.join(content).lower()

        piece = nf.featurize(cid, name=name, title=title, content=content, link=link)
        prints.append((item.get('_id'), piece))
        testx.append(piece)

    testx = vec.transform(testx)
    probs = clf.predict_proba(testx)
    results = clf.predict(testx)
    # print 'testx', testx
    for i in xrange(len(prints)):
        print prints[i]
        print results[i]
        print probs[i]
    return clf, vec


def check():


    nf = NewsFeatures()
    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()

    for item in mongo.article.news_5.find({}):

        link = item.get('url')
        cid = item.get('company_id')
        name = item.get('search_name').lower()
        title = item.get('title').lower()
        content = []
        for v in item.get('parsed_contents'):
            if v.get('data') and v.get('data').strip():
                content.append(v.get('data').strip())
        content = '\n'.join(content).lower()

        piece = nf.featurize(cid, name=name, title=title, content=content, link=link)


def load():

    clf = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.score.lrmodel'))
    vec = joblib.load(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dumps/news.featurizer'))


if __name__ == '__main__':

    print __file__
    # test()
    train()
    # check()
    # load()