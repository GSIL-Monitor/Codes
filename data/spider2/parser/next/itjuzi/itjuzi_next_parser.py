# -*- coding: utf-8 -*-
import os, sys
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("itjuzi_next_parser", stream=True)
logger = loghelper.get_logger("itjuzi_next_parser")

SOURCE = 13031  #ITJUZI
TYPE = 36009    #新产品

download_crawler = download.DownloadCrawler()

def process():
    logger.info("itjuzi_next_parser begin...")

    items = parser_db_util.find_process(SOURCE, TYPE)

    for item in items:
        logger.info(item["url"])

        r = parse_base(item)
        if r is None:
            continue
        #logger.info(r)
        source_company_id = parser_db_util.save_company(r, SOURCE, download_crawler)
        logger.info("source_company_id=%s", source_company_id)

        parser_db_util.save_company_score(source_company_id, r["score"])

        artifacts = []
        for artifact in r["artifacts"]:
            link = artifact["link"]
            type, app_market, app_id = url_helper.get_market(link)
            if type is None:
                continue
            if type == 4040 or type == 4050:
                if app_id is None:
                    continue
            artifact["type"] = type
            artifact["domain"] = app_id
            artifacts.append(artifact)

        parser_db_util.save_artifacts(source_company_id, artifacts)

        parser_db_util.update_processed(item["_id"])
        #break

    logger.info("itjuzi_next_parser end.")


def parse_base(item):
    if item is None:
        return None

    company_key = item["key"]
    content = item["content"]

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
        "artifacts":[{
            "name":content["name"],
            "desc":content["desc"],
            "link":url_helper.url_normalize(content["website"])
        }]
    }


if __name__ == "__main__":
    process()