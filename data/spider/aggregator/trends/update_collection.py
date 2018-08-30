# -*- coding: utf-8 -*-
import sys, os
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config
import loghelper


#logger
loghelper.init_logger("update_collection_rule", stream=True)
logger = loghelper.get_logger("update_collection_rule")


def update(collections):
    conn = db.connect_torndb();
    for collection in collections:
        if collection['rule'] is not None:
            if 'and' not in collection['rule']:
                logger.info(collection['id'])
                rule = json.loads(collection['rule'])
                newKeyword = {'and':[], 'or':[], 'not': []}
                newKeyword['and'] = rule['keyword']
                rule['keyword'] = newKeyword
                logger.info(rule)
                update_sql = "update collection set rule=%s where id=%s"
                conn.update(update_sql, json.dumps(rule), collection['id'])

    conn.close()


def begin():
    global cnt
    conn = db.connect_torndb()

    collections = conn.query("select * from collection where id > 229")
    update(collections)
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    begin()