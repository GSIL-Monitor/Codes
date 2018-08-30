# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json

reload(sys)
sys.setdefaultencoding("utf-8")

import db
import loghelper
import url_helper
import config
import name_helper


#logger
loghelper.init_logger("location_map", stream=True)
logger = loghelper.get_logger("location_map")


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fp = open("location_code_map")
    lines = fp.readlines()
    n =0
    for line in lines:
        infos = line.strip().split()
        # logger.info("%s,%s",line,len(infos))
        if len(infos) != 3:
            continue
        city = infos[2].replace("市","")
        zipcode = infos[0]
        areacode = infos[1]
        # logger.info("%s/%s/%s",city,areacode,zipcode)

        location = conn.get("select * from location where locationName=%s", city)
        if location is not None:
            logger.info("%s/%s/%s",city,areacode,zipcode);n+=1
            conn.update("update location set areacode=%s, zipcode=%s where locationId=%s", areacode, zipcode, location["locationId"])

    conn.close()
    logger.info(n)

