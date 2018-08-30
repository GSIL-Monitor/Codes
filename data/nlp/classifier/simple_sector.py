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
from common.zhtools.segment import Segmenter
from common.zhtools import word_filter

import codecs
import numpy as np


class SimpleSectorClassifier(object):

    def __init__(self):

        self.sectors = [line.strip() for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                                          'config/simple_sector'), encoding='utf-8')]
        self.group_sector = {line.split('#')[0]: (set(line.split('#')[1].strip().split(',')) |
                                                  set([line.split('#')[0]]))
                             for line in codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                                                  'config/cluster_sector'), encoding='utf-8')}

    def classify(self, tags):

        for candidate in self.sectors:
            if candidate in tags:
                return candidate
        return u'其他'

    def classify2(self, tags):

        sector, count = u'其他', 0
        for k, v in self.group_sector.iteritems():
            overlap = len(set(tags) & v)
            if overlap > count:
                sector = k
                count = overlap
        return sector


class ClusterVIPClassifier():

    def __init__(self, sector_setting='default'):

        self.seg = Segmenter(tag=True)
        self.wfilter = word_filter.get_default_filter()
        self.vips = {}

        if sector_setting == 'new':
            sector_setting_file = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                               '../common/dict/vip.cluster.frozen')
        elif sector_setting == 'default':
            sector_setting_file = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                               '../common/dict/sector.cluster.frozen')
        else:
            sector_setting_file = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                               '../common/dict/sector.cluster.frozen')

        db = dbcon.connect_torndb()
        for line in codecs.open(sector_setting_file, encoding='utf-8'):
            vip, tags = line.split('#')[0].lower(), line.split('#')[1].strip().split(',')
            for tag in tags:
                try:
                    self.vips[tag.lower()] = (vip, dbutil.get_tag_novelty(db, tag, name=True)/len(tags))
                except Exception, e:
                    print tag, e
        db.close()

    def train(self, docs):

        pass

    def classify(self, doc, topn=1):

        result = {}
        doc = [word.lower() for word in self.wfilter(self.seg.cut(doc))]
        for word in doc:
            match = self.vips.get(word, (999, 0))
            result[match[0]] = result.get(match[0], 0) + match[1]
        if topn == 1:
            return sorted(result.iteritems(), key=lambda x: -x[1])[0]
        return sorted(result.iteritems(), key=lambda x: -x[1])[:topn]

    def classify_stream(self, docs, topn=1, stress=5):

        result = {}
        for index, doc in enumerate(docs):
            stress_weight = 1.5 if index < stress else 1
            for vip, weight in self.classify(doc, topn=topn*3):
                result[vip] = result.get(vip, 0) + weight * stress_weight
        if topn == 1:
            return sorted(result.iteritems(), key=lambda x: -x[1])[0]
        return sorted(result.iteritems(), key=lambda x: -x[1])[:topn]

    def classify_rules(self, record):

        if record.get('type', 0) == 60001 and record.get('source', 0) == 13807:
            return [8], [1]
        return False


def news_vip():

    # counts = {}

    cvipc = ClusterVIPClassifier()
    mongo = dbcon.connect_mongo()
    db = dbcon.connect_torndb()
    for record in list(mongo.article.news.find({'type': {'$in': [60001, 60002, 60003]}})):
        try:
            docs = [content['content'] for content in record.get('contents', [])]

            # vip, weight = cvipc.classify_stream(docs)

            results = cvipc.classify_stream(docs, topn=2)
            # process first sector
            vip, weight = results[0]
            if weight < 0.5:
                sids = [999]
                weights = [round(weight, 2)]
            else:
                sids = [db.get('select id from sector where sectorName=%s;', vip).id]
                weights = [round(weight, 2)]
            # process second sector
            if len(results) == 2 and results[1][1] >= 5:
                try:
                        vip, weight = results[1]
                        sids.append(db.get('select id from sector where sectorName=%s;', vip).id)
                        weights.append(round(weight, 2))
                except Exception, e:
                    print 'second sector error', record['_id'], e
            mongo.article.news.update({'_id': record['_id']}, {'$set': {'sectors': sids,
                                                                        'sector_confidence': weights}})
        except Exception, e:
            print 'error', record['_id'], e
    db.close()
    mongo.close()

    #     counts.setdefault(vip, []).append(weight)
    #
    # for k, v in counts.iteritems():
    #     print k, len(v), np.mean(v), np.median(v)

if __name__ == '__main__':

    print __file__

    # news_vip()
    # ssc = SimpleSectorClassifier()
    # print ssc.classify2(u'数据服务;大数据;人工智能;企业服务;BI商业智能;行业解决方案;企业服务'.split(';'))

    clf = ClusterVIPClassifier()
    record = {"contents" : [
                {
                    "content" : "",
                    "image" : "",
                    "image_src" : "https://pic.36krcnd.com/avatar/201608/29060932/hk9cl1zazf6tqqcu.jpg",
                    "rank" : 1
                },
                {
                    "content" : "根据彭博社的报道，苹果正在开发一款视频编辑工具，支持社交功能。目前苹果正在测试跟 iOS 系统相关的功能，这个新功能可能会利用到 iPhone 7 传闻中升级的摄像头。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 2
                },
                {
                    "content" : "知情人士称，这个新的应用程序可以让iPhone/iPad用户录制、并编辑分享视频，类似于Snapchat等社交软件。该应用被设计成只需要单手操作，而且使用该应用拍摄的视频可以截图、编辑和上传，且用时不到一分钟。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 3
                },
                {
                    "content" : "外媒评价称，苹果的硬件销量（iPhone、Mac等）正在放缓，CEO库克希望服务业务、如iCloud等增加营收，开发社交应用也是这方面的努力。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 4
                },
                {
                    "content" : "关于苹果意图加强社交功能的想法此前在iOS 10 系统升级中就有展现。例如在新版本的 iMessage 短信应用中，苹果增加了更多社交功能，例如大号 emoji 表情，更多的气泡和屏幕特效，以后还将支持第三方插件，这种改变明显会更贴近年轻人的社交习惯，",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 5
                },
                {
                    "content" : "苹果的这个新应用由Final Cut Pro和iMovie团队负责设计。负责人 Joe Weil 早前是纽约一家视频制作公司的主席，在 2015 年 12 月加入到苹果，早前开发了一款名为 KnowMe 的视频工具。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 6
                },
                {
                    "content" : "有评论称苹果做这款操作简单的视频编辑工具，主要还是想吸引年轻用户，直接应对社交网站 Facebook和阅后即焚 Snapchat。Facebook此前曾推出了多款独立社交应用，不少模仿了抓住了一二十岁年轻人的 Snapchat，例如阅后即焚、图片和视频社交。这些尝试都没获得什么成绩，最终，推出这些应用的创意实验室也于去年年底关闭。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 7
                },
                {
                    "content" : "该应用面临的另一个风险是如果苹果内部专门的隐私审核团队认为这款应用会暴露太多用户信息，也可能否决它的社交功能。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 8
                },
                {
                    "content" : "据了解，苹果计划或将在在2017年发布这款应用。",
                    "image" : "",
                    "image_src" : "",
                    "rank" : 9
                }
            ],
            "processStatus" : 1,
            "title" : "据说为了吸引年轻人，苹果正在开发一款类似Snapchat的视频社交软件"}

    docs = [record['title']]
    docs.extend([content['content'] for content in record.get('contents', [])])
    results = clf.classify_stream(docs, topn=2)

    for k, v in results:
        print k, v