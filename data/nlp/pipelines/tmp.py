# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from common.zhtools.ner import SimpleNER
from emailer import Email

import codecs


def record_mail():

    db = dbcon.connect_torndb()
    for email in db.query('select id, name, content from coldcall;'):
        eid, name, content = email.id, email.name, email.content
        with codecs.open('tmp/raw/%s' % eid, 'w', 'utf-8') as fo:
            fo.write('%s#%s\n' % (eid, name))
            fo.write(content)
    db.close()


def split_lines():

    for f in os.listdir('tmp/raw'):
        with codecs.open(os.path.join('tmp/line', f), 'w', 'utf-8') as fo:
            content = codecs.open(os.path.join('tmp/raw', f), encoding='utf-8').read()
            email = Email('', content)
            email.preprocess()
            email.record(fo)


def link2c():

    db = dbcon.connect_torndb()
    ner = SimpleNER()
    try:
        ner.train()
    except Exception, e:
        print e
    for f in os.listdir('tmp/line'):
        try:
            with codecs.open(os.path.join('tmp/link', f), 'w', 'utf-8') as fo:
                content = codecs.open(os.path.join('tmp/line', f), encoding='utf-8', errors='ignore').readlines()
                email = Email(title=content[0].split('##')[-1], original=content[1:])
                names, ids = email.link2company(db, ner)
                fo.write('%s##%s\n' % ('\t'.join(names), '\t'.join([str(x) for x in ids])))
                fo.write(''.join(content))
        except Exception, e:
            print f, e
    db.close()

if __name__ == '__main__':
    record_mail()