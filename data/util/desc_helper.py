#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import util
import loghelper
import db
import hz
import json
import re

#logger
loghelper.init_logger("word_count", stream=True)
logger = loghelper.get_logger("word_count")

def count_chinese(content):
    retList={}
    for uchar in content:
        if hz.is_chinese(uchar):
            # logger.info("chinese: %s",uchar)
            retList[uchar] = 1
    return len(retList)


def count_other(content):
    content = re.sub("[ 　\?\s+\.\!\/_,$%^*(+\"\'-=><『』;]+|[​​​​​​​​／{}‘’·•―–＋\[\]－％\|｜︱【】：；‧+——！，。？、~@#￥%……&*（）《》“”「」]+".decode('utf-8'), "", content)
    other = ""
    for uchar in content:
        if hz.is_other(uchar):
            # logger.info("other: %s",uchar)
            other += uchar
    return other


def count_other2(content):
    other = ""
    for uchar in content:
        if hz.is_other(uchar):
            # logger.info("other: %s",uchar)
            other += uchar
    return other


def check_desc(content, length=5):
    if content is None or content.strip() == "":
        return False

    if len(content) <= length:
        return False

    if hz.is_chinese_string(content):
        if float(len(set(content)))/float(len(content)) <= 0.1:
            num_chinese = count_chinese(content)
            #logger.info("%s->%s",len(set(content)),num_chinese)
            if len(set(content))-num_chinese <= 20:
                return False
    else:
        #logger.info(len(set(content)))
        if len(content) <= 10:
            return False

        if len(set(content)) <= 20:
            if float(len(set(content)))/float(len(content)) <= 0.28:
                return False
    return True



if __name__ == '__main__':
    desc =[]
    conn = db.connect_torndb()
    #companies = conn.query("select id, description, companyId from source_company order by id")
    # companies = conn.query("select id, description, companyId from source_company where (active is null or active='Y') order by id")
    # #companies = conn.query("select * from source_company where id=65197")
    #
    # for company in companies:
    #     if company["description"] is None or company["description"].strip() == "":
    #         continue
    #     flag = check_desc(company["description"])
    #     if flag is False:
    #
    #         if company["companyId"] is None:
    #             pass
    #             #logger.info("%s is new sourceCompany",company["id"])
    #             #set active ='N'
    #         else:
    #             id1 = conn.get("select id,description from source_company where companyId=%s and id!=%s and (active is null or active='Y') limit 1", company["companyId"], company["id"])
    #             if id1 is None:
    #                 logger.info("%s has no other company",company["id"])
    #                 #set active = 'N'
    #             else:
    #                 logger.info("%s has other company %s->%s",company["id"], id1["id"], id1["description"])
    #                 sql1 =  sql = "update source_company set processStatus=1 where id=%s"
    #                 conn.update(sql1, id1["id"])
    #                 #set processStatus=1 and active=N
    #
    #         desc.append(str(company["id"]))
    #
    #         sql = "update source_company set active='N' where id=%s"
    #         conn.update(sql, company["id"])
    #
    # conn.close()
    n = 0
    websites = conn.query("select * from artifact where type=4010 limit 20000")
    for website in websites:
        if website["name"] is None: website["name"] = ""
        if website["description"] is None: website["description"] = ""
        cchinese = count_other(website["name"])+count_other(website["description"])
        if len(cchinese) > 0:
            n+=1
            logger.info("错误: %s",cchinese)
            logger.info("%s:%s - > %s", website["name"], website["description"], website["id"])
            logger.info("\n\n\n")

    #logger.info(sorted(dict.items(), key=lambda d: d[1]))
    logger.info(n)
    logger.info(",".join(desc))
