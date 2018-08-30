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
from common.zhtools import stopword
from key import Extractor

import codecs


def dump_thesaurus(theme='source', topn=1000):

    db = dbcon.connect_torndb()
    seg = Segmenter()
    stopwords = stopword.get_standard_stopwords()
    tags = set(x.name for x in db.query('select name from tag where type>11001;'))
    vocab = {}

    if theme == 'source':
        query = 'select * from source_company where (active is null or active="Y");'
    else:
        query = 'select * from source_company where (active is null or active="Y");'

    for index, item in enumerate(db.iter(query)):
        for word in set(filter(lambda x: x not in stopwords and
                        len(x) > 1 and not x.isnumeric() and x not in tags and x.strip(), seg.cut(item.description))):
            vocab[word] = vocab.get(word, 0) + 1
        if index % 10000 == 0:
            low = [x[0] for x in vocab.iteritems() if x[1] < 20]
            for lowword in low:
                vocab.pop(lowword)
            print index, 'processed, size of vocab', len(vocab)
    db.close()

    vocab = sorted(vocab.iteritems(), key=lambda x: x[1], reverse=True)[:topn]
    with codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                  'thesaurus/%s.%s.lowidf' % (theme, topn)), 'w', 'utf-8') as fo:
        fo.write('\n'.join([x[0] for x in vocab]))


def import_tags(tags, ttype):

    db = dbcon.connect_torndb()
    for tag in tags:
        dbutil.update_tag_type(db, tag, ttype)
    db.close()


def compare():

    db = dbcon.connect_torndb()
    e = Extractor()
    with codecs.open('dumps/20170903', 'w', 'utf-8') as fo:
        for line in codecs.open('dumps/20170902', encoding='utf-8'):
            code = line.split('\t')[0]
            c = db.get('select id from company where code=%s;', code)
            __compare(c, fo, db, e)


def __compare(c, fo, db, e):

    old = db.query('select tag.name name from tag, company_tag_rel rel where tagId=tag.id and tag.type=11012 '
                   'and companyId=%s and (rel.active is null or rel.active="Y")', c.id)
    old = ','.join([v.name for v in old])
    e.extract(c.id)
    new = db.query('select tag.name name from tag, company_tag_rel rel where tagId=tag.id and tag.type=11012 '
                   'and companyId=%s and (rel.active is null or rel.active="Y")', c.id)
    new = ','.join([v.name for v in new])
    fo.write('%s\t%s\t%s\t%s\t%s\n' % (dbutil.get_company_code(db, c.id), dbutil.get_company_name(db, c.id),
                                       dbutil.get_company_brief(db, c.id), old, new))


if __name__ == '__main__':

    compare()