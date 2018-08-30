# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db
import xlwt

#logger
loghelper.init_logger("export_collection", stream=True)
logger = loghelper.get_logger("export_collection")

def getRound(round):
    if round is None:
        return ""
    if round < 1010:
        return ""
    if round < 1020:
        return "Angel"
    if round < 1030:
        return "Pre-A"
    if round < 1040:
        return "A"
    if round < 1050:
        return "B"
    if round < 1060:
        return "C"
    if round < 1070:
        return "D"
    if round < 1080:
        return "E"
    if round < 1090:
        return "F"
    if round < 1100:
        return "F+"
    if round < 1110:
        return "Pre-IPO"
    if round < 1120:
        return "IPO"
    if round < 1130:
        return "Acquired"
    return "Stragitic Investment"

if __name__ == '__main__':
    collection_id = int(sys.argv[1])

    file_num = 0
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select * from collection_company_rel where collectionId=%s", collection_id)
    f = xlwt.Workbook()
    t = f.add_sheet("collection")
    line = 0
    for c in cs:
        c = conn.get("select * from company where id=%s", c["companyId"])
        if c["active"] == 'N':
            continue
        location = conn.get("select * from location where locationId=%s", c["locationId"])
        round = getRound(c["round"])
        logger.info(c["name"])
        ws = list(conn.query("select link from artifact where companyId=%s and type=4010 and (active is null or active='Y')", c["id"]))
        links = []
        for w in ws:
            if w["link"] is None:
                continue
            links.append(w["link"])
        t.write(line,0,line+1)
        t.write(line,1,c["name"])
        t.write(line,2,c["fullName"])
        t.write(line,3,c["establishDate"].strftime('%Y.%m'))
        t.write(line,4,location["locationName"])
        t.write(line,5,round)
        t.write(line,6, ", ".join(links))
        t.write(line,7,c["description"])

        column = 8
        docs = conn.query("select * from document where companyId=%s and (active is null or active='Y')", c["id"])
        for doc in docs:
            str = "http://www.xiniudata.com/file/%s/%s" % (doc["link"], doc["name"])
            t.write(line, column, str)
            column += 1
            file_num += 1
        line += 1
    f.save('logs/%d.xls' % collection_id)

    conn.close()
    logger.info("file num: %s", file_num)
    logger.info("End.")