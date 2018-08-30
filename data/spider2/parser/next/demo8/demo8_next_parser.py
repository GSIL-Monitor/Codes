# -*- coding: utf-8 -*-
import os, sys
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import util
import loghelper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("demo8_next_parser", stream=True)
logger = loghelper.get_logger("demo8_next_parser")

SOURCE = 13110  #demo8
TYPE = 36009    #新产品

def process():
    logger.info("Demo8_next_parser begin...")

    items = parser_db_util.find_process(SOURCE, TYPE)

    for item in items:
        logger.info(item["url"])
        r = parse_base(item)
        if r is None:
            continue
        #logger.info(r)
        source_company_id = parser_db_util.save_company(r, SOURCE)
        logger.info("source_company_id=%s", source_company_id)

        parser_db_util.save_company_score(source_company_id, r["score"])
        parser_db_util.save_artifacts(source_company_id, r["artifacts"])

        parser_db_util.update_processed(item["_id"])
        #break

    logger.info("Demo8_next_parser end.")


def parse_base(item):
    if item is None:
        return None

    company_key = item["key"]
    content = item["content"]
    artifacts = []
    link = util.norm_url(content["website"])
    atype, market = util.get_market(link)
    if atype is not None:
        artifacts.append({
                "type":atype,
                "name":content["name"],
                "desc":content["desc"],
                "link":link
        })

    if content["url_android"] is not None:
        artifacts.append({
            "type":4050,
            "name":content["name"],
            "desc":content["desc"],
            "link":util.norm_url(content["url_android"])
        })

    if content["url_ios"] is not None:
        artifacts.append({
            "type":4040,
            "name":content["name"],
            "desc":content["desc"],
            "link":util.norm_url(content["url_ios"])
        })

    return {
        "shortName": content["name"],
        "fullName": None,
        "productName": content["name"],
        "description": None,
        "brief": content["desc"],
        "round": 0,
        "roundDesc": "",
        "companyStatus": 2010,
        "fundingType": 0,
        "locationId": 0,
        "establishDate": None,
        "logo": None,
        "sourceId": company_key,
        "field": None,
        "subField": None,
        "tags": None,
        "type":41020,
        "score":content["score"],
        "artifacts":artifacts
    }


if __name__ == "__main__":
    process()