# -*- coding: utf-8 -*-
import os, sys
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
loghelper.init_logger("parser_neeq", stream=True)
logger = loghelper.get_logger("parser_neeq")

# mongo
mongo = db.connect_mongo()
collection = mongo.stock.neeq

SOURCE = 13400
TYPE = 36001


def save_collection(collection_name, item):
    record = collection_name.find_one({"sourceId": item["sourceId"]})
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

            if c['content'].has_key("baseinfo") is False:
                c['content']["baseinfo"]=c['content']["bbseinfo"]

            if c["content"] is None or (c['content'].has_key('ret') and c['content']['ret'] == -999):
                logger.info('%s content is None', c["key"])
                parser_db_util.update_processed(c["_id"])
                continue
            if c['content']["baseinfo"].has_key("name") is False:
                logger.info('%s missing fullName', c["key"])
                parser_db_util.update_processed(c["_id"])
                continue

            content = c['content']

            stockwebsite = 'http://www.neeq.com.cn/nq/detailcompany.html?companyCode=%s&typeId=1&typename=G' % c['key']

            content['stamp'] = datetime.datetime.strptime(re.sub('\..+', '', content['stamp']), '%Y-%m-%d %H:%M:%S')
            content['baseinfo']['listingDate'] = datetime.datetime.strptime(content['baseinfo']['listingDate'],
                                                                            '%Y%m%d')

            if content.has_key('topTenHolders'):
                for holder in content['topTenHolders']:
                    dateTransed = datetime.datetime.strptime(holder['date'], '%Y-%m-%d')
                    content['topTenHolders'][content['topTenHolders'].index(holder)]['date'] = dateTransed

            parserContent = {
                "source": SOURCE,
                "sourceId": int(c['key']),
                "stockwebsite": stockwebsite,
                # "website":content['baseinfo']['website'],
                "name": content['baseinfo']['name'],
                "listingDate": content['baseinfo']['listingDate'],

            }

            content = parseContent(content)
            if content['baseinfo'].has_key('website'):
                parserContent["website"] = content['baseinfo']['website']

            # parserContent.update(content.pop('baseinfo'))
            parserContent.update(content)

            logger.info(json.dumps(parserContent, ensure_ascii=False, cls=util.CJsonEncoder))

            save_collection(collection, parserContent)
            parser_db_util.update_processed(c["_id"])
            logger.info("processed %s", c["key"])

        # time.sleep(1)
        if len(items) == 0:
            logger.info('no more new item')
            break


if __name__ == '__main__':
    while True:
        process()
        logger.info('neeq parser sleep******')
        time.sleep(60 * 60)
