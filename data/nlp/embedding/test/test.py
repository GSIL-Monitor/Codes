# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.setdefaultencoding('utf-8')

# import db as dbcon

import json
import codecs
from gensim.models import Word2Vec


# def dump_w2v():
#
#     db = dbcon.connect_torndb()
#     tags = set(map(lambda tag: tag.name, db.query('select distinct name from tag where type!=11001;')))
#     model = Word2Vec.load('models/20160407.binary.w2vmodel')
#     with codecs.open('tmp/dict', 'w', 'utf-8') as fo:
#         for tag in tags:
#             try:
#                 similars = [x for x in model.most_similar(positive=[tag.lower()], topn=50) if x[0] in tags]
#                 if not similars:
#                     continue
#                 similars = sorted(similars, key=lambda x: x[1], reverse=True)[:5]
#                 fo.write('%s#%s\n' % (tag.lower(), json.dumps(dict(similars)).decode('utf-8').encode('utf-8')))
#             except:
#                 print tag, 'not in vocab'
#     db.close()


def check_w2v():

    simis = {line.split('#')[0].strip(): json.loads(line.split('#')[1])
             for line in codecs.open('tmp/dict', encoding='utf-8')}

    # if word in simis:
    #         for k, v in simis.get(word).iteritems():
    #             print k, v

    while True:
        word = unicode(raw_input('word:\n').strip().lower())
        if word in simis:
            for k, v in simis.get(word).iteritems():
                print k, v
        else:
            print 'not a tag', word


if __name__ == '__main__':

    print __file__
    # dump_w2v()
    check_w2v()