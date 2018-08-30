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


source = 13020
def parse_cf(cf_key):
    item = fromdb.cf.find_one({"source":source, "cf_key":cf_key})
    if item is None:
        return

    content = item["content"]
    # content = json.loads(content)

    company_key = item['company_key']

    data = content['status']['data']

    #company
    company = data['company']
    name = company['name']
    fullName = company['fullName']
    description = company.get('projectAdvantage')
    logo_url = company['logo']
    brief = company['brief']
    company_status = company['status']

    logo_id = parser_util.get_logo_id(source, company_key, 'company', logo_url)


    accessCount = data['statistics']['accessCount']
    likesCount = data['statistics']['likesCount']
    followCount = data['statistics']['followCount']

    tags = data['tags']
    tag_arr = []
    for tag in tags:
        tag_arr .append(tag['name'])

    tag = ','.join(tag_arr)

    funds = data['funds']
    phase = funds['phase']
    unit = funds.get('unit')
    value = funds.get('value')


    cf = content['crowdfunding']

    coinvestors_count = 0
    if cf['data'].get('co_investors'):
        coinvestors_count = len(cf['data']['co_investors'])
    base = cf['data']['base']
    base_status = base['status']
    max_coinvestor_number = base['max_coinvestor_number']
    cf_min_raising = base['cf_min_raising']
    start_time = base['start_time']
    end_time = base['end_time']
    time_left =  base['time_left']
    min_investment = base['min_investment']
    # round = base['round']
    cf_success_raising = base['cf_success_raising']
    cf_max_raising = base['cf_max_raising']
    cf_success_raising_offer = base['cf_success_raising_offer']
    cf_raising = base['cf_raising']

    leader = base['leader']
    organization = base['organization']

    funding = cf['data']['funding']
    lead_investment = funding['lead_investment']
    valuation = funding['valuation']

    detail = cf['data']['detail']
    lead_desc = detail['lead_desc']
    bm_pain_point = detail['bm_pain_point']
    file_business_plan = detail['file_business_plan']
    com_video_link = detail['com_video_link']
    com_feature_pic = detail['com_feature_pic']
    market_situation = detail['market_situation']
    lead_business_desc = detail['lead_business_desc']
    competitor_analyze = detail['competitor_analyze']
    bm_profit_model = detail['bm_profit_model']
    market_share = detail['market_share']
    core_resources = detail['core_resources']
    cf_advantage = detail['cf_advantage']
    advantages = []
    for advantage in cf_advantage:
        advantages.append(advantage['value'])
    advantages = ','.join(advantages)

    lead_reason = detail['lead_reason']
    advantage_analysis = detail['advantage_analysis']



    lead_risk = detail['lead_risk']
    com_vision = detail['com_vision']
    com_desc = detail['com_desc']
    bm_solution = detail['bm_solution']

    start_time = datetime.datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S')
    end_time = datetime.datetime.strptime(end_time, '%m/%d/%Y %H:%M:%S')


    if phase == 'ANGEL':
        round = 1010
    elif phase == 'PRE_A':
        round = 1020
    elif 'A' in phase:
        round = 1030
    else:
        round = 0


    currency =0

    if unit == 'CNY':
        currency = 3020
    elif unit == 'USD':
        currency = 3010


    if base_status == 25: #ready
        base_status = 14010
    elif base_status == 30: #raising
        base_status = 14020
    elif base_status == 35:
        base_status = 14030


    if time_left == None or time_left == '':
        base_status = 14030

    today =  datetime.datetime.now()

    if end_time < today:
        base_status = 14030




    source_company_id = parser_util.get_source_company(source, company_key)

    if source_company_id is None:
        source_company = {"name": name,
                          "fullName": fullName,
                          "description": com_desc,
                          "brief": brief,
                          "round": None,
                          "roundDesc": None,
                          "companyStatus": 2010,
                          'fundingType':None,
                          "locationId": None,
                          "address": None,
                          "phone": None,
                          "establishDate": None,
                          "logo": logo_id,
                          "source": source,
                          "sourceId": company_key,
                          "field": None,
                          "subField": None,
                          "tags": None,
                          "headCountMin": None,
                          "headCountMax": None
                          }

        source_company_id = parser_util.insert_source_company(source_company)


    if description is None or description == '':
            description = com_desc

    source_crowdfunding = {
        'name': name,
        'description': description,
        'coinvestorCount': coinvestors_count,
        'maxCoinvestorNum': max_coinvestor_number,
        'minRaising': cf_min_raising,
        'successRaising': cf_success_raising,
        'maxRaising': cf_max_raising,
        'minInvestment': min_investment,
        'currency': currency,
        'startDate': start_time,
        'endDate': end_time,
        'preMoney': None,
        'postMoney': None,
        'status': base_status,
        'round': round,
        'roundDesc': phase,
        'value': value,
        'tags': tag,
        'accessCount': accessCount,
        'likesCount': likesCount,
        'followCount': followCount,
        'painPoint': bm_pain_point,
        'marketSituation': market_situation,
        'competitorAnalyze': competitor_analyze,
        'profitModel':bm_profit_model,
        'marketShare':market_share,
        'coreResources': core_resources,
        'cfAdvantage': advantages,
        'advantageAnalysis': advantage_analysis,
        'companyVision': com_vision,
        'companyDesc': com_desc,
        'bmSolution': bm_solution,
        'source': source,
        'sourceId': cf_key,
        'sourceCompanyId': source_company_id
    }

    # logger.info(tag)
    # logger.info(coinvestors_count)
    # logger.info(base_status)
    # logger.info(max_coinvestor_number)
    # logger.info(start_time)
    # logger.info(end_time)
    # logger.info(min_investment)
    # logger.info(cf_min_raising)
    # logger.info(cf_success_raising)
    # logger.info(cf_max_raising)
    # logger.info(bm_pain_point)
    # logger.info(market_situation)
    # logger.info(competitor_analyze)
    # logger.info(bm_profit_model)
    # logger.info(market_share)
    # logger.info(core_resources)
    # logger.info('cf_advantage=%s', advantages)
    # logger.info('advantages=%s', advantage_analysis)
    # logger.info(com_vision)



    source_cf_id = parser_util.insert_source_crowdfunding(source_crowdfunding)

    if organization is not None:
        investor_name = organization['name']
        investor_type = 10020
        source_id = organization['id']
    elif leader is not None:
        investor_name = leader['name']
        investor_type = 10010
        source_id = leader['id']
    else:
        investor_name = ''
        investor_type = 10020
        source_id = None


    source_investor_id = parser_util.find_source_investor(source, source_id)

    source_cf_leader = {
        'sourceCfId': source_cf_id,
        'investorName' :investor_name,
        'investorType': investor_type,
        'sourceInvestorId': source_investor_id,
        'description': lead_desc,
        'investment': lead_investment,
        'valuation':valuation,
        'businessDesc': lead_business_desc,
        'reason': lead_reason,
        'risk': lead_risk
    }

    parser_util.insert_source_cf_leader(source_cf_leader)


    #bp
    source_id = str(cf_key)+'_bp'
    source_cf_document = {
        'sourceCfId': source_cf_id,
        'name': None,
        'description': None,
        'link': file_business_plan,
        'rank': None,
        'sourceId': source_id,
        'type': 9010
    }

    parser_util.insert_source_cf_document(source_cf_document)

    #video
    source_id = str(cf_key)+'_video'
    source_cf_document = {
        'sourceCfId': source_cf_id,
        'name': None,
        'description': None,
        'link': com_video_link,
        'rank': None,
        'sourceId': source_id,
        'type': 9020
    }

    parser_util.insert_source_cf_document(source_cf_document)

    rank = 0
    for link in com_feature_pic:
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




if __name__ == '__main__':
    (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("cf_36kr", "crawler_cf_36kr_v2")

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

                    # kafka_consumer.task_done(message)
                    # kafka_consumer.commit()
                except Exception,e :
                    logger.error(e)
                    traceback.print_exc()
        except Exception,e :
            logger.error(e)
            traceback.print_exc()
            time.sleep(60)
            (logger, fromdb, kafka_producer, kafka_consumer) = parser_util.parser_init("cf_36kr", "crawler_cf_36kr_v2")
