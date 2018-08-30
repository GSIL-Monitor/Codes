# -*- coding: utf-8 -*-
import os, sys, json
import time, datetime
import find_company
import company_aggregator
import company_info_expand
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
import corporate_util
import email_helper, name_helper


#logger
loghelper.init_logger("company_merge_decompose_auto", stream=True)
logger = loghelper.get_logger("company_merge_decompose_auto")

# fp2 = open("me.txt", "w")

def corp_decompose():
    n = 0
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    conn = db.connect_torndb()
    companies = conn.query("select id,name,corporateId,verify,modifyUser,modifyTime "
                           "from company where (active is null or active='Y')")
    for company in companies:
        cdflag = False
        if company["corporateId"] is None: continue
        cs = conn.query("select * from company where (active is null or active='Y') and corporateId=%s",
                         company["corporateId"])
        if len(cs) > 1: continue
        # if int(company["id"]) < 2400: continue
        if company["modifyUser"] is not None and company["modifyTime"] >= ss and company["verify"] == 'Y':
            pass
        else:
            scs = conn.query("select * from source_company where (active is null or active!='N') and "
                             "companyId=%s and source in (13400,13401,13402)", company["id"])
            if len(scs) > 0:
                logger.info("stock here no info")
                continue

            for source in [13022,13030]:
                scs = conn.query("select * from source_company where (active is null or active!='N') and "
                                 "companyId=%s and source=%s", company["id"], source)
                if len(scs) > 1:
                    cdflag = True
                    break
        if cdflag is True:
            # mongo = db.connect_mongo()
            # scs = list(conn.query(
            #     "select * from source_company where (active is null or active='Y') and "
            #     "companyStatus!=2020 and companyId=%s order by source",
            #     company["id"]))
            # if mongo.aggre.agg.find_one({"companyId": int(company["id"])}) is None:
            #     aggc = {
            #         "companyId": int(company["id"]),
            #         "sourceCompanyIds": [int(sc["id"]) for sc in scs]
            #     }
            #     mongo.aggre.agg.insert(aggc)
            # mongo.close()
            # logger.info("decompose %s|%s", company["id"], company["name"])
            # do decompose
            # corporate_util.autoDecompose(company["corporateId"],company["id"])
            n += 1
        # if n == 4:
        #     exit()

    logger.info("decompose num %s",n)
    conn.close()


def corp_decompose2():
    n = 0
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_goshang = mongo.info.gongshang
    companies = conn.query("select id,name,corporateId,verify,modifyUser,modifyTime "
                           "from company where (active is null or active='Y')")
    for company in companies:

        if company["corporateId"] is None: continue
        cs = conn.query("select * from company where (active is null or active='Y') and corporateId=%s",
                         company["corporateId"])
        if len(cs) > 1: continue
        # if int(company["id"]) < 2400: continue
        if company["modifyUser"] is not None and company["modifyTime"] >= ss and company["verify"] == 'Y':
            continue

        corp_names = conn.query("select * from corporate_alias where type=12010 and "
                                "(active is null or active='Y') and corporateId=%s", company["corporateId"])
        corp_names_list = []
        for corp_name in corp_names:
            if corp_name["verify"] == "Y" and corp_name["modifyUser"] is not None: continue
            if corp_name["name"] is not None and corp_name["name"].find("分公司")>=0: continue
            name_gongshang = collection_goshang.find_one({"name": corp_name["name"]})
            if name_gongshang is not None:
                corp_names_list.append({"name": corp_name["name"], "member":name_gongshang.get("members",[])})
        if len(corp_names_list) < 3:
            continue

        logger.info("decompose %s|%s", company["id"], company["name"])
        # for cn in corp_names_list:
        #     logger.info(cn["name"])
        #     logger.info(json.dumps(cn["member"], ensure_ascii=False, cls=util.CJsonEncoder))
        # mongo = db.connect_mongo()
        # scs = list(conn.query(
        #     "select * from source_company where (active is null or active='Y') and "
        #     "companyStatus!=2020 and companyId=%s order by source",
        #     company["id"]))
        # if mongo.aggre.agg.find_one({"companyId": int(company["id"])}) is None:
        #     aggc = {
        #         "companyId": int(company["id"]),
        #         "sourceCompanyIds": [int(sc["id"]) for sc in scs]
        #     }
        #     mongo.aggre.agg.insert(aggc)
        # mongo.close()
        # logger.info("decompose %s|%s", company["id"], company["name"])
        # do decompose
        # corporate_util.autoDecompose(company["corporateId"],company["id"])
        n += 1
        # if n == 4:
        #     exit()

    logger.info("decompose num %s",n)
    conn.close()
    mongo.close()


def corp_merge():
    n = 0
    n1 = 0
    n2 = 0
    conn = db.connect_torndb()
    cnames = conn.query("select ca.name,count(distinct ca.corporateId) cnt from "
                        "corporate_alias ca join corporate co  on co.id=ca.corporateId "
                        "join company c on c.corporateId=co.id "
                        "where (ca.active='Y' or ca.active is null) and (co.active='Y' or co.active is null) "
                        "and (c.active='Y' or c.active is null) and ca.type=12010 group by ca.name having cnt>1")

    for cname in cnames:
        full_name = cname["name"]
        corporate_ids = []
        stockFlag = False

        if full_name is None or full_name.strip() == "" or full_name.strip() == "-":
            continue

        corporate_aliases = conn.query("select a.* from corporate_alias a join corporate c on c.id=a.corporateId where "
                                       "(c.active is null or c.active !='N') and (a.active is null or a.active !='N') "
                                       "and a.type=12010 and a.name=%s",
                                       full_name)
        for ca in corporate_aliases:

            c_stock = conn.get("select * from corporate_stock_exchange_rel where corporateId=%s limit 1",
                               ca["corporateId"])
            if c_stock is not None:
                stockFlag = True
                continue

            company = conn.get("select * from company where corporateId=%s and (active is null or active='Y') limit 1",
                               ca["corporateId"])
            if company is not None:

                if ca["corporateId"] not in corporate_ids:
                    corporate_ids.append(int(ca["corporateId"]))

        if len(corporate_ids) > 1 and stockFlag is False:
            #do merge
            n += 1
            mflag = corporate_util.autoMerge(corporate_ids,full_name)
            if mflag == 1:
                n1 += 1
            elif mflag == 2:
                n2 += 1

    logger.info("merge num %s/%s/%s",n2, n1, n)
    conn.close()

def get_links(cids):
    links = []
    conn = db.connect_torndb()
    for cid in cids:
        companies = conn.query("select * from company where corporateId=%s and (active is null or active='Y')", cid)
        for c in companies:
            link = 'http://pro.xiniudata.com/validator/#/company/%s/overview' % c["code"]
            links.append(link)
    conn.close()
    return ";".join(links)


def corp_merge2():
    fp2 = open("me.txt", "w")
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    conn = db.connect_torndb()
    cnames = conn.query("select fullName,count(*) as cnt from corporate where (active is null or active !='N') "
                        "and fullName is not null and fullName!='' group by fullName having cnt>1")

    # cnames = conn.query("select fullName,count(*) as cnt from corporate where (active is null or active !='N') "
    #                     "and fullName='上海中慎网络科技有限公司' group by fullName having cnt>1")
    for cname in cnames:
        full_name = cname["fullName"]
        corporate_ids = []
        stockFlag = False

        if full_name is None or full_name.strip() == "" or full_name.strip() == "-" \
                or full_name.strip() == "个人" or full_name.strip() == "扎堆":
            continue

        corporate_aliases = conn.query("select * from corporate_alias where name=%s and (active is null or active !='N')",
                                full_name)
        for caa in corporate_aliases:
            ca = conn.get("select * from corporate where (active is null or active !='N') and id=%s",
                          caa["corporateId"])
            if ca is None: continue
            if ca["fullName"] != full_name: continue

            c_stock = conn.get("select * from corporate_stock_exchange_rel where corporateId=%s limit 1",
                               ca["id"])
            if c_stock is not None:
                stockFlag = True
                continue

            company = conn.get("select * from company where corporateId=%s and (active is null or active!='N') limit 1",
                               ca["id"])
            if company is not None:

                if ca["id"] not in corporate_ids:
                    corporate_ids.append(int(ca["id"]))

        if len(corporate_ids) > 1 and stockFlag is False:
            logger.info("merge:%s-> %s",full_name, corporate_ids)
            #do merge
            n += 1
            mflag = corporate_util.autoMerge(corporate_ids,full_name)

            if mflag is None:
                logger.info("wrong")
                exit()
            if mflag == 1:
                n1 += 1
            elif mflag == 2:
                n2 += 1
            elif mflag == 3:
                n3 += 1
            elif mflag == 4:
                n4 += 1
                line = "%s+++%s+++%s\n" % (
                full_name, ";".join([str(id) for id in corporate_ids]), get_links(corporate_ids))
                fp2.write(line)
            else:
                line = "%s+++%s+++%s\n" % (full_name, ";".join([str(id) for id in corporate_ids]), get_links(corporate_ids))
                fp2.write(line)

    logger.info("merge num %s/%s/%s/%s/%s",n4, n3, n2, n1, n)
    content = '''<div>Dears,    <br /><br />

        附件是目前系统中存在重复的公司，请在后台搜索
        </div>
        '''
    fp2.close()
    path = os.path.join(sys.path[0], "me.txt")
    logger.info(path)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in ["celine","zhlong","bamy"]]),
                                "重复公司检索--人工审查",content, path)
    conn.close()


def corp_merge3():
    tline = ""
    n = 0
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0; n5=0; n6=0; n7=0
    conn = db.connect_torndb()
    cnames = conn.query("select name,count(*) as cnt from corporate_alias where (active is null or active !='N') "
                        "and name is not null and name!=''  group by name having cnt>1")

    # cnames = conn.query("select fullName,count(*) as cnt from corporate where (active is null or active !='N') "
    #                     "and fullName='上海中慎网络科技有限公司' group by fullName having cnt>1")
    logger.info("total names: %s", len(cnames))

    for cname in cnames:
        pnames = []
        fundingFlag = False
        cfullFlag = True
        full_name = cname["name"]
        corporate_ids = []
        corporate_ids_f = []
        stockFlag = False

        if full_name is None or full_name.strip() == "" or full_name.strip() == "-" \
                or full_name.strip() == "个人" or full_name.strip() == "扎堆":
            continue

        corporate_aliases = conn.query("select * from corporate_alias where name=%s and (active is null or active !='N')",
                                full_name)
        for caa in corporate_aliases:
            ca = conn.get("select * from corporate where (active is null or active !='N') and id=%s",
                          caa["corporateId"])
            if ca is None: continue
            # if ca["fullName"] != full_name: continue

            c_stock = conn.get("select * from corporate_stock_exchange_rel where corporateId=%s limit 1",
                               ca["id"])
            if c_stock is not None:
                stockFlag = True
                continue

            company = conn.get("select * from company where corporateId=%s and (active is null or active='Y') limit 1",
                               ca["id"])
            if company is not None:

                if ca["id"] not in corporate_ids:
                    corporate_ids.append(int(ca["id"]))

                    if ca["fullName"] != full_name:
                        cfullFlag = False
                    else:
                        if ca["id"] not in corporate_ids_f:
                            corporate_ids_f.append(int(ca["id"]))

                    funding = conn.get("select * from funding where corporateId=%s and (active is null or active='Y') "
                                       "order by fundingDate desc limit 1", caa["corporateId"])
                    if fundingFlag is False and funding is not None:
                        fundingFlag = True

                    pnames.append(company["name"])


        if len(corporate_ids) > 1 and stockFlag is False:

            if len(pnames) >= 2:
                vv = compare(pnames)
            else:
                vv = 0

            (chinese, company) = name_helper.name_check(full_name)
            if chinese is True:
                chinese_type = "Y"
                n5 += 1
                if fundingFlag is True:
                    n3 += 1
                if cfullFlag is True:
                    n4 += 1
                if vv <= 0.75:
                    n7 += 1

            else:
                chinese_type = "N"
                n6 += 1
            #do merge

            n += 1

            logger.info("merge:%s %s-> %s", full_name, corporate_ids, chinese_type)
            mflag = corporate_util.autoMerge(corporate_ids,full_name)
            #
            # if mflag is None:
            #     logger.info("wrong")
            #     exit()
            if mflag == 1:
                n1 += 1
            else:
                n2 += 1

            # elif mflag == 2:
            #     n2 += 1
            # elif mflag == 3:
            #     n3 += 1
            # elif mflag == 4:
            #     n4 += 1
            #     line = "%s+++%s+++%s\n" % (
            #     full_name, ";".join([str(id) for id in corporate_ids]), get_links(corporate_ids))
            #     fp2.write(line)
            # else:
            c1 = "否"; c2 = "否"; c3 = "否"
            if len(corporate_ids_f) == 1:
                c1 = "是"
            if len(corporate_ids_f) == len(corporate_ids):
                c2 = "是"
            if len(corporate_ids_f) == 0:
                c3 = "是"

            line = "%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s+++%s\n" % (full_name, ";".join([str(id) for id in corporate_ids]),
                                                      get_links(corporate_ids),
                                                      "中文名" if chinese_type =='Y' else "英文名",
                                                      "有融资" if fundingFlag is True else "无融资",
                                                      "公司主要名称一致" if cfullFlag is True else "公司别名一致",
                                                      "短名高度相似" if vv <= 0.75 else "短名不相似",
                                                      "可以根据verify自动聚合" if mflag == 1 else " ",
                                                                               c1,c2,c3)

            # fp2.write(line)
            tline += line
    fp2 = open("me.txt", "w")
    fp2.write(tline)
    logger.info("merge num %s/%s/%s/%s/%s/%s/%s/%s",n, n1, n2, n3, n4, n5, n6, n7)
    content = '''<div>Dears,    <br /><br />

        附件是目前系统中存在重复的公司，请在后台搜索
        </div>
        '''
    fp2.close()
    path = os.path.join(sys.path[0], "me.txt")
    logger.info(path)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "bamy@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in ["bamy"]]),
                                "重复公司检索--人工审查",content, path)
    conn.close()

def compare(names):
    import itertools
    logger.info(json.dumps(names, ensure_ascii=False, cls=util.CJsonEncoder))
    v = 0
    vn = 0
    for i in itertools.combinations(names, 2):
        vn += 1
        value = string_distance(i[0],i[1])
        logger.info("%s ,%s -> %s", i[0], i[1], value)
        v += value

    logger.info("total: %s", v/vn)
    return v/vn



def string_distance(stringA,stringB):
    def edit_distance(s1, s2, weights=(1, 1, 2)):

        a, d, m = weights  # weight of add, delete, modify
        len1, len2 = len(s1), len(s2)
        status = [[0 for _ in xrange(len2 + 1)] for _ in xrange(len1 + 1)]
        for i in xrange(len1 + 1):
            status[i][0] = i * d
        for j in xrange(len2 + 1):
            status[0][j] = j * a
        for i in xrange(1, len1 + 1):
            for j in xrange(1, len2 + 1):
                status[i][j] = status[i - 1][j - 1] if s1[i - 1] == s2[j - 1] \
                    else min(status[i - 1][j] + d, status[i][j - 1] + a, status[i - 1][j - 1] + m)
        return status[- 1][- 1]


    edit = float(edit_distance(stringA, stringB, (1, 1, 3)))
    return edit / len(set(stringA) | set(stringB))



def count_companyId():
    ids = []
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    cids = list(mongo.aggre.agg.find({}))
    for cid in cids:
        scids = cid["sourceCompanyIds"]
        for scid in scids:
            sc = conn.get("select id,companyId from source_company where id=%s", scid)
            if sc is not None and sc["companyId"] is not None and sc["companyId"] not in ids:
                ids.append(sc["companyId"])
    conn.close()
    mongo.close()
    logger.info("%s/%s", len(cids), len(ids))

if __name__ == '__main__':

    logger.info("python company_auto")
    while True:
        corp_merge3()
        # corp_decompose2()
        # corp_merge()
        # count_companyId()
        break
        time.sleep(60*10)

