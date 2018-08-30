# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon

import codecs
import itertools


def add_terms():

    db = dbcon.connect_torndb()

    companies = [line.strip().split('#') for line in codecs.open('dict/company_famous', encoding='utf-8')]
    companies = filter(lambda x: x.strip(), set(itertools.chain(*companies)))
    for c in companies:
        db.execute('insert into thesaurus (termName, termType, createTime, modifyTime) '
                   'values (%s, 43020, now(), now());', c)
    univs = [line.strip().split('#') for line in codecs.open('dict/university_985', encoding='utf-8')]
    univs = filter(lambda x: x.strip(), set(itertools.chain(*univs)))
    for u in univs:
        db.execute('insert into thesaurus (termName, termType, createTime, modifyTime) '
                   'values (%s, 42010, now(), now());', u)
    bats = [line.strip().split('#') for line in codecs.open('dict/bat', encoding='utf-8')]
    bats = filter(lambda x: x.strip(), set(itertools.chain(*bats)))
    for bat in bats:
        db.execute('insert into thesaurus (termName, termType, createTime, modifyTime) '
                   'values (%s, 43010, now(), now());', bat)

    univs = [line.strip().split('#') for line in codecs.open('dict/university_211', encoding='utf-8')]
    univs = filter(lambda x: x.strip(), set(itertools.chain(*univs)))
    univs985 = [line.strip().split('#') for line in codecs.open('dict/university_985', encoding='utf-8')]
    univs985 = set(filter(lambda x: x.strip(), set(itertools.chain(*univs985))))
    for u in univs:
        if u in univs985:
            continue
        db.execute('insert into thesaurus (termName, termType, createTime, modifyTime) '
                   'values (%s, 42020, now(), now());', u)

    db.close()


if __name__ == '__main__':

    add_terms()