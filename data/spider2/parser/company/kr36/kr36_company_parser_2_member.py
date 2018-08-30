# -*- coding: utf-8 -*-
import os, sys
import datetime,time
import json
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
from kr36_location import kr36_cities


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper
import util, name_helper, url_helper, download, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("36kr_company_parser_2_member", stream=True)
logger = loghelper.get_logger("36kr_company_parser_2_member")

SOURCE = 13022  #36kr
TYPE = 36005    #公司信息

download_crawler = download.DownloadCrawler(use_proxy=False)


def process():
    logger.info("36kr_company_parser begin...")

    start = 0
    while True:
        items = parser_db_util.find_process_limit(SOURCE, TYPE, start, 1000)
        # items = [parser_db_util.find_process_one(SOURCE,TYPE,9258)]
        for item in items:
            # try:


            source_company_id = parser_db_util.get_company(SOURCE, item["key"])
            logger.info("sourcecid: %s", source_company_id)
            parseMember_save(source_company_id["id"], item, download_crawler)


            # except Exception, E:
            #     logger.info(E)
            #     pass
            # if flag:
            parser_db_util.update_processed(item["_id"])
            logger.info("processed %s" ,item["url"])

            conn = db.connect_torndb()
            conn.update("update source_company set processStatus=1 where id=%s", source_company_id["id"])
            conn.close()
            # else:
            #     logger.info("lack something:  %s", item["url"])

            #break
        # break
        if len(items) == 0:
            break

    logger.info("36kr_company_parser end.")




def parseMember_save(source_company_id, item, download_crawler):
    logger.info("parseMember_save")
    if item["content"].has_key("member") is False:
        return

    members = item["content"]["member"]["data"]["members"]
    for m in members:
        if not m.has_key("name"):
            continue

        logger.info(m["name"])

        desc = m.get("intro")
        position = m.get("position","")


        logo = m.get("avatar")
        if logo:
            logo = logo.replace("https://","http://")
        source_member = {
            "source": SOURCE,
            "sourceId": str(m["id"]),
            "name": m["name"],
            "photo_url": logo,
            "weibo": None,
            "location": 0,
            "role": position,
            "description": desc,
            "education": None,
            "work": None
        }
        ptype = name_helper.position_check(position)

        source_company_member_rel = {
            "sourceCompanyId": source_company_id,
            "position": position,
            "joinDate": None,
            "leaveDate": None,
            "type": ptype
        }

        parser_db_util.save_member_standard(source_member, download_crawler, source_company_member_rel)
        # logger.info(source_member)
        # logger.info(source_company_member_rel)




if __name__ == "__main__":
    while True:
        process()
        #break   #test
        time.sleep(60)