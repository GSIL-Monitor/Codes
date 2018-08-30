# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from bson.objectid import ObjectId
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db, download
import pandas as pd

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import parser_db_util
import re

# logger
loghelper.init_logger("feixiaohao_marketdata_parser", stream=True)
logger = loghelper.get_logger("feixiaohao_marketdata_parser")

NULLVALUE = '-999'
lastFileName = None


def parse_mongo(df, fileName):
    # fileName = '/data/task-v2/spider2/crawler/blockchain/file/market_data_2018-03-2719:26:10.xls'
    date = datetime.datetime.strptime(re.findall('market_data_(.+).xls', fileName)[0], "%Y-%m-%d%H:%M:%S")
    mongo = db.connect_mongo()
    collectionfxhmarket = mongo.raw.feixiaohao_market

    if collectionfxhmarket.find_one({'date': date}) is None:
        logger.info('saving data for mongo date:%s', date)
        result = []
        for ix, row in df.iterrows():
            for c in row.index:
                if row[c] == NULLVALUE:
                    row[c] = None

            digitalToken = get_digitalToken(row[u'名称'])
            if digitalToken is not None:
                datamap = {'date': date,
                           'digitalTokenId': digitalToken['id'],
                           'circulationMarketValue': row[u'流通市值(¥)'],
                           'price': row[u'价格'],
                           'circulationQuantity': row[u'流通数量'],
                           'turnover24h': row[u'24H成交额'],
                           'increase24h': row[u'24H涨幅'],
                           'turnoverRate': row[u'换手率'],
                           'flowRate': row[u'流通率'],
                           'forkedCurrency': row[u'是否是分叉币'],
                           'crowdfundingAvgPrice': row[u'众筹均价'],
                           }
                result.append(datamap)

        collectionfxhmarket.insert_many(result)

    mongo.close()


def save_data_mongo(digitalTokenId, row, fileName):
    for c in row.index:
        if row[c] == NULLVALUE:
            row[c] = None

    # fileName = '/data/task-v2/spider2/crawler/blockchain/file/market_data_2018-03-2719:26:10.xls'
    date = datetime.datetime.strptime(re.findall('market_data_(.+).xls', fileName)[0], "%Y-%m-%d%H:%M:%S")

    mongo = db.connect_mongo()
    collectionfxhmarket = mongo.raw.feixiaohao_market

    if collectionfxhmarket.find_one({'digitalTokenId': digitalTokenId, 'date': date}) is None:
        logger.info('inserting into mongo digitalTokenId:%s|date:%s', digitalTokenId, date)
        collectionfxhmarket.insert({'date': date,
                                    'digitalTokenId': digitalTokenId,
                                    'circulationMarketValue': row[u'流通市值(¥)'],
                                    'price': row[u'价格'],
                                    'circulationQuantity': row[u'流通数量'],
                                    'turnover24h': row[u'24H成交额'],
                                    'increase24h': row[u'24H涨幅'],
                                    'turnoverRate': row[u'换手率'],
                                    'flowRate': row[u'流通率'],
                                    'forkedCurrency': row[u'是否是分叉币'],
                                    'crowdfundingAvgPrice': row[u'众筹均价'],
                                    })
    mongo.close()


def save_data(digitalTokenId, row):
    for c in row.index:
        if row[c] == NULLVALUE:
            row[c] = None

    conn = db.connect_torndb()
    dtm = conn.get('select * from digital_token_market where digitalTokenId=%s limit 1', digitalTokenId)
    if dtm is None:
        sql = "insert digital_token_market(digitalTokenId,circulationMarketValue,price,circulationQuantity,turnover24h,increase24h,turnoverRate,flowRate,forkedCurrency,crowdfundingAvgPrice,createTime,modifyTime) \
                          values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, digitalTokenId, row[u'流通市值(¥)'], row[u'价格'], row[u'流通数量'], row[u'24H成交额'], row[u'24H涨幅'],
                    row[u'换手率'], row[u'流通率'], row[u'是否是分叉币'], row[u'众筹均价'])
    else:
        sql = "update digital_token_market set circulationMarketValue=%s, price=%s, circulationQuantity=%s, turnover24h=%s, increase24h=%s, turnoverRate=%s, flowRate=%s, forkedCurrency=%s, crowdfundingAvgPrice=%s, modifyTime=now() where digitalTokenId=%s"
        conn.update(sql, row[u'流通市值(¥)'], row[u'价格'], row[u'流通数量'], row[u'24H成交额'], row[u'24H涨幅'], row[u'换手率'],
                    row[u'流通率'], row[u'是否是分叉币'], row[u'众筹均价'], digitalTokenId)
        if row[u'流通数量'] > dtm['totalCirculation']:
            logger.info('correct totalCirculation from %s to %s', dtm['totalCirculation'], row[u'流通数量'])
            conn.update('update digital_token_market set totalCirculation=%s where digitalTokenId=%s', row[u'流通数量'],
                        digitalTokenId)
    conn.close()


def get_digitalToken(fxhName):
    conn = db.connect_torndb()

    symbol = fxhName.split('-', 1)
    if fxhName.find('-') >= 0:
        digitalToken = conn.get('''select * from digital_token where symbol=%s and name=%s limit 1''', symbol[0],
                                symbol[-1])
    else:
        digitalToken = conn.get('''select * from digital_token where symbol=%s limit 1''', fxhName)

    conn.close()
    return digitalToken


def parse_data(fileName):
    # fileName = '/data/task-v2/spider2/crawler/blockchain/file/market_data_2018-03-2719:26:10.xls'

    import pandas as pd
    df = pd.read_excel(fileName).replace('?', NULLVALUE)
    df[u'是否是分叉币'] = df[u'是否是分叉币'].fillna(u'N').replace('是', 'Y')
    df = df.fillna(NULLVALUE)

    cnt = 0
    for ix, row in df.iterrows():
        digitalToken = get_digitalToken(row[u'名称'])
        if digitalToken is not None:
            logger.info('saving data for digitaltoken:%s|%s', row[u'名称'], digitalToken['id'])
            save_data(digitalToken['id'], row)
            # save_data_mongo(digitalToken['id'], row, fileName)
            cnt += 1
        else:
            logger.info('not found %s', row[u'名称'])
    logger.info('cnt:%s', cnt)

    parse_mongo(df, fileName)


def get_fileName():
    # path = '/data/task-201606/spider2/crawler/blockchain/file'
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/blockchain/file')
    lists = os.listdir(path)  # 列出目录的下所有文件和文件夹保存到lists
    lists.sort(key=lambda fn: os.path.getmtime(path + "/" + fn))  # 按时间排序
    file_new = os.path.join(path, lists[-1])  # 获取最新的文件保存到file_new

    # logger.info("fresh fileName:%s", file_new)
    return file_new


def run_history():
    path = '/data/task-201606/spider2/crawler/blockchain/file'
    lists = os.listdir(path)  # 列出目录的下所有文件和文件夹保存到lists
    for li in lists[596:]:
        fileName = os.path.join(path, li)
        try:
            parse_data(fileName)
        except:
            print '%s fail' % fileName


def bug_fix():
    columns = [i for i in
               'circulationMarketValue	price	circulationQuantity	turnover24h	increase24h	turnoverRate	flowRate	forkedCurrency	crowdfundingAvgPrice'.split()]
    # columns=['circulationMarketValue']
    for c in columns:
        mongo.raw.feixiaohao_market.update_many({c: NULLVALUE}, {'$set': {c: None}})


def start_run(flag):
    global lastFileName
    while True:
        newFileName = get_fileName()
        logger.info("last fileName %s", lastFileName)
        logger.info("now fileName %s", newFileName)
        if newFileName != lastFileName:
            logger.info("parser_feixiaohao_marketdata %s start...", flag)

            parse_data(newFileName)

            logger.info("parser_feixiaohao_marketdata %s end.", flag)
            lastFileName = newFileName

        if flag == "incr":
            time.sleep(60 * 5)  # 30 minutes
        else:
            exit()


if __name__ == '__main__':
    logger.info("Begin...")
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run("incr")
        elif param == "all":
            start_run("all")
    else:
        start_run("incr")
