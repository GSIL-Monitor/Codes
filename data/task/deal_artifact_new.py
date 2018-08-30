# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, url_helper

#logger
loghelper.init_logger("deal_artifact_new", stream=True)
logger = loghelper.get_logger("deal_artifact_new")


def check(item):
    logger.info("check: %s, %s", item["id"], item["name"])
    deal_id = item["dealId"]
    if deal_id is None:
        set_deal_artifact_new_proceed(item["id"], "F")
        return

    conn = db.connect_torndb()
    deal = conn.get("select * from deal where id=%s", deal_id)
    conn.close()
    if deal is None:
        set_deal_artifact_new_proceed(item["id"], "F")
        return

    company_id = deal["companyId"]

    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where companyId=%s and source=13001 and sourceId=%s",
                  company_id, str(deal_id))
    if sc is None:
        conn.close()
        set_deal_artifact_new_proceed(item["id"], "F")
        return

    if sc["processStatus"] == 2:
        source_artifact_id = item["sourceArtifactId"]
        sa = conn.get("select * from source_artifact where id=%s", source_artifact_id)
        if sa["active"] == 'N':
            set_deal_artifact_new_proceed(item["id"], "F")
        else:
            set_deal_artifact_new_proceed(item["id"], "S")
            a = conn.get("select * from artifact where companyId=%s and type=%s and "
                         "((link=%s and link is not null) or (domain=%s and domain is not null))",
                         company_id, sa["type"],sa["link"],sa["domain"])
            conn.insert("insert deal_artifact_rel(dealId,artifactId,follow,active,createUser,createTime) "
                "values(%s,%s,'Y','Y',%s,now())",
                deal_id,
                a["id"],
                item["createUser"]
                )
    conn.close()


def process(item):
    logger.info("process: %s, %s", item["id"], item["name"])
    deal_id = item["dealId"]
    if deal_id is None:
        set_deal_artifact_new_proceed(item["id"], "F")
        return

    conn = db.connect_torndb()
    deal = conn.get("select * from deal where id=%s", deal_id)
    conn.close()
    if deal is None:
        set_deal_artifact_new_proceed(item["id"], "F")
        return

    company_id = deal["companyId"]

    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where companyId=%s and source=13001 and sourceId=%s",
                  company_id, str(deal_id))
    if sc is None:
        source_company_id = conn.insert("insert source_company(companyId,source,sourceId,createTime,processStatus) "
                                        "values(%s,%s,%s,now(),%s)",
                                        company_id, 13001, str(deal_id),2)
    else:
        source_company_id = sc["id"]

    if item["sourceArtifactId"] is None:
        link = item["link"]
        domain = None
        if item["type"] == 4010:
            link = url_helper.url_normalize(link)
            flag, domain = url_helper.get_domain(link)
            if flag is False:
                domain = None

        sourceArtifactId = conn.insert("insert source_artifact(sourceCompanyId,name,description,link,domain,type,createTime) "
                                       "values(%s,%s,%s,%s,%s,%s,now())",
                                       source_company_id,
                                       item["name"],
                                       item["description"],
                                       link,
                                       domain,
                                       item["type"])
        conn.update("update deal_artifact_new set sourceArtifactId=%s, proceed='Y' where id=%s", sourceArtifactId, item["id"])
        conn.update("update source_company set processStatus=0 where id=%s", source_company_id)
    conn.close()


def set_deal_artifact_new_proceed(id,proceed):
    conn = db.connect_torndb()
    conn.update("update deal_artifact_new set proceed=%s where id=%s", proceed, id)
    conn.close()


if __name__ == '__main__':
    while True:
        logger.info("Start...")
        conn = db.connect_torndb()
        check_items = conn.query("select * from deal_artifact_new where verify='Y' and proceed='Y'")
        items = conn.query("select * from deal_artifact_new where verify='Y' and (proceed is null or proceed='N')")
        conn.close()

        #check if aggregated
        for item in check_items:
            check(item)
            pass

        #create source_company, wait to expand and aggregate
        for item in items:
            process(item)

        logger.info("End.")

        if len(items) == 0:
            time.sleep(60)