# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import my_request
import util
import db
import extract
import aggregator_util
import trends_tool

def merge_cf(source_cf_id):

    source_cf = mysqldb.get('select * from source_crowdfunding where id = %s', source_cf_id)

    cf_id = match_cf(source_cf)
    if cf_id is None:
        cf_id = insert_crowdfunding(source_cf)
        update_source_crowdfunding(source_cf_id,cf_id)

    else:
        update_crowdfunding(source_cf)

        # aggregator_util.insert_cf_leader(cf_id, source_cf_id)
        # aggregator_util.insert_cf_document(cf_id, source_cf_id)



def match_company(source_cf):
    source_company = mysqldb.get('select * from source_company where source=%s and sourceId=%s',
                                 source_cf['source'], source_cf['sourceCompanyId'])

    if source_company is not None:
        return source_company['companyId']


def match_cf(source_cf):
    crowdfunding = mysqldb.get('select * from crowdfunding where name=%s', source_cf['name'])
    if crowdfunding is not None:
        return crowdfunding['id']


def insert_crowdfunding(source_cf):
    s = source_cf
    sql = 'insert crowdfunding (name, description, amountRaising, successRaising, coinvestorCount,' \
          'minInvestment, currency, startDate, endDate, preMoney,' \
          'postMoney, status, active, createTime)' \
          'values' \
          '(%s, %s, %s, %s, %s, ' \
          '%s, %s, %s, %s, %s, ' \
          '%s, %s, %s, now())'

    cf_id = mysqldb.insert(sql, s['name'], s['description'], s['maxRaising'], s['successRaising'], s['coinvestorCount'],
                   s['minInvestment'], s['currency'], s['startDate'], s['endDate'], s['preMoney'],
                   s['postMoney'], s['status'], 'Y')
    return cf_id

def update_crowdfunding(source_cf):
    sql = 'update  crowdfunding set ' \
          ' description =%s, successRaising=%s, coinvestorCount=%s, status=%s, modifyTime=%s' \
          ' where id = %s'

    mysqldb.update(sql, source_cf['description'], source_cf['successRaising'], source_cf['coinvestorCount'],
                  source_cf['status'], source_cf['cfId'])



def update_source_crowdfunding(source_cf_id,cf_id):
    sql = 'update source_crowdfunding set cfId = %s where id = %s'
    mysqldb.update(sql, cf_id, source_cf_id)


def merge_patch(source_cf_id):
    source_cf = mysqldb.get('select * from source_crowdfunding where id = %s', source_cf_id)
    if source_cf != None:
        mysqldb.update('update crowdfunding set description = %s where id = %s',
                       source_cf['description'], source_cf['cfId'])



if __name__ == '__main__':
    spider_name = "cf_aggregator"
    (logger, fromdb, mysqldb, kafka_producer, kafka_consumer) = aggregator_util.aggregator_init(spider_name)
    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
			                                         message.offset, message.key,
			                                         message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    source_cf_id = msg["id"]
                    if type == "cf":
                        merge_cf(source_cf_id)

                    if type == "jd_patch":
                        merge_patch(source_cf_id)

                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, mysqldb, kafka_producer, kafka_consumer) = aggregator_util.aggregator_init(spider_name)