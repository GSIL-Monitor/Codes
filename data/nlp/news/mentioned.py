# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil, dicts
from common.zhtools.ner import CompanyNER
from score.relatedness import RelatednessScorer

import logging
from bson.objectid import ObjectId

# logging
logging.getLogger('news_mention').handlers = []
logger_mention = logging.getLogger('news_mention')
logger_mention.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_mention.addHandler(stream_handler)


class CompanyLinker(object):

    def __init__(self):

        self.ner = CompanyNER()
        self.scorer = RelatednessScorer(model='easy')
        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.weight_title = 2
        self.weight_front = 1.5

    def find_all(self):

        for record in list(self.mongo.article.news.find({'type': {'$in': [60001, 60002, 60003]}})):
            try:
                mentioned = list(self.find(record['_id']))
                if mentioned:
                    cids, confs = [x[0] for x in mentioned], [x[1] for x in mentioned]
                    self.mongo.article.news.update({'_id': record['_id']},
                                                   {'$set': {'companyIds': cids, 'mention_confidence': confs}})
                else:
                    cids = [0]
                logger_mention.info('%s processed, found' % record['_id'], cids)
            except Exception, e:
                logger_mention.exception(record['_id'], e)

    def find(self, nid):

        record = self.mongo.article.news.find({'_id': nid}).limit(1)[0]
        return self.find_from_record(record)

    def find_from_record(self, record):

        candidates = self.find_candidates(record)
        for name, freq in candidates.iteritems():
            cids = dbutil.get_id_from_name(self.db, name)
            # print cids
            if 0 < len(cids) < 3:
                for cid in cids:
                    flag, confidence = self.scorer.compare(cid, name=name, title=record['title'],
                                                           content=' '.join([content['content'] for content in
                                                                             record['contents']]))
                    if flag or freq > 8:
                        yield int(cid), round(confidence * freq, 2)

    def find_candidates(self, record):

        candidates = {}

        # title
        found = [x.word for x in self.ner.chunk(record.get('title')) if x.flag == 'cn' and x.word.strip()]
        if 0 < len(found) < 3:
            for name in found:
                candidates[name] = candidates.get(name, 0) + self.weight_title

        # contents
        for content in record.get('contents', [])[:-1]:
            for name in [x.word for x in self.ner.chunk(content.get('content')) if x.flag == 'cn' and x.word.strip()]:
                weight = self.weight_front if int(content.get('rank')) < 4 else 1
                candidates[name] = candidates.get(name, 0) + weight

        return candidates


def clean(model='check', min_count=30):

    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()

    if model == 'check':
        cids = {}
        for record in mongo.article.news.find({'type': {'$in': [60001, 60002, 60003]}, 'processStatus': 1,
                                               'companyIds': {'$ne': []}}):
            for cid in record.get('companyIds', []):
                cids[cid] = cids.get(cid, 0) + 1
        for cid, count in sorted(filter(lambda y: y[1] > min_count, cids.iteritems()), key=lambda x: -x[1]):
            try:
                print dbutil.get_company_name(db, cid), cid, count
            except Exception, e:
                print cid, e
    if model == 'clear':
        clearids = map(lambda x: int(x), dicts.get_common_cid())
        for cid in clearids:
            print 'processing', cid
            for record in mongo.article.news.find({'companyIds': cid}):
                cids, confs = list(record['companyIds']), list(record['mention_confidence'])
                index = cids.index(cid)
                cids.remove(cid)
                del confs[index]
                print cid, cids, confs
                mongo.article.news.update({'_id': record['_id']},
                                          {'$set': {'companyIds': cids, 'mention_confidence': confs}})
    if model == 'dup':
        pass

    db.close()
    mongo.close()


def makeup():

    mongo = dbcon.connect_mongo()
    for record in mongo.article.news.find({'companyId': {'$ne': None}, 'type': {'$in': [60001, 60002, 60003]}}):
        cid = record['companyId']
        cids, confs = list(record.get('companyIds', [])), list(record.get('mention_confidence', []))
        if cid in cids:
            continue
        else:
            print cid, cids, confs
            cids.append(cid)
            confs.append(1)
            mongo.article.news.update({'_id': record['_id']},
                                      {'$set': {'companyIds': cids, 'mention_confidence': confs}})
    mongo.close()


if __name__ == '__main__':

    print __file__

    clean('check')

    # makeup()

    # cl = CompanyLinker()
    # # # cl.find_all()
    # # for result in cl.find(ObjectId('57c5235c4877af0b95ca829a')):
    # #     print result
    #
    # title = u'远程可视化诊疗+药物送货上门，痤疮诊疗公司 Curology 获 1500 万美元 B 轮融资'
    # contents = [
    #     {'rank': 0, 'content': u'David Lortscher 是新墨西哥州的一位皮肤科职业医师，他发现皮肤科诊疗领域存在一些问题：医师数量不足并且患者也往往会放弃去医院诊疗，因为他们认为皮肤科是面向高收入人群的一项服务，也有一部分患者是由于预约诊疗等待时间过长。于是，Lortscher 创办了痤疮定制配方远程医疗公司 Curology ，让患者不必再花费数月的时间迅速实现处方诊疗体验。'},
    #     {'rank': 1, 'content': u'从一个想法、五个人、一间居民楼到如今26人团队，400万＋用户，仅一年时间，蜗牛睡眠在不动声色间让自己的App蝉联App Store分类榜第一，做成了睡眠健康类的佼佼者。凭借专业睡眠报告、原创催眠音乐、浅睡唤醒闹钟，以及话题不断的梦话记录等功能，蜗牛睡眠App积攒了不少忠实用户，采访之际，高嵩也向猎云网分享了一些蜗牛睡眠用户主动晒出的睡眠体检报告，不禁感叹原来睡觉也可以如此有趣。'},
    #     {'rank': 2, 'content': u'就是这样一款人气App，最近又有了新动作，不仅在9月份上线了蜗牛睡眠3.0版本，而且还推出了一款帮助用户提高睡眠质量的智能型睡眠枕。'}
    # ]
    # record = {'title': title, 'contents': contents}
    # print cl.find_candidates(record)