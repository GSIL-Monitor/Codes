# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import logging
from elasticsearch.exceptions import NotFoundError

import db as dbconnection
# from search import SearchClient
from nlp.common import dbutil

# logging
logging.getLogger('search').handlers = []
logger_search = logging.getLogger('search')
logger_search.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_search.addHandler(stream_handler)


def delete_nonactive(es):

    global logger_search

    db = dbconnection.connect_torndb()
    # es = SearchClient()

    for cid in dbutil.get_nonactive_company(db):
        try:
            delete_company(db, es, cid)
            logger_search.info('%s deleted' % cid)
        except NotFoundError, ne:
            logger_search.info('%s not found' % cid)
        except Exception, e:
            logger_search.exception('Error, %s failed # %s' % (cid, e))

    # __delete_single(db, es, 89995)


def delete_company(db, es, cid):

    # 1. completion
    completion2delete = set()
    completion2delete.add('c%s' % cid)
    # full name
    completion2delete.add('f%s' % cid)
    # artifact name
    aresults = dbutil.get_artifact_idname_from_cid(db, cid)
    if aresults:
        for aresult in aresults:
            aid, aname = aresult
            completion2delete.add('a%s' % aid)
    # alias
    aliass = dbutil.get_alias_idname(db, cid)
    if aliass and len(aliass) < 10:
        for aid, aname in aliass:
            completion2delete.add('n%s' % aid)
    for c in completion2delete:
        try:
            es.delete_index('completion', c)
        except NotFoundError, ne:
            continue

    # 2. company
    code = dbutil.get_company_code(db, cid)
    es.delete_index('company', code)


def delete_alias(es, aid):

    es.delete_index('completion', 'n%s' % aid)


def delete_artifact(es, aid):

    es.delete_index('completion', 'a%s' % aid)


if __name__ == '__main__':

    print __file__
    # es = SearchClient()
    # delete_nonactive()