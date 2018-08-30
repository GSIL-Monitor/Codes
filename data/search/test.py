# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

import db as dbcon
import config
from client import SearchClient
from api.views.collection import update_collection


import time
import logging
import commands
from collections import defaultdict
from elasticsearch import Elasticsearch


# logging
logging.basicConfig(level=logging.INFO, format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
logger_st = logging.getLogger('search test')


def speed(run=10, search='company', server_id=1):

    if server_id == 2:
        server = 'http://10.27.83.226:5001/api/search'
    else:
        server = 'http://60.205.3.49:5001/api/search'

    search_mode = {'company': '{"payload": {"input": "", "start": 0, "size": 10, "filter": {}}}',
                   'event': '{"payload": {"start": 0, "size": 10, "filter": {}}}',
                   'industry': '{"payload": {"input": "", "start": 0, "size": 10, "filter": {}}}',
                   'investor': '{"payload": {"input": "", "start": 0, "size": 10, "filter": {}}}',
                   'topic': '{"payload": {"input": "", "start": 0, "size": 10}}'}

    server = server + 'universal_%s' % search if search != 'company' else server + 'universal'
    cmd = """ curl -H "Content-type: application/json" -X POST -d '%s' %s """ % (search_mode[search], server)

    db = dbcon.connect_torndb()

    if search == 'topic':
        names = db.query('select topicId from topic_company where active is null or active="Y" order by rand() limit %s;' % (run))
        names = set(name.topicId for name in names)
    elif search in ['event', 'investor']:
        names = db.query('select name from investor where active is null or active="Y" order by rand() limit %s;' % (run))
        names = set(name.name for name in names)
    else:
        names = db.query('select name from %s where active is null or active="Y" order by rand() limit %s;' % (search, run))
        names = set(name.name for name in names)


    db.close()

    logger_st.info('test %s\n' % search)

    start = time.time()
    for name in names:
        logger_st.info('item: %s' % name)
        logger_st.info(cmd % name)
        result = commands.getoutput(cmd % name)
        logger_st.info('\n%s\n' % result)

    end = time.time()
    logger_st.info('test search %s' % search)
    logger_st.info('total: %f' % (end - start))
    logger_st.info('average: %f\n' % (float(end - start)/run))


def test(search=None, sort=None, start=0, size=10, verbose=0, server_id=1):

    if server_id == 2:
        server = 'http://10.27.83.226:5001/api/search/'
    else:
        server = 'http://10.25.142.96:5001/api/search/'

    input_cmd = '{"payload": {"input": "%s", "filter": {}, "sort": %s, "start": %s, "size": %s}}'
    investor_cmd = '{"payload": {"filter": {"investor": ["%s"]}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    investorId_cmd = '{"payload": {"filter": {"investorId": [%s]}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    industryId_cmd = '{"payload": {"input": "", "industry": %s, "filter": {}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    tag_cmd = '{"payload": {"input": "", "filter": {"tag": ["%s"]}, "sort": %s, "start": %s, "size": %s}}'
    date_cmd = '{"payload": {"input": "", "filter": {"date": [%s]}, "sort": %s, "start": %s, "size": %s}}'
    round_cmd = '{"payload": {"input": "", "filter": {"round": [%s]}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    location_cmd = '{"payload": {"input": "", "filter": {"location": [%s]}, "sort": %s, "start": %s, "size": %s}}'
    funding_date_cmd = '{"payload": {"filter": {"funding_date": ["%s"]}, "sort": %s, "start": %s, "size": %s}}'
    source_cmd = '{"payload": {"filter": {"source": ["%s"]}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    status_cmd = '{"payload": {"input": "", "filter": {"status": [%s]}, "sort": %s, "order": "desc", "start": %s, "size": %s}}'
    topic_cmd = '{"payload": {"input": "", "topic": %s, "sort": %s, "order": "desc", "start": %s, "size": %s}}'

    search_mode = {'company': {'company': input_cmd, 'tag': tag_cmd, 'date': date_cmd, 'round': round_cmd, 'location': location_cmd},
                   'event': {'tag': tag_cmd, 'investor': investor_cmd, 'investorId': investorId_cmd, 'round': round_cmd,
                             'date': date_cmd, 'funding_date': funding_date_cmd, 'source': source_cmd},
                   'industry': {'industry': input_cmd, 'industryId': industryId_cmd, 'tag': tag_cmd, 'round': round_cmd, 'status': status_cmd},
                   'investor': {'investor': input_cmd, 'tag': tag_cmd, 'round': round_cmd},
                   'topic': {'topic': topic_cmd, 'tag': tag_cmd, 'round': round_cmd, 'status': status_cmd}}

    db = dbcon.connect_torndb()

    company = db.query('select name from company where active is null or active="Y" order by rand() limit 5;')
    company = set(c.name for c in company)

    investor = db.query('select name, id from investor where online = "Y" and (active is null or active="Y") order by rand() limit 5;')
    investorId = set(i.id for i in investor)
    investor = set(i.name for i in investor)

    industry = db.query('select name, id from industry where active is null or active="Y" order by rand() limit 5;')
    industryId = set(i.id for i in industry)
    industry = set(i.name for i in industry)

    tag = db.query('select distinct(t.id), name from company_tag_rel c join tag t on c.tagId = t.id'
                   ' where (c.active="Y" or c.active is null) and (t.type not in (11000, 11001, 11002, 11100)'
                   ' or t.type is null) order by rand() limit 5;')

    tag = set(t.name for t in tag)

    date = {2016, 2017, 2018}

    round = db.query('select distinct(round) from company where round is not null and (active is null or active="Y") order by rand() limit 5;')
    round = set(r.round for r in round)

    location = db.query('select location.locationId from location order by rand() limit 5')
    location = set(l.locationId for l in location)

    funding_date = {'latest7', 'latest30', 'latest90'}

    source = {69001, 69002, 69999}

    status = {-1, -2, 2020, 2025}

    topic = db.query('select distinct(topicId) from topic_company where active is null or active="Y" order by rand() limit 5;')
    topic = set(t.topicId for t in topic)

    fields = {'company': company, 'investor': investor, 'investorId': investorId, 'industry': industry, 'industryId': industryId, 'tag': tag,
              'date': date, 'round': round, 'location': location, 'funding_date': funding_date, 'source': source, 'status': status, 'topic': topic}

    db.close()

    searches = search or search_mode.keys()
    sorts = sort or range(76001, 76011) + [76020]
    logger_st.info(searches)
    bugs = defaultdict(set)
    for sor in sorts:
        for se in searches:
            if sor == 76020 and se not in ['industry', 'topic']: continue
            for field in search_mode[se]:
                if sor == 76008 and (se != 'investor' or field != 'tag'): continue
                se_server = server + 'universal_%s' % se if se != 'company' else server + 'universal'
                cmd = """ curl -H "Content-type: application/json" -X POST -d '%s' %s""" % (search_mode[se][field], se_server)
                for f in fields[field]:
                    logger_st.info('check doc: %s; field: %s %s; sort by:%s' % (se, field, f, sor))
                    fcmd = cmd % (f, sor, start, size)
                    result = commands.getoutput(fcmd)
                    if not ('"code":0' in result or '"code": 0' in result):
                        bugs[sor].add('doc: %s field:%s %s 500 Internal Server Error' % (se, field, f)) if '500 Internal' in result\
                            else bugs[sor].add('doc: %s field:%s %s %s' % (se, field, f, result))
                        logger_st.info(fcmd)
                        logger_st.info('\n%s\n' % result)
                    else:
                        result = result[result.index('"code"') - 2:].replace('false', 'False').replace('true', 'True')
                        try:
                            result = eval(result)
                        except Exception:
                            logger_st.info(result)
                        else:
                            map = {'company': 'company', 'topic': 'company', 'industry': 'company', 'investor': 'investor', 'event': 'funding'}
                            count = result[map[se]]['count']
                            if count == 0:
                                bugs[sor].add('doc: %s field:%s %s No search results' % (se, field, f))
                                logger_st.info(fcmd)
                            if count > 226000:
                                bugs[sor].add('doc: %s field:%s %s Full search results' % (se, field, f))
                                logger_st.info(fcmd)
                            if verbose:
                                logger_st.info('\n%s\n' % result)
                            logger_st.info('count: %s' % (count))
                            logger_st.info('check pass\n')
        return bugs


def case():
    pass


if __name__ == '__main__':

    # speed(search='company')
    # speed(search='investor')
    # speed(search='industry')
    # speed(search='topic')
    # speed(search='event')
    # test(search=['topic'])
    # test(search=[76009])
    bugs = test(start=5, server_id=int(sys.argv[1]))
    logger_st.info("\n*******bugs*******\n")
    for sort in sorted(bugs.keys()):
        for field in sorted(bugs[sort]):
            print(sort, field)
