# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbconfig
import config as tsbconfig
import dbutil
from search.client import SearchClient

import codecs
import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

import logging

# logging
logging.getLogger('cleaner').handlers = []
logger_cleaner = logging.getLogger('cleaner')
logger_cleaner.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
logger_cleaner.addHandler(stream_handler)


def clean_tags():

    db = dbconfig.connect_torndb()
    logger_cleaner.info("start to clean tags %s" % time.ctime())
    deleted = []
    # deleted = dbutil.rm_few_tags(db)
    # print 'few tags cleaned'
    try:
        deleted.extend(dbutil.rm_1char_tags(db))
        logger_cleaner.info("one char tag cleaned")
    except Exception, e:
        logger_cleaner.info("%s" % e)
    try:
        dbutil.rm_junk_tags(db)
        logger_cleaner.info("11001 tags cleaned")
    except Exception, e:
        logger_cleaner.info("%s" % e)

    db.execute('update tag set type=11000 where type is null and createUser is not null;')
    logger_cleaner.info("default tag type has been set")

    try:
        dbutil.update_tags_global_novelty(db)
        logger_cleaner.info("tag novelty updated")
    except Exception, e:
        logger_cleaner.info("novelty" % e)

    # rm 11001 tags from company_tag_rel
    t11001 = [tag.id for tag in db.query('select id from tag where type=11001;')]
    db.execute('delete from company_tag_rel where tagId in %s and createUser is not null;', t11001)
    # TODO LOGISSUE, report back which 11001 tags are tagged by user

    # update 11003 tags
    # TODO update and replace

    clients = []
    host, port = tsbconfig.get_es_config_1()
    clients.append(SearchClient(Elasticsearch([{'host': host, 'port': port}])))
    host, port = tsbconfig.get_es_config_2()
    clients.append(SearchClient(Elasticsearch([{'host': host, 'port': port}])))

    for client in clients:
        for tid in deleted:
            tid = 'k%s' % tid
            try:
                client.delete_index('completion', tid)
                print tid, 'index removed', time.ctime()
            except TransportError, te:
                pass
            except Exception, e:
                print tid, e, time.ctime()
    print 'tag cleaned, total %s, like %s' % (str(len(deleted)), ','.join([str(x) for x in deleted]))
    db.close()


def dirty():

    db = dbconfig.connect_torndb()
    dbutil.rm_waste_tags(db)
    db.close()


def rm_tag(name):

    db = dbconfig.connect_torndb()
    if db.get('select count(*) as count from thesaurus where termName=%s and termType<35030;', name).count > 0:
        db.execute('update thesaurus set termType=35001 where termName=%s and termType<35030;', name)
    else:
        db.execute('insert into thesaurus (termName, termType, createTime, modifyTime) '
                   'values (%s, 35001, now(), now());', name)
    tid = db.get('select id from tag where name=%s;', name)
    if (not tid) or (not tid.id):
        db.close()
        return
    tid = tid.id
    db.execute('delete from company_tag_rel where tagId=%s and (verify!="Y" or verify is null or active="N");', tid)
    db.execute('delete from tags_rel where tagId=%s', tid)
    db.execute('delete from tags_rel where tag2Id=%s', tid)
    try:
        db.execute('delete from tag where id=%s and (verify!="Y" or verify is null);', tid)
    except Exception, e:
        db.execute('update tag set type=11001 where id=%s', tid)
    db.close()


def re_link(tid1, tid2):

    db = dbconfig.connect_torndb()
    dbutil.re_link(db, tid1, tid2)
    db.close()


def relink_dup():

    db = dbconfig.connect_torndb()
    dups = db.query('select name, count(name) as c from tag where type=11010 group by name having c>1;')
    for dup in dups:
        tids = [x.id for x in db.query('select id from tag where name=%s and type=11010;', dup.name)]
        tid1 = tids[0]
        for tid2 in tids[1:]:
            dbutil.re_link(db, tid2, tid1)
    db.close()


def rmtags():

    with codecs.open('dict/tag.delete', 'r', 'utf-8') as f:
        for line in f:
            try:
                rm_tag(line.strip())
            except Exception, e:
                print line, e


def rmwastetags():

    db = dbconfig.connect_torndb()
    ab = set()
    for tag in db.query('select * from tag where (tag.createUser is not null and tag.createUser!=139)'):
        if tag.type == 11010 or tag.type == 11001:
            if db.get('select count(*) as c from company_tag_rel where tagId=%s and active="Y";', tag.id).c < 1:
                db.execute('update tag set type=11001, modifyTime=now(), modifyUser=19 where id=%s;', tag.id)
                print tag.name
            # if db.get('select count(*) as c from company_tag_rel where tagId=%s;', tag.id).c < 1:
            #     db.execute('update tag set type=11001, modifyTime=now(), modifyUser=19 where id=%s;', tag.id)
        else:
            ab.add(tag.name)
    # print '\n\n'
    # for tag in ab:
    #     print tag


def modify_tags():

    db = dbconfig.connect_torndb()
    # for index, line in enumerate([u'广告\t广告营销', u'电商\t电子商务']):
    for index, line in enumerate(codecs.open('dict/tag.modify', encoding='utf-8')):
        try:
            tags = [tag for tag in line.split('\t') if tag.strip()]
            if len(tags) < 2:
                continue
            if len(tags) == 2:
                if tags[0] == tags[1]:
                    continue
                elif tags[0].lower() == tags[1].lower():
                    db.execute('update tag set name=%s where name=%s;', tags[1], tags[0])
                else:
                    tid1, tid2 = dbutil.get_tag_id(db, tags[0].strip()), dbutil.get_tag_id(db, tags[1].strip())
                    dbutil.re_link(db, tid1, tid2)
            else:
                tid1 = dbutil.get_tag_id(db, tags[0])
                tid2s = [dbutil.get_tag_id(db, tag) for tag in tags[1:]]
                cids = [item.companyId for item in db.query('select companyId from company_tag_rel '
                                                            'where tagId=%s and (active="Y" or active is null);', tid1)]
                for cid in cids:
                    for tid2 in tid2s:
                        dbutil.update_company_tag(db, cid, tid2, 0.5)
        except Exception, e:
            print line.strip(), e
    db.close()


def check_famous_investor():

    db = dbconfig.connect_torndb()
    r = db.query("select id, name from investor where active='Y' or active is null;")
    investor_dict = {}

    for row in r:
        i = row["id"]
        name = row["name"]
        if i in investor_dict:
            investor_dict[i].append(name)
        else:
            investor_dict[i] = [name]

    r = db.query("select investorid, name from investor_alias where active='Y' or active is null;")
    for row in r:
        i = row["investorid"]
        name = row["name"]
        if i in investor_dict:
            investor_dict[i].append(name)

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/investors_famous')
    famous_list = [line for line in codecs.open(path, encoding='utf-8')]
    new_famous_list = []
    for line in famous_list:
        tup = line.strip().split('#')
        i = int(tup[0])
        name = tup[1]
        if i in investor_dict:
            new_famous_list.append(line)
        else:
            p = False
            for j, jnames in investor_dict.iteritems():
                if name in jnames:
                    p = j
            if p:
                new_line = str(p) + '#' + name
                new_famous_list.append(new_line)
                print i, name, p
            else:
                new_famous_list.append(line)
                print i, name
    new_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'dict/investors_famous.bak')
    with codecs.open(new_path, mode='w' ,encoding='utf-8') as f:
        for line in new_famous_list:
            f.write(line.strip())
            f.write('\n')
    db.close()


def daily_news():

    db = dbconfig.connect_torndb()
    dbutil.clear_tag(db, 574419, True)
    db.close()


if __name__ == '__main__':

    if sys.argv[1] == 'tag':
        clean_tags()
    elif sys.argv[1] == 'dirty':
        dirty()
    elif sys.argv[1] == 'rmtag':
        rm_tag(sys.argv[2])
    elif sys.argv[1] == 'link':
        re_link(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'rmduptag':
        relink_dup()
    elif sys.argv[1] == 'rmtags':
        rmwastetags()
        # rmtags()
    elif sys.argv[1] == 'modify':
        modify_tags()
    elif sys.argv[1] == 'investor':
        check_famous_investor()
    elif sys.argv[1] == 'dailynews':
        daily_news()