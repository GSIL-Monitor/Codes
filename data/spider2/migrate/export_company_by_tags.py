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
    tags_str = sys.argv[1]

    logger.info("Begin...")
    tags = tags_str.split(",")

    f = xlwt.Workbook()

    conn = db.connect_torndb()
    for tag in tags:
        logger.info(tag)
        item = conn.get("select * from tag where name=%s",tag)
        cs = conn.query("select * from company_tag_rel where tagId=%s", item["id"])

        t = f.add_sheet(tag.decode('utf8'))
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
            if c["establishDate"] is not None:
                t.write(line,3,c["establishDate"].strftime('%Y.%m'))
            t.write(line,4,location["locationName"])
            t.write(line,5,round)
            t.write(line,6, ", ".join(links))
            t.write(line,7,c["description"])
            line += 1
    conn.close()
    f.save('logs/%s.xls' % tags_str)

    logger.info("End.")