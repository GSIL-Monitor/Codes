# -*- coding: utf-8 -*-
import os, sys
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("select_best_company", stream=True)
logger = loghelper.get_logger("select_best_company")


def main():
    cnt = 0
    _id = 0
    while True:
        items = conn.query("select * from company where id>%s order by id limit 100", _id)
        for item in items:
            _id = item["id"]
            if check(item):
                cp = conn.get("select * from corporate where id=%s", item["corporateId"])
                logger.info("%s|%s|%s", item["code"], item["name"], cp["fullName"])
                cnt += 1

        if cnt > 200:
            break


def check(company):
    if company["active"] != 'Y':
        return False
    if company["modifyTime"] < datetime.datetime(2017,7,1):
        return False

    # check funding
    fundings = conn.query("select * from funding where corporateId=%s and "
                          "(active is null or active='Y')",
                          company["corporateId"])
    if len(fundings) == 0:
        return False

    for funding in fundings:
        if funding["verify"] is None:
            return False

    # check news
    items = list(mongo.article.news.find({"companyIds": company["id"]}))
    if len(items) < 5:
        return False

    # check ios, android
    artifacts = conn.query("select * from artifact where companyId=%s and "
                           "(active is null or active='Y') and type=4040",
                           company["id"])
    if len(artifacts) == 0:
        return False

    artifacts = conn.query("select * from artifact where companyId=%s and "
                           "(active is null or active='Y') and type=4050",
                           company["id"])
    if len(artifacts) == 0:
        return False

    # check member
    members = conn.query("select * from company_member_rel where companyId=%s and "
                         "(active is null or active='Y')",
                         company["id"])
    if len(members) == 0:
        return False


    return True


if __name__ == "__main__":
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    main()