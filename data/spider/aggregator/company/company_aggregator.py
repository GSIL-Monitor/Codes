# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import random
import json
import lxml.html
from pymongo import MongoClient
import gridfs
import pymongo
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)
from tld import get_tld
from urlparse import urlsplit
import tldextract
from pyquery import PyQuery as pq

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

#logger
loghelper.init_logger("company_aggregator", stream=True)
logger = loghelper.get_logger("company_aggregator")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)
fromdb = mongo.crawler_v2
imgfs = gridfs.GridFS(mongo.gridfs)

#mysql
conn = None

# kafka
kafkaProducer = None
kafkaConsumer = None


def initKafka():
    global kafkaProducer
    global kafkaConsumer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)
    kafkaConsumer = KafkaConsumer("beian_v2", group_id="company_aggregator",
                metadata_broker_list=[url],
                auto_offset_reset='smallest')

def find_company(source_company):
    if source_company["companyId"] is not None:
        return source_company["companyId"]

    full_name = source_company["fullName"]
    if full_name is not None and full_name != "":
        company_id = find_company_by_full_name(full_name)
        if company_id is not None:
            return company_id


    source_domains = conn.query("select * from source_domain where sourceCompanyId=%s", source_company["id"])
    for source_domain in source_domains:
        if source_domain["organizerType"] == "企业":
            company_id = find_company_by_full_name(source_domain["organizer"])
            if company_id is not None:
                return company_id
        company_id = find_company_by_domain(source_domain["domain"])
        if company_id is not None:
            return company_id

    return None


def find_company_by_full_name(full_name):
    if full_name is None or full_name == "":
        return None

    company = conn.get("select * from company where fullName=%s", full_name)
    if company is not None:
        return company["id"]

    company_alias = conn.get("select * from company_alias where type=12010 and name=%s", full_name)
    if company_alias is not None:
        return company_alias["companyId"]
    return None


def find_company_by_domain(domain):
    if domain is None or domain == "":
        return None

    domain = conn.get("select * from domain where domain=%s limit 1", domain)
    if domain is not None:
        return domain["companyId"]
    return None

def aggregate(source_company_id):
    logger.info("source_company_id: %s" % source_company_id)
    s = conn.get("select * from source_company where id=%s", source_company_id)
    if s == None:
        return

    company_id = find_company(s)

    #company
    if company_id is not None:
        logger.info("Update company: %s" % s["fullName"])
        conn.update("update source_company set companyId=%s where id=%s", company_id, source_company_id)

        company = conn.get("select * from company where id=%s", company_id)
        if company["code"] is None or company["code"] == "":
            code = aggregator_util.get_company_code(company["name"])
            conn.update("update company set code=%s where id=%s", code, company_id)

        # 来自不同的源或不同项目, 如何合并?
        css = conn.query("select * from source_company where companyId=%s and companyStatus!=2020", company_id)

        rank = sys.maxint
        selected = None
        if len(css) > 1:
            for cs in css:
                if cs["companyStatus"] == 2020:
                    continue
                if cs["description"] is None or cs["description"] == "":
                    continue

                sa = conn.query("select * from source_artifact where sourceCompanyId=%s and type=4010", cs["id"])
                for a in sa:
                    domain = util.get_domain(a["link"])
                    if domain is None or domain == "":
                        continue

                    myRank = None
                    if a["rank"] is not None:
                        diff = datetime.datetime.today() - a["rankDate"]
                        if diff.days <= 3:
                            myRank = a["rank"]

                    if myRank is None:
                        alex = trends_tool.get_alexa(domain)
                        logger.info("%s, %s, %s" % (cs["name"],domain,alex["global_rank"]))
                        try:
                            if alex["global_rank"] == "-":
                                myRank = -1
                            else:
                                myRank = int(alex["global_rank"].replace(",",""))
                            conn.update("update source_artifact set rank=%s, rankDate=now() where id=%s",
                                        myRank, a["id"])
                        except:
                            continue

                    if myRank!=-1 and myRank < rank:
                        rank = myRank
                        selected = cs

            if selected is None:
                selected = s    # TODO
        else:
            selected = css[0]

        if selected is not None and selected["companyStatus"] != 2020:
            logger.info("selected=%s" % selected["name"])
            sql = "update company set \
                name=%s,fullName=%s,description=%s,brief=%s,\
                productDesc=%s, modelDesc=%s, operationDesc=%s, teamDesc=%s, marketDesc=%s, compititorDesc=%s, advantageDesc=%s, planDesc=%s, \
                round=%s,roundDesc=%s,companyStatus=%s,fundingType=%s,preMoney=%s,currency=%s,\
                locationId=%s,address=%s,phone=%s,establishDate=%s,logo=%s,\
                headCountMin=%s,headCountMax=%s,\
                modifyTime=now() \
                where id=%s"
            conn.update(sql,
                    selected["name"],selected["fullName"],selected["description"],selected["brief"],
                    selected.get("productDesc"), selected.get("modelDesc"), selected.get("operationDesc"), selected.get("teamDesc"), selected.get("marketDesc"), selected.get("compititorDesc"), selected.get("advantageDesc"), selected.get("planDesc"),
                    selected["round"],selected["roundDesc"],selected["companyStatus"],selected["fundingType"],selected["preMoney"],selected["currency"],
                    selected["locationId"],selected["address"],selected["phone"],selected["establishDate"],selected["logo"],
                    selected["headCountMin"],selected["headCountMax"],
                    company_id
                    )
    else:
        logger.info("New company: %s" % s["fullName"])
        if s["companyStatus"] != 2020:
            code = aggregator_util.get_company_code(s["name"])
            sql = "insert company(code,name,fullName,description,brief,\
                productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
                round,roundDesc,companyStatus,fundingType,preMoney,currency,\
                locationId,address,phone,establishDate,logo,\
                headCountMin,headCountMax,\
                active,createTime,modifyTime) \
                values(%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,%s, \
                    %s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,\
                    %s,%s,\
                    %s,now(),now())"
            company_id = conn.insert(sql,
                    code,s["name"],s["fullName"],s["description"],s["brief"],
                    s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
                    s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
                    s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],
                    s["headCountMin"],s["headCountMax"],
                    'Y')

            conn.update("update source_company set companyId=%s where id=%s", company_id, source_company_id)
        else:
            return



    # company_alias
    add_company_alias(company_id, s["fullName"])

    # domain & company_alias
    source_domains = conn.query("select * from source_domain where sourceCompanyId=%s", source_company_id)
    for sd in source_domains:
        if sd["organizerType"] == "企业":
            add_company_alias(company_id, sd["organizer"])

        if sd["organizer"] is not None:
            domain = conn.get("select * from domain where companyId=%s and domain=%s and organizer=%s",
                    company_id,sd["domain"],sd["organizer"])
        else:
            domain = conn.get("select * from domain where companyId=%s and domain=%s limit 1",
                    company_id,sd["domain"])
        if domain is None:
            sql = "insert domain(companyId,domain,organizer,organizerType,beianhao,mainBeianhao,\
                    websiteName,homepage,beianDate,expire,\
                    active,createTime,modifyTime)\
                    values(%s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,\
                    'Y',now(),now())"
            conn.insert(sql,
                    company_id,
                    sd["domain"],sd["organizer"],sd["organizerType"],sd["beianhao"],sd["mainBeianhao"],\
                    sd["websiteName"],sd["homepage"],sd["beianDate"],sd["expire"]
                    )

    # footprint
    source_footprints = conn.query("select * from source_footprint where sourceCompanyId=%s and footprintId is null", source_company_id)
    for sf in source_footprints:
        fp = conn.get("select * from footprint where companyId=%s and footDate=%s and description=%s",
                      company_id, sf["footDate"], sf["description"])
        if fp is None:
            sql = "insert footprint(companyId,footDate,description,active,createTime,modifyTime) \
                values(%s,%s,%s,'Y',now(),now())"
            footprint_id = conn.insert(sql,company_id,sf["footDate"],sf["description"])
        else:
            footprint_id = fp["id"]
        conn.update("update source_footprint set footprintId=%s where id=%s",footprint_id, sf["id"])

    # establishDate
    company1 = conn.get("select * from company where id=%s", company_id)
    if company1["establishDate"] is None:
        gongshang = conn.get("select g.* from gongshang_base g join company_alias a on g.companyAliasId=a.id \
                             join company c on a.companyId=c.id where c.id=%s order by g.establishTime limit 1", company_id)
        if gongshang is not None:
            conn.update("update company set establishDate=%s where id=%s", gongshang["establishTime"], company_id)
        else:
            fp = conn.get("select * from footprint where companyId=%s order by footDate limit 1", company_id)
            if fp is not None:
                conn.update("update company set establishDate=%s where id=%s", fp["footDate"],company_id)

    # member
    rels = conn.query("select * from source_company_member_rel where sourceCompanyId=%s", source_company_id)
    for rel in rels:
        if rel["companyMemberRelId"] is not None:
            # 已匹配
            continue

        source_member_id = rel["sourceMemberId"]
        source_member = conn.get("select * from source_member where id=%s", source_member_id)
        if source_member is None:
            continue

        member_id = source_member["memberId"]
        if member_id is None:
            member_id = aggregate_member(company_id, source_member)

        cmrel = conn.get("select * from company_member_rel where companyId=%s and memberId=%s",
                           company_id, member_id)
        if cmrel is None:
            cmrelId = conn.insert("insert company_member_rel(\
                companyId,memberId,position,joinDate,leaveDate,type,\
                active,createTime,modifyTime) \
                values(%s,%s,%s,%s,%s,%s,'Y',now(),now())",
                company_id, member_id, rel["position"],rel["joinDate"],rel["leaveDate"],rel["type"]
                )
        else:
            cmrelId = cmrel["id"]

        conn.update("update source_company_member_rel set companyMemberRelId=%s where id=%s",
                        cmrelId, rel["id"])

    # funding & investor
    sfs = conn.query("select * from source_funding where sourceCompanyId=%s", source_company_id)
    for sf in sfs:
        if sf["fundingId"] is None:
            #f = conn.get("select * from funding where companyId=%s and round=%s and roundDesc=%s",
            #             company_id, sf["round"], sf["roundDesc"])
            f = conn.get("select * from funding where companyId=%s and round=%s limit 1",
                          company_id, sf["round"])
            if f is None:
                sql = "insert funding(companyId,preMoney,postMoney,investment,\
                            round,roundDesc,currency,precise,fundingDate,fundingType,\
                            active,createTime,modifyTime) \
                        values(%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,'Y',now(),now())"
                fundingId=conn.insert(sql,
                                      company_id,
                                      sf["preMoney"],
                                      sf["postMoney"],
                                      sf["investment"],
                                      sf["round"],
                                      sf["roundDesc"],
                                      sf["currency"],
                                      sf["precise"],
                                      sf["fundingDate"],
                                      8030
                                      )
            else:
                fundingId = f["id"]
            conn.update("update source_funding set fundingId=%s where id=%s", fundingId, sf["id"])
        else:
            fundingId = sf["fundingId"]

        sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
        for sfir in sfirs:
            if sfir["fundingInvestorRelId"] is not None:
                continue

            source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
            if source_investor is None:
                continue
            investor_id = aggregate_investor(source_investor)

            funding_investor_rel = conn.get("select * from funding_investor_rel \
                                where investorId=%s and fundingId=%s",
                                investor_id, fundingId)
            if funding_investor_rel is None:
                sql = "insert funding_investor_rel(fundingId, investorId, currency, investment,\
                        precise,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,'Y',now(),now())"
                fundingInvestorRelId = conn.insert(sql,
                            fundingId,
                            investor_id,
                            sfir["currency"],
                            sfir["investment"],
                            sfir["precise"]
                        )
            else:
                fundingInvestorRelId = funding_investor_rel["id"]

            conn.update("update source_funding_investor_rel set fundingInvestorRelId=%s where id=%s",
                        fundingInvestorRelId,sfir["id"]
                        )

    # update company stage
    funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                       company_id)
    if funding is not None:
        conn.update("update company set round=%s, roundDesc=%s where id=%s",
                    funding["round"],funding["roundDesc"],company_id)

    # artifact
    sas = conn.query("select * from source_artifact where sourceCompanyId=%s", source_company_id)
    for sa in sas:
        if sa["artifactId"] is not None:
            continue
        if sa["type"] == 4010:
            continue
            '''
            if sa["link"] is not None and sa["link"] != "":
                link = util.norm_url(sa["link"])
                a = conn.get("select * from artifact where type=4010 and (name=%s or link=%s)", sa["name"], link)
                if a is None:
                    sql = "insert artifact(companyId,name,description,link,type,active,createTime,modifyTime) \
                            values(%s,%s,%s,%s,4010,'Y',now(),now())"
                    artifact_id = conn.insert(sql,
                            company_id,sa["name"],sa["description"],link
                                )
                else:
                    artifact_id = a["id"]
                conn.update("update source_artifact set artifactId=%s where id=%s",
                            artifact_id, sa["id"])
            '''
        else:
            a = conn.get("select * from artifact where type=%s and name=%s",sa["type"], sa["name"])
            if a is None:
                sql = "insert artifact(companyId,name,description,link,type,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,'Y',now(),now())"
                artifact_id = conn.insert(sql,
                        company_id,sa["name"],sa["description"],sa["link"],sa["type"]
                            )
            else:
                artifact_id = a["id"]
            conn.update("update source_artifact set artifactId=%s where id=%s",
                        artifact_id, sa["id"])

    domains = conn.query("select * from domain where companyId=%s", company_id)
    for domain in domains:
        str = domain["homepage"]
        if str is None:
            continue
        homepages = str.split(",")
        for h in homepages:
            logger.info(h)
            homepage = conn.get("select * from homepage where originalHomepage=%s",h)

            lastHomepage = None
            tags = None
            desc = None
            if homepage is None:
                url = "http://" + h
                (flag, r) = my_request.get_no_sesion(logger,url)
                if flag == -1:
                    conn.insert("insert homepage(companyId,originalHomepage,status,createTime,modifyTime) \
                            values(%s,%s,%s,now(),now())",
                                company_id,h,-1)
                else:
                    logger.info("status=%s, url=%s" % (r.status_code,r.url))
                    netloc = urlsplit(r.url).netloc
                    conn.insert("insert homepage(companyId,originalHomepage,lastHomepage,status,createTime,modifyTime) \
                            values(%s,%s,%s,%s,now(),now())",
                                company_id,h,netloc,r.status_code)
                    lastHomepage = "http://" + netloc
                    r.encoding = r.apparent_encoding
                    d = pq(r.text)
                    tags = d('meta[name="keywords"]').attr('content')
                    desc = d('meta[name="description"]').attr('content')
            else:
                if homepage["lastHomepage"] is not None:
                    lastHomepage = "http://" + homepage["lastHomepage"]

            if lastHomepage is not None:
                a = conn.get("select * from artifact where type=4010 and link=%s", lastHomepage)
                if a is None:
                    sql = "insert artifact(companyId,name,link,type,active,createTime,modifyTime,domain,alexa,tags,description) \
                            values(%s,null,%s,4010,'Y',now(),now(),%s,'Y',%s,%s)"
                    artifact_id = conn.insert(sql,
                            company_id,lastHomepage,util.get_domain(lastHomepage),tags,desc
                            )
                else:
                    sql = "update artifact set domain=%s, alexa='Y',tags=%s, description=%s where id=%s"
                    conn.update(sql,util.get_domain(lastHomepage),tags, desc, a["id"])

    # news
    aggregator_util.merge_news(source_company_id, company_id, conn)

    # job
    aggregator_util.merge_job(source_company_id, company_id, conn)

    # others
    company = conn.get('select * from company where id = %s', company_id)
    full_name = company['fullName']
    name = company['name']

    # aggregator_util.merge_weibo(company_id, name, full_name, conn)
    # aggregator_util.merge_wechat(company_id, name, full_name, conn)

    # result = trends_tool.haosou_news(result['name'])

    msg = {"type":"company", "id":company_id}
    flag = False
    while flag == False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def aggregate_member(company_id, source_member):
    member_id = source_member["memberId"]
    if member_id is not None:
        return member_id

    #前提: source_company已对应到company
    #scmrels = conn.query("select * from source_company_member_rel where sourceMemberId=%s", source_member["id"])
    scmrels = conn.query("select r.* from source_company_member_rel r join source_company sc on r.sourceCompanyId=sc.id where sc.companyId=%s", company_id)
    for rel in scmrels:
        source_company = conn.get("select * from source_company where id=%s", rel["sourceCompanyId"])
        if source_company is None:
            continue
        if source_company["companyId"] is None:
            continue
        members = conn.query("select m.* from \
            member m join company_member_rel r on m.id=r.memberId \
            where r.companyId=%s", source_company["companyId"])
        for m in members:
            if m["name"] == source_member["name"]:
                conn.update("update source_member set memberId=%s where id=%s", m["id"], source_member["id"])
                return m["id"]

    # new member
    #if source_member["work"] is None and source_member["description"] is not None:
    #    source_member["work"] = source_member.get("description")

    member_id = conn.insert("insert member( \
                            name,description,education,work,photo,active,createTime,modifyTime \
                            ) \
                            values(%s,%s,%s,%s,%s,'Y',now(),now())",
                            source_member["name"],
                            source_member["description"],
                            source_member["education"],
                            source_member["work"],
                            source_member["photo"]
    )
    conn.update("update source_member set memberId=%s where id=%s", member_id, source_member["id"])

    return member_id


def aggregate_investor(source_investor):
    investor_id = source_investor["investorId"]
    if investor_id is not None:
        return investor_id

    name = source_investor["name"]
    website = source_investor["website"]
    if website.find("无") != -1:
        website = None
    domain = util.get_domain(website)

    investor = conn.get("select * from investor where name=%s", name)
    if investor is None and website is not None and website !="":
        investor = conn.get("select * from investor where website=%s",website)
    if investor is None and domain is not None and domain!="":
        investor = conn.get("select * from investor where domain=%s",domain)

    if investor is None:
        investor_id = conn.insert("insert investor(name,website,domain,\
                            description,logo,stage,field,type,\
                            active,createTime,modifyTime) \
                            values(%s,%s,%s,\
                            %s,%s,%s,%s,%s,\
                            'Y',now(),now())",
                            source_investor["name"],
                            website,
                            domain,
                            source_investor["description"],
                            source_investor["logo"],
                            source_investor["stage"],
                            source_investor["field"],
                            10020
                            )
    else:
        investor_id = investor["id"]
    conn.update("update source_investor set investorId=%s where id=%s",investor_id,source_investor["id"])

    return investor_id

def add_company_alias(company_id, fullName):
    if fullName is None or fullName == "":
        return

    alias = conn.get("select * from company_alias where companyId=%s and name=%s",
        company_id, fullName)

    if alias is None:
        sql = "insert company_alias(companyId,name,type,active,createTime,modifyTime) \
                values(%s,%s,%s,%s,now(),now())"
        conn.insert(sql, company_id, fullName,12010,'Y')


if __name__ == '__main__':
    logger.info("company aggregator start")
    initKafka()

    # conn = db.connect_torndb()
    # aggregate(10)
    # conn.close()
    # exit(0)

    i = 0
    while True:
        try:
            for message in kafkaConsumer:
                try:
                    conn = db.connect_torndb()
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                     message.offset, message.key,
                                                     message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    source_company_id = msg["id"]

                    if type == "company":
                        aggregate(source_company_id)
                except Exception,e :
                    logger.exception(e)
                finally:
                    kafkaConsumer.task_done(message)
                    kafkaConsumer.commit()
                    conn.close()

                    #i += 1
                    #if i >=10 :
                    #    exit(0)
        except KeyboardInterrupt:
            exit(0)
        except Exception,e :
            logger.exception(e)
            time.sleep(60)
            initKafka()