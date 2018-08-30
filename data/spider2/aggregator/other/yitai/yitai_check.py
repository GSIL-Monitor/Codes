# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, config
import db, name_helper, url_helper
import json

# logger
loghelper.init_logger("yitai_check", stream=True)
logger = loghelper.get_logger("yitai_check")


def find_company_by_short_name(short_name):
    # logger.info("find_company_by_short_name")
    if short_name is None or short_name == "":
        return None

    short_name = name_helper.company_name_normalize(short_name)

    conn = db.connect_torndb()
    company = conn.get("select * from company_alias where name=%s and (active is null or active !='N') limit 1",
                       short_name)
    conn.close()
    if company is not None:
        logger.info("find_company_by_short_name 1")
        return company["id"]

    return None

def find_company_by_full_name(full_name):
    # logger.info("find_company_by_full_name")
    if full_name is None or full_name == "":
        return None

    full_name = name_helper.company_name_normalize(full_name)
    conn = db.connect_torndb()
    corporate = conn.get("select * from corporate_alias where name=%s and (active is null or active !='N') limit 1",
                         full_name)
    conn.close()
    if corporate is not None:
        logger.info("find_corporate_by_full_name 1")
        return corporate["id"]

    conn = db.connect_torndb()
    company = conn.get("select * from company_alias where name=%s and (active is null or active !='N') limit 1",
                       full_name)
    conn.close()
    if company is not None:
        logger.info("find_company_by_full_name 1")
        return company["id"]

    return None


def find_company_by_artifact(website):
    type, market, website_domain = url_helper.get_market(website)

    if type == 4010 and website_domain is not None:

        conn = db.connect_torndb()
        artifact = conn.get("select a.* from artifact a join company c on c.id=a.companyId "
                            "where (c.active is null or c.active !='N') and a.type=%s and a.link=%s limit 1",
                            4010, website)
        conn.close()
        if artifact is not None:
            logger.info("find_company_by_artifact 1, %s, %s", artifact["type"], artifact["link"])
            return artifact["companyId"]

        conn = db.connect_torndb()
        artifact = conn.get("select a.* from artifact a join company c on c.id=a.companyId "
                            "where (c.active is null or c.active !='N') and a.type=%s and a.domain=%s limit 1",
                            4010, website_domain)
        conn.close()
        if artifact is not None:
            logger.info("find_company_by_artifact 2, %s, %s", artifact["type"], artifact["domain"])
            return artifact["companyId"]
    return None


if __name__ == '__main__':
    logger.info("Begin...")
    num = 0
    num1 = 0
    conn = db.connect_torndb()
    fp = open("../../../../../xiniu.txt")
    lines = fp.readlines()
    # lines = []
    file = open("../../../../../yitai.txt", "w")
    dataList=[]
    for line in lines:
        # logger.info(line)
        line = json.loads(line)
        num += 1
        # if num>100:break

        if len(line) >= 4:
            if line['companyName'] is not None and line['companyName'].find("公司") >= 0:
                id = find_company_by_full_name(line['companyName'])
                if id is not None:
                    continue
            if line['homepage'] is not None and line['homepage'].find("http") >= 0:
                id = find_company_by_artifact(line['homepage'].strip())
                if id is not None:
                    continue
            if line['projectName'] is not None:
                id = find_company_by_short_name(line['projectName'])
                if id is not None:
                    continue

            num1 += 1
            logger.info("line find nothing -> %s", line)

            file.write(json.dumps(line) + '\n')
            dataList.append(line)
        else:
            num1 += 1

    import pandas as pd
    df = pd.DataFrame(dataList)

    for column in df.columns:
        def illegal(row):
            import re
            content = row[column]
            if content is not None:
                ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
                content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
            return content

        df[column]=df.apply(illegal,axis=1)

    # df['abstract'] = df.apply(illegal, axis=1)
    df.to_excel('yitai.xlsx',index=0)


            # investorIds = [get_investor(name) for name in names if get_investor(name) is not None]
            # investorIds_str = [str(investorId) for investorId in investorIds]
            #
            # if len(investorIds) < 2:
            #     logger.info("Names: %s only match %s investors: %s", ":".join(names), len(investorIds), ":".join(investorIds_str))
            #     continue
            #
            # ts = conn.query("select * from audit_reaggregate_investor where type=1 and beforeProcess like %s",
            #                 "%" + str(investorIds[0]) + "%")
            # exists = False
            # for t in ts:
            #     find = True
            #     for investorId in investorIds:
            #         if t["beforeProcess"].find(str(investorId)) == -1:
            #             find = False
            #             break
            #     if find is True:
            #         logger.info("************Find same request databaseid: %s", t["id"])
            #         exists = True
            #         break
            #
            # if exists is False:
            #     logger.info("Insert %s", ":".join(investorIds_str))
            #     conn.insert("insert audit_reaggregate_investor(type,beforeProcess,createTime,processStatus) "
            #             "values(1,%s,now(),0)", " ".join(investorIds_str))
            # break
    conn.close()

    logger.info("%s, %s, End.", num, num1)
