# -*- coding: utf-8 -*-
import os, sys
import time
import find_company
import company_aggregator_dev
import company_info_expand
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
import icp_chinaz
import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/screenshot'))
import screenshot_website

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../funding'))
import patch_company_round

#logger
loghelper.init_logger("company_decompose_dev", stream=True)
logger = loghelper.get_logger("company_decompose_dev")



def set_processStatus_zero(company_id, exclude_scid, hard):
    logger.info("Reset other source companies for company: %s", company_id)
    #aggregateGrade 1 聚合等级尽按公司全名查询
    conn = db.connect_torndb()
    if hard is True:
        conn.update("update source_company set processStatus=0, companyId=null, aggregateGrade=1 where companyId=%s and id !=%s",company_id, exclude_scid)
    else:
        conn.update("update source_company set processStatus=0, companyId=null, aggregateGrade=0 where companyId=%s and id !=%s", company_id, exclude_scid)
    conn.close()

def set_funding_processStatus(scid):
    logger.info("Reset source funding for source_company: %s", scid)
    conn = db.connect_torndb()
    conn.update("update source_funding set processStatus=0 where sourceCompanyId=%s", scid)
    conn.close()

def update_column(company, source_company):
    columns = [
        "logo",
        "fullName",
        "description",
        "productDesc",
        "modelDesc",
        "operationDesc",
        "teamDesc",
        "marketDesc",
        "compititorDesc",
        "advantageDesc",
        "planDesc",
        "brief"
    ]

    conn = db.connect_torndb()
    for column in columns:
        sql = "update company set " + column + "=%s where id=%s"
        # if source_company[column] is not None and source_company[column].strip() != "":
        conn.update(sql, source_company[column], company["id"])
    conn.close()


def decompose(company_id, hard=True):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    scs = list(conn.query(
        "select * from source_company where (active is null or active='Y') and (source is not null and source != 13002 and (source < 13100 or source >= 13110)) and companyStatus!=2020 and companyId=%s order by source",
        company_id))
    conn.close()

    if len(scs) < 2:
        logger.info("Company : %s has one active source company, no need decompose", company_id)
        return True

    fullName = company["fullName"]
    name = company["name"]
    description = company["description"]
    # init crawler
    beian_links_crawler = beian_links.BeianLinksCrawler()
    icp_chinaz_crawler = icp_chinaz.IcpchinazCrawler()
    screenshot_crawler = screenshot_website.phantomjsScreenshot()

    for sc in scs:

        company_info_expand.expand_source_company(sc["id"], beian_links_crawler, icp_chinaz_crawler,screenshot_crawler)
        company_aggregator_dev.aggregator(sc)


    return True

def get_company_by_code(code):
    conn = db.connect_torndb()
    company = conn.get("select * from company where code=%s and (active is null or active='Y')",code)
    conn.close()
    return company


if __name__ == '__main__':
    if len(sys.argv) > 1:
        #company_id = int(sys.argv[1])
        code = sys.argv[1]
        company = get_company_by_code(code)
        if company is None:
            logger.info("company %s not exist!",code)
            exit()
        company_id = company["id"]
        flag = decompose(company_id, hard=False)
        logger.info("decompose result: %s", flag)
    else:
        logger.info("python company_decompose <companyId>")
        while True:
            # conn = db.connect_torndb()
            # ts = conn.query("select * from audit_reaggregate_company where type=-1 and processStatus=1")
            # for t in ts:
            #     logger.info("%s: %s", t["id"], t["beforeProcess"])
            #     beforeProcess = t["beforeProcess"]
            #     code = beforeProcess
            #     company = get_company_by_code(code)
            #     flag = ""
            #     if company:
            #         flag = decompose(company["id"])
            #         logger.info("decompose result: %s", flag)
            #
            #     conn.update("update audit_reaggregate_company set processStatus=2, afterProcess=%s "
            #                 "where id=%s",
            #                  flag, t["id"])
            # conn.close()
            #
            # time.sleep(60)
            pass

