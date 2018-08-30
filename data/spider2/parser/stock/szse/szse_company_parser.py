# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq
import datetime, time
import json, re, copy

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

# logger
loghelper.init_logger("parser_szse", stream=True)
logger = loghelper.get_logger("parser_szse")

# mongo
mongo = db.connect_mongo()
collection = mongo.stock.szse

SOURCE = 13402
TYPE = 36001


def save_collection(collection_name, item):
    record = collection_name.find_one({'source': item['source'], "sourceId": item["sourceId"]})
    item['sourceId_str'] = str(item['sourceId']) if item['source'] != 13402 else item['stockwebsite'].split('code=')[-1]

    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        item["processStatus"] = 0
        item["active"] = None
        item["verify"] = None
        id = collection_name.insert(item)
    else:
        id = record["_id"]
        item['createTime'] = record['createTime']
        # item["modifyTime"] = record['modifyTime']

        histories = []
        if record.has_key("histories"):
            histories = record.pop('histories')

        record.pop('_id')
        recordNew = copy.deepcopy(record)
        for i in ['processStatus', 'active', 'verify', 'modifyTime']: recordNew.pop(i)
        if recordNew.has_key("memectBrief"): recordNew.pop("memectBrief")
        if recordNew.has_key("jqkaBrief"): recordNew.pop("jqkaBrief")

        if item == recordNew:
            logger.info('%s has no update', item['name'])
        elif item != recordNew:
            logger.info('%s changed', item['name'])
            for i in recordNew:
                if not item.has_key(i):
                    logger.info('%s,old:%s ,new:None', i, record[i])
                else:
                    if item[i] != recordNew[i]:
                        logger.info('%s,old:%s , new:%s', i, recordNew[i], item[i])

            histories.append(record)
            item["processStatus"] = 0
            item["active"] = None
            item["verify"] = None

        item['histories'] = histories
        item["modifyTime"] = datetime.datetime.now()
        collection_name.update_one({"_id": id}, {'$set': item})
    return id


def parseContent(content):
    contentNew = content
    # print content,type(content)
    if isinstance(content, basestring):
        try:
            contentNew = int(content)
        # print content
        except:
            try:
                contentNew = float(content)
            except:
                try:
                    contentNew = content.decode('utf-8')
                except:
                    contentNew = content

    if isinstance(content, list):
        for j in content:
            contentNew[content.index(j)] = parseContent(j)
    if isinstance(content, dict):
        for j in content:
            contentNew[j] = parseContent(content[j])
    return contentNew


def process():
    skip = 0
    limit = 1000

    num = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, skip, limit)
        # items = [parser_db_util.find_process_one(SOURCE, TYPE, 837630)]

        # skip += limit
        for c in items:
            num += 1

            logger.info("%s: %s" % (num, c["key"]))

            content = c['content']
            d = pq(html.fromstring(content))
            name = d(':contains("公司名称")+ td').text()
            if c["content"] is None:
                logger.info('%s content is None', c["key"])
                parser_db_util.update_processed(c["_id"])
                continue

            if name is None or name == '':
                logger.info('%s missing fullName', c["key"])
                parser_db_util.update_processed(c["_id"])
                continue

            stockwebsite = 'http://www.szse.cn/main/marketdata/hqcx/hqlb/index.shtml?code=%s' % c['key']
            listingDate = d(':contains("A股上市日期")+ td').text()
            listingDate = datetime.datetime.strptime(listingDate, '%Y-%m-%d') if len(listingDate) > 0 else ''
            website = d(':contains("公司网址")+ td').text()

            parserContent = {
                "source": SOURCE,
                "sourceId": int(c['key']),
                "stockwebsite": stockwebsite,
                "website": website,
                'listingDate': listingDate

            }

            # content['stamp'] = datetime.datetime.strptime(re.sub('\..+', '', content['stamp']), '%Y-%m-%d %H:%M:%S')
            # content['baseinfo']['listingDate']=datetime.datetime.strptime(content['baseinfo']['listingDate'], '%Y%m%d')

            # if content.has_key('executives'):
            #     for executive in content['executives']:
            #         dateTransed = datetime.datetime.strptime(executive['START_TIME'], '%Y-%m-%d')
            #         content['executives'][content['executives'].index(executive)]['START_TIME'] = dateTransed

            # content = parseContent(content)

            # parserContent.update(content.pop('baseinfo'))
            # content['baseinfo'] = content['baseinfo'][0]
            parserContent['baseinfo'] = {
                'shortname': d(':contains("A股简称")+ td').text(),
                'englishName': d(':contains("英文名称")+ td').text(),
                'regLocation': d(':contains("注册地址")+ td').text(),
                'totalStockEquity': d(':contains("A股总股本")+ td').text(),
                'region': d(':contains("地      区")+ td').text(),
                'province': d(':contains("省    份")+ td').text(),
                'city': d(':contains("城     市")+ td').text(),
                'industry': d(':contains("所属行业")+ td').text(),

            }
            parserContent['executives'] = []

            parserContent['name'] = name

            # parserContent.update(content)

            logger.info(json.dumps(parserContent, ensure_ascii=False, cls=util.CJsonEncoder))

            save_collection(collection, parserContent)
            parser_db_util.update_processed(c["_id"])
            logger.info("processed %s", c["key"])

        # time.sleep(1)
        if len(items) == 0:
            logger.info("no more items")
            break


if __name__ == '__main__':
    while True:
        process()
        time.sleep(60)
