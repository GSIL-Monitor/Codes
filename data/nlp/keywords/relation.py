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
from common.zhtools.segment import Segmenter

import codecs
import logging
from gensim.models import Word2Vec

# logging
logging.getLogger('tags_rel').handlers = []
logger_tr = logging.getLogger('tags_rel')
logger_tr.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_tr.addHandler(stream_handler)


class TagRelationFinder(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        # self.tags = {t.name: (t.id, t.type)
        #              for t in dbutil.get_tags_by_type(self.db, [11000, 11010, 11011, 11012, 11013])}
        self.tags = {t.name: (t.id, t.type)
                     for t in dbutil.get_tags_by_type(self.db, [11011, 11012])}
        self.seg = Segmenter(itags=True)
        word2vec_model = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                      '../embedding/models/s400w3min20_20180118.binary.w2vmodel')
        self.w2v = Word2Vec.load(os.path.join(word2vec_model))

        self.similarity_threshold = 0.3
        self.max_candidates = {
            11000: 5,
            11010: 5,
            11011: 5,
            11013: 2
        }

    def update_relevant_tags(self, tid, t_type=None, t_name=None):

        if not t_type:
            t_type = dbutil.get_tag_info(self.db, tid, 'type')
        if not t_name:
            t_name = dbutil.get_tag_info(self.db, tid, 'name')
        for target_type in [11000, 11010, 11011, 11013]:
            candidates = [tag for tag, (_, t) in self.tags.items() if t == target_type]
            similarities = sorted([(tag, self.__get_similarity(t_name, tag)) for tag in candidates],
                                  key=lambda x: -x[1])[:self.max_candidates.get(target_type)]
            if len(filter(lambda x: x[1] > self.similarity_threshold, similarities)) == 0:
                similarities = []
            else:
                similarities = filter(lambda x: x[1] > self.similarity_threshold, similarities)
            for tag, weight in similarities:
                dbutil.update_tags_rel(self.db, tid, self.tags.get(tag)[0], weight, 54020)
        if t_type != 11012:
            candidates = [tag for tag, (_, t) in self.tags.items() if t == 11012]
            vip, weight = max([(tag, self.__get_similarity(t_name, tag)) for tag in candidates])
            dbutil.update_tags_rel(self.db, tid, self.tags.get(vip)[0], weight, 54020)

    def __get_similarity(self, t1, t2):

        if (t1 not in self.w2v.vocab) or (t2 not in self.w2v.vocab):
            return 0
        else:
            return self.w2v.similarity(t1, t2)

        # t1 = [w for w in self.seg.cut4search(t1) if w in self.w2v.vocab]
        # t2 = [w for w in self.seg.cut4search(t2) if w in self.w2v.vocab]
        # if (not t1) or (not t2):
        #     return 0
        # return self.w2v.n_similarity(t1, t2)

    def update_all(self):

        global logger_tr
        for t_name, (tid, t_type) in self.tags.items():
            try:
                logger_tr.info('Processing %s' % tid)
                self.update_relevant_tags(tid, t_type, t_name)
            except Exception, e:
                logger_tr.exception('Fail %s, due to %s' % (tid, e))


def update_tags_rel():

    trf = TagRelationFinder()
    trf.update_all()


def dump():

    db = dbcon.connect_torndb()
    with codecs.open('dumps/tags.rel', 'w', 'utf-8') as fo:
        for t in dbutil.get_tags_by_type(db, [11010, 11011, 11012, 11013]):
            rels = [(dbutil.get_tag_info(db, r.tag2Id, 'name'), dbutil.get_tag_info(db, r.tag2Id, 'type'))
                    for r in dbutil.get_tags_rel(db, t.id, type=54020)]
            fo.write('%s\t%s\t%s\n' % (t.type, t.name, ','.join([x[0] for x in rels if x[1] == 11011])))
            fo.write('%s\t\t%s\n' % (t.type, ','.join([x[0] for x in rels if x[1] == 11013])))
            fo.write('%s\t\t%s\n' % (t.type, ','.join([x[0] for x in rels if x[1] == 11010])))
            fo.write('%s\t\t%s\n' % (t.type, ','.join([x[0] for x in rels if x[1] == 11000])))
    db.close()


if __name__ == '__main__':

    update_tags_rel()
    # dump()
