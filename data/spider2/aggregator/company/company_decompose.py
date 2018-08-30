# -*- coding: utf-8 -*-
import os, sys
import time
import find_company
import company_aggregator
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
loghelper.init_logger("company_decompose", stream=True)
logger = loghelper.get_logger("company_decompose")

def delete_old_data(company_id):
    logger.info("Deleting old data for company: %s", company_id)
    conn = db.connect_torndb()
    conn.execute("delete from company_member_rel where companyId=%s", company_id)

    fundings = list(conn.query("select id from funding where companyId=%s and (createUser is null or createUser=-2) and modifyUser is null", company_id))
    for funding in fundings:
        fundingId = funding["id"]
        conn.execute("delete from funding_investor_rel where fundingId=%s", fundingId)
        conn.execute("delete from funding where id=%s", fundingId)
    patch_company_round.process(company_id)

    conn.execute("delete from footprint where companyId=%s", company_id)
    conn.execute("delete from job where companyId=%s", company_id)
    conn.execute("delete from company_alias where companyId=%s", company_id)

    #check artifact
    artifacts = list(conn.query("select id from artifact where companyId=%s", company_id))
    for artifact in artifacts:
        artifactId= artifact["id"]
        deal_artifact = conn.get("select * from deal_artifact_rel where artifactId=%s limit 1", artifactId)
        if deal_artifact is not None:
            logger.info("artifact: %s is in deal_artifact_rel, reserve!!!")
        else:
            conn.execute("delete from source_summary_android where artifactId=%s", artifactId)
            conn.execute("delete from artifact_pic where artifactId=%s", artifactId)
            conn.execute("delete from artifact where id=%s", artifactId)
    conn.close()


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

    reserve_sc = None
    for sc in scs:
        logger.info("source company: %s, source: %s, sourceId: %s", sc["id"], sc["source"], sc["sourceId"])
        if sc["name"].strip() != "" and sc["name"] == name:
            # logger.info("Reserve source company: %s, %s for company: %s, %s", sc["id"], sc["name"], company["id"], company["name"])
            reserve_sc = sc
            break
            # update_column(company,sc)
            # delete_old_data(company_id)
            # company_info_expand.expand_source_company(sc["id"], beian_links_crawler, icp_chinaz_crawler,screenshot_crawler)
            # set_processStatus_zero(company_id, sc["id"])
            # company_aggregator.aggregator(sc)
            # return True
            #
    #Must find one sc for decompose

    # #if no source_company can match company
    # sc_ids = [str(sc["id"]) for sc in scs if sc.has_key("id")]
    # logger.info("Can not locate source companys (%s) for company: %s", sc_ids, company_id)
    # return False
    if reserve_sc is None:
        reserve_sc = scs[0]

    logger.info("Reserve source company: %s, %s for company: %s, %s", reserve_sc["id"], reserve_sc["name"], company["id"], company["name"])
    update_column(company,reserve_sc)
    delete_old_data(company_id)
    company_info_expand.expand_source_company(reserve_sc["id"], beian_links_crawler, icp_chinaz_crawler,screenshot_crawler)
    set_processStatus_zero(company_id, reserve_sc["id"], hard)

    for sc in scs:
        set_funding_processStatus(sc["id"])

    company_aggregator.aggregator(reserve_sc)
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
            conn = db.connect_torndb()
            ts = conn.query("select * from audit_reaggregate_company where type=-1 and processStatus=1")
            for t in ts:
                logger.info("%s: %s", t["id"], t["beforeProcess"])
                beforeProcess = t["beforeProcess"]
                code = beforeProcess
                company = get_company_by_code(code)
                flag = ""
                if company:
                    flag = decompose(company["id"])
                    logger.info("decompose result: %s", flag)

                conn.update("update audit_reaggregate_company set processStatus=2, afterProcess=%s "
                            "where id=%s",
                             flag, t["id"])
            conn.close()

            time.sleep(60)

