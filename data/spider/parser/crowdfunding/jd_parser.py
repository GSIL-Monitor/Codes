# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random, json

from bson.objectid import ObjectId
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import requests
import util
import parser_util
from pyquery import PyQuery as pq


source = 13010
def parse_cf(cf_key):
    item = fromdb.cf.find_one({"source":source, "cf_key":cf_key})
    if item is None:
        return

    content = item["content"]
    html = content['html']
    d = pq(html)

    name = d('h2.s-s-tit').text()
    status = d('div.status').text()

    focus = content['focus']
    focus = json.loads(focus.replace('(', '').replace(')', ''))

    praiseCount = focus['data']['praise']
    focusCount = focus['data']['focus']

    support = json.loads(content['support'])
    djCount = support['mininumCount']
    xdjCount = support['silkmumAmount']
    coinvestors_count = int(djCount)+ int(xdjCount)


    if status == '路演中':
        status = 14010
    elif status == '融资中':
        status = 14020
    elif status == '融资成功':
        status = 14030
    else:
        status = 0


    desc = None
    cf_min_raising = None
    cf_max_raising = None
    max_coinvestor_number = None
    cf_success_raising = None
    time_left = None
    end_time = None

    table = d('s-s-cont')
    tds = pq(table)('td')


    if status == '路演中':
        desc = d('td:eq(0) > div').text()
    else:
        cf_max_raising =  d('td:eq(0) > span').text()
        max_coinvestor_number =  d('td:eq(1) > span').text()
        cf_success_raising =  d('td:eq(2) > span').text()
        time_left =  d('td:eq(3) > span').text()



    if '天' in time_left:
        day = time_left.replace('天', '')
        day = int(day)+1
        end_time = datetime.date.today() + datetime.timedelta(days=day)

    raising_arr = cf_max_raising.split('-')
    if len(raising_arr) == 2:
        cf_min_raising = raising_arr[0].replace('￥', '').replace(',', '').strip()
        cf_max_raising = raising_arr[1].replace('￥', '').replace(',', '').strip()
    else:
        cf_max_raising = cf_max_raising.replace('￥', '').replace(',', '').strip()

    cf_success_raising = cf_success_raising.replace('￥', '').replace(',', '').strip()



    if '万' in cf_max_raising:
        cf_max_raising = int(cf_max_raising.split('.')[0])* 10000

    if cf_min_raising is None:
        cf_min_raising = cf_max_raising
    elif '万' in cf_min_raising:
        cf_min_raising = int(cf_min_raising.split('.')[0])* 10000

    if '万' in cf_success_raising:
        cf_success_raising = int(cf_success_raising.split('.')[0])* 10000

    if cf_min_raising == '' or cf_min_raising is None:
        cf_min_raising = 0

    if cf_max_raising == '' or cf_max_raising is None:
        cf_max_raising = 0

    if cf_success_raising == '' or cf_success_raising is None:
        cf_success_raising = 0

    max_coinvestor_number = max_coinvestor_number.replace('人', '')

    # logger.info(name)
    # logger.info(cf_max_raising)
    # logger.info(max_coinvestor_number)
    # logger.info(cf_success_raising)
    # logger.info(time_left)
    # logger.info(praiseCount)
    # logger.info(focusCount)
    # logger.info(djCount)
    # logger.info(xdjCount)

    intro = d('.intro-noRight').text()
    intro = ''.join(intro)

    try:
        (postMoney,) = util.re_get_result(u"投后估值：(.*?)本轮融资金额", intro)
        postMoney = postMoney.strip()

        (value,) = util.re_get_result(u"本轮融资金额：(.*?) 本轮出让股权比例为", intro)
        value = value.strip()

        if u'亿' in postMoney:
            postMoney = int(postMoney.split(u'亿')[0]) * 10000
        else:
            postMoney = int(postMoney.split(u'万')[0])

        value = value.split(u'万')[0]

    except Exception, e :
        postMoney = None
        value = None





    currency = 3020
    source_crowdfunding = {
        'name': name,
        'description': desc,
        'coinvestorCount': coinvestors_count,
        'maxCoinvestorNum': max_coinvestor_number,
        'minRaising': cf_min_raising,
        'successRaising': cf_success_raising,
        'maxRaising': cf_max_raising,
        'minInvestment': 10000,
        'currency': currency,
        'startDate': None,
        'endDate': end_time,
        'preMoney': None,
        'postMoney': None,
        'status': status,
        'round': None,
        'roundDesc': None,
        'value': value,
        'tags': None,
        'accessCount': None,
        'likesCount': praiseCount,
        'followCount': focusCount,
        'painPoint': None,
        'marketSituation': None,
        'competitorAnalyze': None,
        'profitModel':None,
        'marketShare':None,
        'coreResources': None,
        'cfAdvantage': None,
        'advantageAnalysis': None,
        'companyVision': None,
        'companyDesc': desc,
        'bmSolution': None,
        'source': source,
        'sourceId': cf_key,
        'sourceCompanyId': None
    }

    source_cf_id = parser_util.insert_source_crowdfunding(source_crowdfunding)

    team = json.loads(content['team'])
    for member in team:
        member_name = member['ptRealname']
        photo_url = member['ptImg']
        member_desc =  member['ptIntroduce']
        member_position = member['ptTitle']
        sourceId = member['ptId']

        source_member = {'name': member_name,
                        'photo_url': photo_url,
                        'weibo':None,
                        'location':None,
                        'role': member_position,
                        'description': member_desc,
                        'education': None,
                        'work': None,
                        'source': source,
                        'sourceId': sourceId,
                         'sourceCfId': source_cf_id
                        }

        parser_util.insert_source_cf_member(source_member)


    leader = item['leader']
    source_investor_id = None
    investor_name = None
    if leader != None and leader != '':
        l = pq(leader)
        logo_url = pq(l('img:eq(0)')).attr('src')

        investor_name = l('h1:eq(0)').text()
        investor_desc = l('.desc').text()

        source_investor = {
            'name': investor_name,
            'website': None,
            'description': investor_desc,
            'logo_url': logo_url,
            'stage': None,
            'field': None,
            'type': 10020,
            'source': source,
            'sourceId': cf_key
        }
        source_investor_id = parser_util.insert_source_investor(source_investor)

    desc = d('div.stake-member-mesg > p').text()

    source_cf_leader = {
        'sourceCfId': source_cf_id,
        'investorName' :investor_name,
        'sourceInvestorId': source_investor_id,
        'investorType': 10020,
        'description': desc,
        'investment': None,
        'valuation':None,
        'businessDesc': None,
        'reason': None,
        'risk': None
    }

    parser_util.insert_source_cf_leader(source_cf_leader)


    #BP
    bp = item["bp"]
    if bp != None:
        bp_id = bp['bp_id']
        source_id = str(cf_key)+'_bp'
        source_cf_document = {
            'sourceCfId': source_cf_id,
            'name': None,
            'description': None,
            'link': bp_id,
            'rank': None,
            'sourceId': source_id,
            'type': 9010
        }
        parser_util.insert_source_cf_document(source_cf_document)


    video_path = pq(d('embed')).attr('src')
    source_id = str(cf_key)+'_video'
    source_cf_document = {
        'sourceCfId': source_cf_id,
        'name': None,
        'description': None,
        'link': video_path,
        'rank': None,
        'sourceId': source_id,
        'type': 9020
    }

    parser_util.insert_source_cf_document(source_cf_document)

    link = pq(d('.stake-speed > img')).attr('src')

    img_list = d('div.img-list')
    img_list.append(link)
    rank = 0
    for img in pq(img_list)('img'):
        link = pq(img).attr('src')
        rank += 1
        source_id = str(cf_key)+'_'+str(rank)

        link = parser_util.get_cf_pic_id(source_cf_id, source_id, link)

        source_cf_document = {
            'sourceCfId': source_cf_id,
            'name': None,
            'description': None,
            'link': link,
            'rank': rank,
            'sourceId': source_id,
            'type': 9030
        }

        parser_util.insert_source_cf_document(source_cf_document)


    msg = {"type":"cf", "id": source_cf_id}
    kafka_producer.send_messages("parser_v2", json.dumps(msg))


def parse_patch(cf_key):
    item = fromdb.cf.find_one({"source":source, "cf_key":cf_key})
    if item is None:
        return

    desc = item["desc"]

    source_cf_id = parser_util.update_source_cf_desc(cf_key, desc)

    msg = {"type":"jd_patch", "id": source_cf_id}
    kafka_producer.send_messages("parser_v2", json.dumps(msg))




if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("cf_jd", "crawler_cf_jd_v2")

    while True:
        try:
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    cf_key = msg["cf_key"]

                    if type == "cf":
                        parse_cf(cf_key)

                    if type == 'jd_patch':
                        parse_patch(cf_key)

                    kafka_consumer.task_done(message)
                    kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("cf_jd", "crawler_cf_jd_v2")
