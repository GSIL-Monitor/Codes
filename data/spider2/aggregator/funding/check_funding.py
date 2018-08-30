# -*- coding: utf-8 -*-
#重新聚合融资信息
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import funding_aggregator
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../company'))
import company_decompose
import patch_company_round
#logger
loghelper.init_logger("regenerate_funding", stream=True)
logger = loghelper.get_logger("regenerate_funding")

def check_funding_by_sort(fundings):
    flag = True
    fdDict = {}
    for funding in fundings:
        if funding["round"] is not None: fdDict.setdefault(int(funding["round"]), []).append(funding)
    fdTuple = sorted(fdDict.iteritems(), key=lambda d: d[0], reverse=True)
    # logger.info(fdTuple)
    roundDate = None
    for fdround in fdTuple:
        if len(fdround[1]) > 1: flag = False; logger.info(fdTuple);logger.info("funding DOUBLE!"); break
        if roundDate is None:
            roundDate = fdround[1][0]["fundingDate"]
        else:
            if fdround[1][0]["fundingDate"] is not None and roundDate is not None and roundDate < fdround[1][0]["fundingDate"]:
                logger.info(fdTuple)
                logger.info("funding WRONG !")
                flag = False; break
    return flag

def find_company_by_name(names):
    companyIds = []
    for name in names:
        name = name_helper.company_name_normalize(name)
        conn = db.connect_torndb()
        companies = conn.query("select * from company where fullName=%s and (active is null or active !='N') order by id desc", name)
        companyIds.extend([company["id"] for company in companies if company["id"] not in companyIds])
        # logger.info("a: %s",companyIds)
        companies2 = conn.query( "select * from company where name=%s and (active is null or active !='N') order by id desc", name)
        companyIds.extend([company["id"] for company in companies2 if company["id"] not in companyIds])
        # logger.info("b: %s", companyIds)
        # company_alias = conn.query("select distinct a.companyId from company_alias a join company c on c.id=a.companyId where (c.active is null or c.active !='N') \
        #                            and (a.active is null or a.active !='N') and a.name=%s order by c.id desc", name)
        # companyIds.extend([company["companyId"] for company in company_alias if company["companyId"] not in companyIds])
        # logger.info("c: %s", companyIds)
    return companyIds


def famous_cids():
    fcids = []
    fp = open("company_famous.txt")
    lines = fp.readlines()
    for line in lines:
        names = [name for name in line.strip().split("#") if name is not None and name.strip() != ""]
        fcids.extend([int(id) for id in find_company_by_name(names) if id not in fcids])
    return fcids



if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cids = famous_cids()
    logger.info(cids)
    # cs = conn.query("select distinct companyId from funding where (active is null or active='Y') and round=1110")
    # cids.extend([int(c["companyId"]) for c in cs if int(c["companyId"]) not in cids])

    # cids = [26745, 169396, 9055, 3615, 2465, 11704, 12450, 22608, 168981, 132501, 108206, 121077, 93544, 45433, 35559, 27103, 19557, 18160,
    #         13082, 12218, 8811, 8746, 6485, 6483, 6357, 5987, 4237, 30189, 18201, 11135, 9584, 3054, 1177, 7703, 30533, 10483, 7705, 55628,
    #         5655, 10721, 37037, 28048, 2617]

    num = 0; num1 =0; num2 =0; num3 = 0; num4 = 0; num5 = 0; num6 = 0
    tot = len(cids)
    regids = []
    regids2 = []
    for cid in cids:
        company = conn.get("select * from company where (active is null or active='Y') and id=%s", cid)
        # 摩拜单车,ofo
        if company is None: continue
        num+=1
        patch_company_round.process(cid)
        fundings_all = conn.query("select * from funding where companyId=%s and (active is null or active='Y')", cid)
        fundings_checked = [funding for funding in fundings_all if ((funding["createUser"] is not None and funding["createUser"] != -2) or funding["modifyUser"] is not None)]

        if len(fundings_checked) > 0: continue
        num1 += 1

        scs = list(conn.query("select * from source_company where (active is null or active='Y') and (source is not null and source != "
                              "13002 and (source < 13100 or source >= 13110)) and companyStatus!=2020 and companyId=%s order by source",
                              cid))
        if len(scs) == 0:
            num2 += 1
        elif len(scs) == 1:
            num3 += 1
        else:
            logger.info("company : %s|%s|%s has %s source companies", company["id"], company["code"], company["name"],
                        len(scs))
            for sc in scs:
                logger.info("**********%s, %s, %s, %s", sc["source"], sc["sourceId"], sc["name"], sc["fullName"])
            logger.info("\n")
            flag = False
            for sc in scs:
                if sc["name"] != company["name"] and sc["fullName"] != company["fullName"]: flag = True; break
            if flag is True:
                num5 += 1
                regids2.append(cid)
                # logger.info("company : %s|%s|%s has %s source companies", company["id"], company["code"], company["name"], len(scs))
                # for sc in scs:
                #     logger.info("**********%s, %s, %s, %s", sc["source"], sc["sourceId"], sc["name"], sc["fullName"])
                # logger.info("\n")
                flag2 = check_funding_by_sort(fundings_all)
                if flag2 is False:
                    logger.info("funding NOT!")
                    regids.append(cid)
                    num6 += 1
                logger.info("\n")


            num4 += 1


    logger.info("%s, %s, %s|%s|%s, %s/%s/%s", num2, num3, num6, num5, num4, num1, num, tot)
    logger.info(regids)
    logger.info(regids2)

    # for cid in [10483]:
    #     company_decompose.decompose(cid, hard=True)
    logger.info("End.")