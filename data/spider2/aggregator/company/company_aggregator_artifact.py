# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util
import helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../artifact'))
import artifact_recommend
import set_artifact_rank

#logger
loghelper.init_logger("company_aggregator_artifact", stream=True)
logger = loghelper.get_logger("company_aggregator_artifact")


def aggregate_artifact(company_id,source_company_id, test=False):
    table_names = helper.get_table_names(test)

    # artifact
    conn = db.connect_torndb()
    sas = list(conn.query("select * from source_artifact where sourceCompanyId=%s", source_company_id))
    for sa in sas:
        if sa["active"] == "Y" or sa["active"] is None:
            if sa["domain"] is not None and sa["domain"].strip() != "":
                artifact = conn.get("select * from " + table_names["artifact"] + " where companyId=%s and type=%s and domain=%s limit 1",
                                    company_id, sa["type"], sa["domain"])
            else:
                artifact = conn.get("select * from " + table_names["artifact"] + " where companyId=%s and type=%s and link=%s limit 1",
                                    company_id, sa["type"], sa["link"])

            if artifact is None:
                logger.info("type: %s, link: %s, domain: %s", sa["type"], sa["link"], sa["domain"])
                artifact_id = aggregator_db_util.insert_artifact(company_id, sa, test)
                art = conn.get("select * from artifact where id=%s", artifact_id)
                set_artifact_rank.set_artifact_rank(art)

    if not test:
        conn.update("update artifact set recommend=null where companyId=%s and recommend='Y'", company_id)
        artifact = artifact_recommend.get_recommend_artifact(company_id)
        if artifact:
            conn.update("update artifact set recommend='Y' where id=%s", artifact["id"])

    conn.close()
