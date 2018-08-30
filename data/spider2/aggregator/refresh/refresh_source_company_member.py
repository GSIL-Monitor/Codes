# -*- coding: utf-8 -*-
import os, sys, re, json
import time
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util
import helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/company/itjuzi'))
import itjuzi_company_3_search

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/recruit/lagou'))
import lagou_company_search

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/company/kr36'))
import kr36_company_2_search_2

#logger
loghelper.init_logger("refresh_source_company_member", stream=True)
logger = loghelper.get_logger("refresh_source_company_member")

COMPANIES = []


def check_postion(position, crels):
    for crel in crels:
        if crel["position"] is not None and re.search(position, crel["position"], re.I):
            return True
    return False

def aggregate_member(company_id, source_company_id, test=False):
    logger.info("aggregate_member")
    conn = db.connect_torndb()
    rels = conn.query("select * from source_company_member_rel where sourceCompanyId=%s "
                      "and modifyTime>'2018-07-03'", source_company_id)
    crels = conn.query("select * from company_member_rel where companyId=%s and (active is null or active='Y')", company_id)
    logger.info(json.dumps(crels, ensure_ascii=False, cls=util.CJsonEncoder))
    conn = db.connect_torndb()
    for rel in rels:
        source_member_id = rel["sourceMemberId"]
        source_member = conn.get("select * from source_member where id=%s", source_member_id)
        if source_member is None:
            continue

        #Check position if it is existed
        exist = False
        # if rel["position"] is not None:
        #     for position in ["ceo", "cto", "coo"]:
        #         if re.search(position, rel["position"], re.I) and check_postion(position, crels):
        #             exist = True
        #             break
        if exist:
            continue
        # member_id = source_member["memberId"]
        # if member_id is None:
        #     member_id = aggregate_one_member(company_id, source_member)
        logger.info(json.dumps(source_member, ensure_ascii=False, cls=util.CJsonEncoder))
        member_id = aggregate_one_member(company_id, source_member, test)
        logger.info("aggregate_member. member_id=%s source, %s", member_id, source_member["name"])
        insert_company_member_rel(company_id,member_id,rel, test)


def aggregate_one_member(company_id, source_member, test):
    table_names = helper.get_table_names(test)
    # member_id = source_member["memberId"]
    # if member_id is not None:
    #     return member_id

    member_id = None
    conn = db.connect_torndb()

    #同公司同名识别为同一个人
    members = conn.query("select m.* from "
        + table_names["member"] + " m join " + table_names["company_member_rel"] + " r on m.id=r.memberId " +
        "where r.companyId=%s and (r.active is null or r.active='Y')", company_id)
    m = None

    for m in members:
        logger.info(json.dumps(m, ensure_ascii=False, cls=util.CJsonEncoder))
        if m["name"] == source_member["name"]:
            member_id = m["id"]
            # flag = replace(m, source_member)
            # if flag:
            #     logger.info("update")
            #     logger.info(json.dumps(m, ensure_ascii=False, cls=util.CJsonEncoder))
            #     aggregator_db_util.update_member(m)
            break

    if member_id is None and not test:
        member_id = source_member["memberId"]

    if member_id is not None:
        #merge
        if m is not None:
            if not test:
                flag = replace(m, source_member)
                if flag:
                    logger.info("update")
                    logger.info(json.dumps(m, ensure_ascii=False, cls=util.CJsonEncoder))
                    aggregator_db_util.update_member(m)
    else:
        member_id = aggregator_db_util.insert_member(source_member, test)

    if not test:
        conn.update("update source_member set memberId=%s where id=%s", member_id, source_member["id"])

    conn.close()
    return member_id


def update_member(member):
    m = member
    conn = db.connect_torndb()
    conn.update("update member set \
                        description=%s, education=%s, work=%s, photo=%s, modifyTime=now() \
                        where id=%s",
                        m["description"],m["education"],m["work"],m["photo"],m["id"])
    conn.close()


def insert_company_member_rel(company_id, member_id, source_company_member_rel, test=False):
    rel = source_company_member_rel
    conn = db.connect_torndb()
    table_names = helper.get_table_names(test)
    item = conn.get("select * from " + table_names["company_member_rel"] + " where companyId=%s and memberId=%s "
                    "and (active is null or active='Y') "
                    "limit 1", company_id, member_id)
    if item is None:

        cmrelId = conn.insert("insert " + table_names["company_member_rel"] +"(\
                    companyId,memberId,position,joinDate,leaveDate,type,\
                    active,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s,'Y',now(),now())",
                    company_id, member_id, rel["position"],rel["joinDate"],rel["leaveDate"],rel["type"]
                    )
    else:
        if rel["type"] < item["type"]:
            logger.info("update type***********")
            conn.update("update company_member_rel set type=%s where id=%s", rel["type"], item["id"])
        cmrelId = item["id"]
    conn.close()
    return cmrelId

def replace(member, source_member):
    names = ["name",
             "description",
             "education",
             "work",
             "photo",
             ]
    flag = False
    for name in names:
        if source_member[name] is not None and source_member[name].strip() != "":
            member[name] = source_member[name]
            flag = True
    return flag


def refresh_company(companyId):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", companyId)
    corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
    scs_itjuzi = conn.query("select * from source_company where source=13030 and companyId=%s and "
                            "(active is null or active='Y')", companyId)
    scs_lagou = conn.query("select * from source_company where source=13050 and companyId=%s and "
                           "(active is null or active='Y') and aggregateVerify is null", companyId)

    if len(scs_itjuzi) == 0:
        if company["name"] is not None and company["name"].strip() != "":
            itjuzi_company_3_search.start_run(company["name"], None)
        if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
            itjuzi_company_3_search.start_run(corporate["fullName"], None)
    else:
        for sc_itjuzi in scs_itjuzi:
            if sc_itjuzi["sourceId"] is not None and sc_itjuzi["sourceId"].strip() != "":
                itjuzi_company_3_search.start_run(company["name"], sc_itjuzi["sourceId"])

    if len(scs_lagou) > 0:
        for sc_lagou in scs_lagou:
            if sc_lagou["sourceId"] is not None and sc_lagou["sourceId"].strip() != "":
                lagou_company_search.start_run(company["name"], sc_lagou["sourceId"])

    conn.close()
    pass


def refresh_company_card(companyIds):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp
    n = 0
    n1 = 0
    for companyId in companyIds:
        company = conn.get("select * from company where id=%s", companyId)
        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
        scs_card = conn.query("select * from source_company where source=13121 and companyId=%s and "
                              "(active is null or active='Y')", companyId)

        if len(scs_card) > 0:
            n1 += 1
            for sc_card in scs_card:
                item = collection.find_one({"url": "http://vip.api.qimingpian.com/d/c3", 'postdata.id':sc_card["sourceId"]},
                                           {"data.basic": 1, "postdata": 1, "productinfos": 1, "url": 1})
                if item is not None:
                    n += 1
                    logger.info(item["_id"])
                    break
    logger.info("%s -- %s -- %s", len(companyIds), n1, n)

    mongo.close()
    conn.close()
    pass

def refresh_company_36kr(companyIds):
    conn = db.connect_torndb()
    kcs = []
    for cId in companyIds:
        companyId = cId
        company = conn.get("select * from company where id=%s", companyId)
        corporate = conn.get("select * from corporate where id=%s", company["corporateId"])

        scs_kr36 = conn.query("select * from source_company where source=13022 and companyId=%s and "
                              "(active is null or active='Y')", companyId)

        if len(scs_kr36) == 0:
            if company["name"] is not None and company["name"].strip() != "":
                # kr36_company_2_search.start_run(company["name"], None, listcrawler,companycrawler)
                kcs.append({"keyword": company["name"].strip(), "sourceId": None})
            if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
                # kr36_company_2_search.start_run(corporate["fullName"], None, listcrawler,companycrawler)
                kcs.append({"keyword": corporate["fullName"].strip(), "sourceId": None})
        else:
            pass

    if len(kcs) > 0:
        kr36_company_2_search_2.start_run(kcs)

    conn.close()
    pass
    # conn = db.connect_torndb()
    # kcs = []
    # kcids = []
    # ffn = 0
    # nnn = 0
    # for cId in companyIds:
    #     companyId = cId
    #     company = conn.get("select * from company where id=%s", companyId)
    #     corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
    #
    #     scs_kr36 = conn.query("select * from source_company where source=13022 and companyId=%s and "
    #                           "(active is null or active='Y')", companyId)
    #
    #
    #     if len(scs_kr36) == 0:
    #         nnn += 1
    #         # if company["name"] is not None and company["name"].strip() != "":
    #         #     # kr36_company_2_search.start_run(company["name"], None, listcrawler,companycrawler)
    #         #     kcs.append({"keyword":company["name"].strip(), "sourceId":None})
    #         # if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
    #         #     # kr36_company_2_search.start_run(corporate["fullName"], None, listcrawler,companycrawler)
    #         #     kcs.append({"keyword": corporate["fullName"].strip(), "sourceId": None})
    #         pass
    #     else:
    #         ff = False
    #         for sc_kr36 in scs_kr36:
    #             aggregate_member(companyId, sc_kr36["id"])
    #
    #             mms = conn.query("select * from company_member_rel where companyId=%s and"
    #                               " (active is null or active='Y')", companyId)
    #             if len(mms) > 0:
    #                 break
    #             # mms = conn.query("select * from source_company_member_rel where sourceCompanyId=%s ", sc_kr36["id"])
    #             # if len(mms) > 0:
    #             #     logger.info("Company: %s has source_member under %s|%s|%s|%s",
    #             #                 companyId, sc_kr36["id"], sc_kr36["name"], mms[0]["position"], mms[0]["type"])
    #             #     ff = True
    #
    #         if ff is True:
    #             ffn += 1
    #
    #             # aggregate_member(companyId, sc_kr36["id"])
    #             #
    #             # mms = conn.query("select * from company_member_rel where companyId=%s and"
    #             #                   " (active is null or active='Y')", companyId)
    #             # if len(mms) > 0:
    #             #     break
    #
    # #     else:
    # #         for sc_kr36 in scs_kr36:
    # #             if sc_kr36["sourceId"] is not None and sc_kr36["sourceId"].strip() != "":
    # #                 # kr36_company_2_search.start_run(company["name"], sc_kr36["sourceId"], listcrawler,companycrawler)
    # #                 kcids.append(companyId)
    # #                 kcs.append({"keyword": company["name"].strip(), "sourceId": sc_kr36["sourceId"]})
    # #
    # # if len(kcs) > 0:
    # #     logger.info("***********%s-----%s", len(kcids), len(companyIds))
    # #     kr36_company_2_member.start_run(kcs)
    # logger.info(ffn)
    # logger.info(nnn)
    # conn.close()
    # pass

def ss_run():

    while True:

        if len(COMPANIES) == 0:
            return
        KEYC = COMPANIES.pop(0)
        logger.info("************ here do company: %s, remain: %s", KEYC, len(COMPANIES))
        refresh_company(KEYC)

rmap = {
    1000: '未融资',
    1010: '天使轮',
    1011: '天使轮',
    1020: 'pre-A',
    1030: 'A',
    1031: 'A+',
    1039: 'Pre-B',
    1040: 'B',
    1041: 'B+',
    1050: 'C',
    1060: 'D',
    1070: 'E',
    1080: 'F',
    1090: '后期阶段',
    1100: 'pre-IPO',
    1105: '新三板',
    1106: '新三板定增',
    1110: 'IPO',
    1120: '被收购',
    1130: '战略投资',
    1140: '私有化',
    1150: '债权融资',
    1160: '股权转让',
    1111:  "Post-IPO",
    1131:  "战略合并",
    1009:  "众筹",
    1109:  "ICO",
    1112: "定向增发",
}

def check_news(companyId):
    global line
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection = mongo.info.gongshang
    collection_news = mongo.article.news
    company = conn.get("select * from company where id=%s", companyId)
    corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
    funding = conn.get("select * from funding where corporateId=%s and (active is null or active='Y') "
                       "order by fundingDate desc limit 1", corporate["id"])
    newes = list(collection_news.find({"companyIds": companyId,"type": {"$ne":61000}}))
    names = []
    newsids = []
    newsidnames = []
    if len(newes) > 0:
        if corporate["fullName"] is not None and corporate["fullName"].strip() != "":
            gongshang = collection.find_one({"name": corporate["fullName"]})

            if gongshang is not None:

                if gongshang.has_key("legalPersonName") is True and gongshang["legalPersonName"] is not None and \
                       gongshang["legalPersonName"] not in ["","-"] and gongshang["legalPersonName"] not in names:
                    names.append(gongshang["legalPersonName"])

                if gongshang.has_key("members") is True and len(gongshang["members"]) > 0:
                    for mem in gongshang["members"]:
                        if mem.has_key("name") is True and mem["name"] is not None and \
                                mem["name"] not in ["", "-"] and mem["name"] not in names:
                            names.append(mem["name"])

                if len(names) > 0:
                    logger.info(json.dumps(names, ensure_ascii=False, cls=util.CJsonEncoder))

                    for news in newes:
                        main = ""
                        for content in news.get("contents",[]):
                            if isinstance(content,dict) and content.has_key("content") and content["content"].strip() != "":
                                main = main + content["content"]

                        fflag = False

                        for name in names + ["CEO","创始人","ceo"]:
                            if main.find(name) >= 0:
                                logger.info("id: %s find: %s, for company: %s|%s", news["_id"], name, companyId, company["code"])
                                newsidnames.append(
                                    {"id": "http://pro.xiniudata.com/#/news/%s" % str(news["_id"]), "n": name})
                                fflag = True
                            if fflag is True:
                                break

                        if fflag is True:
                            newsids.append(str(news["_id"]))
                            # newsidnames.append({"id": "http://pro.xiniudata.com/#/news/%s" % str(news["_id"]),"n": name})


    logger.info("company: %s, total find %s, %s", companyId, len(newsids), ":".join(newsids))

    conn.close()
    mongo.close()
    link = "http://pro.xiniudata.com/validator/#/company/%s/overview" % company["code"]
    rounda = corporate["round"]
    roundDesc = rmap[int(rounda)] if (rounda is not None and rmap.has_key(int(rounda))) else str(rounda)
    newsstr = ";".join([nn["id"] + "(" + nn["n"] + ")" for nn in newsidnames])
    line = "%s<<<%s<<<%s<<<%s<<<%s<<<%s<<<%s\n" % (company["code"], link, company["name"], roundDesc,
                                                   funding["fundingDate"], len(newsids), newsstr)
    # if len(newsids) > 0:
    #     exit()
    logger.info(line)
    logger.info("\n\n\n\n")
    return newsids,line




if __name__ == '__main__':

    logger.info("python refresh_source_company_member")
    while True:
        conn = db.connect_torndb()
        mongo = db.connect_mongo()
        collection_raw = mongo.raw.projectdata
        collection = mongo.task.company_refresh
        sql = '''select  c.id,c.code,c.name,
                        case when co.locationId>370 then '国外' else '国内' end as location  
                    ,
                    case when co.round=1000 then "尚未获投"
                    when co.round=1010 then "种子轮"
                    when co.round=1011 then "天使轮"
                    when co.round=1020 then "Pre-A轮"
                    when co.round=1030 then "A轮"
                    when co.round=1031 then "A+轮"
                    when co.round=1039 then "Pre-B"
                    when co.round=1040 then "B轮"
                    when co.round=1041 then "B+轮"
                    when co.round=1050 then "C轮"
                    when co.round=1051 then "C+轮"
                    when co.round=1060 then "D轮"
                    when co.round=1070 then "E轮"
                    when co.round=1080 then "F轮"
                    when co.round=1090 then "后期阶段"
                    when co.round=1100 then "Pre-IPO"
                    when co.round=1105 then "新三板"
                    when co.round=1106 then "新三板定增"
                    when co.round=1110 then "上市"
                    when co.round=1120 then "并购"
                    when co.round=1140 then "私有化"
                    when co.round=1150 then "债权融资"
                    when co.round=1160 then "股权转让"
                    when co.round=1130 then "战略投资"
                    when co.round=1111 then "Post-IPO" 
                    when co.round=1131 then "战略合并"          
                    when co.round=1009 then "众筹"          
                    when co.round=1109 then "ICO"          
                    when co.round=1112 then "定向增发"          
                     end as round
            ,count(distinct f.id) funding,count(distinct cmr.memberId) member
        from company c
        join corporate co on c.corporateid=co.id
        left join funding f on c.id=f.companyId and (f.active='Y' or f.active is null) 
        left join company_member_rel cmr on cmr.companyId=c.id and (cmr.active = 'Y' or cmr.active is null) and cmr.type not in (5030,5040)
        where
        (c.active='Y' or c.active is null) 
        group by c.id,c.code,c.name
        having funding>0 and member=0
            '''
        results = conn.query(sql)
        logger.info("%s cnt", len(results))
        for result in results:
            # if result["id"] not in COMPANIES and result["location"] == "国内" and int(result["id"])> 60000:
            if result["id"] not in COMPANIES and result["location"] == "国内":
                COMPANIES.append(result["id"])

        # refresh_company_card(COMPANIES)
        # if len(COMPANIES) > 0:
        #     threads = [gevent.spawn(ss_run) for i in xrange(11)]
        #     gevent.joinall(threads)
        # ss_run()
        # refresh_company_36kr(COMPANIES)
        fp2 = open("report.txt", "w")
        a = 0
        for CID in COMPANIES:
            nids, line = check_news(CID)
            if len(nids) > 0 :
               a += 1
            fp2.write(line)
        # fp2 = open("report.txt", "w")
        #
        fp2.close()
        logger.info("%s/%s cnt", a,len(COMPANIES))
        conn.close()
        mongo.close()
        time.sleep(1)
        break

