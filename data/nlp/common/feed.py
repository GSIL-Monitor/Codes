# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../keywords'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon
from common import dbutil, dicts
from common.zhtools import hants
from common.zhtools.segment import Segmenter
from common.zhtools.postagger import Tagger
from common.zhtools import stopword, word_filter
# from corpus import words_filtering

import logging
import fasttext
from zhon.hanzi import punctuation
from numpy import mean

# logging
logging.getLogger('feeder').handlers = []
logger_feeder = logging.getLogger('feeder')
logger_feeder.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_feeder.addHandler(stream_handler)


class Feeder(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()

        self.non_trusted_discount = 0.5
        self.brief_promote = 1.5
        self.trusted_sources = dicts.get_known_company_source()

        self.wfilter = word_filter.get_default_filter()
        self.seg = Segmenter(tag=True)

    def feed(self, cid, mode='default', quanlity='low'):

        feeds = {
            'default': self.__feed_default,
            'with_tag': self.__feed_with_tag
        }.get(mode, 'default')(cid)
        feeds = list(feeds)
        if quanlity == 'medium':
            ave = min(mean([feed[1] for feed in feeds]), 2)
            return filter(lambda x: x[1] >= ave, feeds)
        if quanlity == 'low':
            return feeds

    def feed_string(self, cid, mode='default'):

        feeds = list(self.feed(cid, mode, 'medium'))
        return ' '.join([feed[0].strip() for feed in feeds])

    def feed_seged(self, cid, feed_mode='default'):

        return self.wfilter(self.seg.cut(self.feed_string(cid, feed_mode)))

    def feed_seged_fine(self, cid, feed_mode='default'):

        return self.wfilter(self.seg.cut4search(self.feed_string(cid, feed_mode)))

    def feed_relevant_string(self, cid):

        pass

    def __feed_with_tag(self, cid):

        for feed in self.__feed_default(cid):
            yield feed
        for source_tag in dbutil.get_source_company_tags(self.db, cid, self.trusted_sources):
            if source_tag and source_tag.strip():
                yield source_tag, 2

    def __feed_default(self, cid):

        cscore = dbutil.get_company_score(self.db, cid, 37010)
        # company info
        info = dbutil.get_company_info(self.db, cid)
        score = 1.5 if cscore > 0.5 else 1
        if info.verify and info.verify == 'Y':
            score += 1
        if info.brief and info.brief.strip():
            yield self.__preprocess(info.brief.strip()), score
        if info.description and info.description.strip():
            yield self.__preprocess(info.description.strip()), score

        # source company
        for info in dbutil.get_source_company_infos(self.db, cid):
            discount = self.non_trusted_discount if info.source not in self.trusted_sources else 1
            if info.brief and info.brief.strip():
                yield self.__preprocess(info.brief.strip()), discount*self.brief_promote
            if info.description and info.description.strip():
                yield self.__preprocess(info.description.strip()), discount

        # iOS
        info = dbutil.get_recommend_artifact(self.db, cid)
        if info and info.description and info.description.strip():
            ascore = 1 if (info.verify and info.verify == 'Y') else 0.5
            yield self.__preprocess(info.description.strip()), ascore

    def __preprocess(self, content):

        # clean and narrow down candidates
        # 繁转简
        content = hants.translate(unicode(content))
        # 转小写
        content = content.lower()

        return content.strip()


class NewsFeeder(object):

    def __init__(self):

        self.seg = Segmenter(tag=True)
        self.wfilter = word_filter.get_default_filter()

    def feed(self, record, granularity='default'):

        global logger_feeder

        try:
            contents = self.wfilter(self.seg.cut(record['title'].replace('\n', ' ')))
            if record.get('original_tags', []) and isinstance(record.get('original_tags', []), list):
                contents.extend(record.get('original_tags', []))
            if granularity == 'fine':
                contents.extend(self.wfilter(self.seg.cut4search(' '.join([piece['content'].replace('\n', ' ')
                                                                           for piece in record['contents']]))))
            else:
                contents.extend(self.wfilter(self.seg.cut(' '.join([piece['content'].replace('\n', ' ')
                                                                    for piece in record['contents']]))))
            return contents
        except Exception, e:
            logger_feeder.error('Fail to feed, %s, %s' % (record['_id'], e))
            return []


class Filter(object):

    def __init__(self):

        self.stopwords = stopword.get_standard_stopwords()
        self.stopwords.update(punctuation)

    def filter(self, word):
        return word not in self.stopwords

    def filtermany(self, words):
        # words = words_filtering(words)
        return filter(lambda word: self.filter(word), words)


class FilterLocation(Filter):

    def __init__(self):

        super(FilterLocation, self).__init__()
        self.stopwords.update(stopword.get_stopwords('location'))


if __name__ == '__main__':

    feeder = Feeder()
    for content, weight in feeder.feed(958):
        print weight, content
    print feeder.feed_string(958)
