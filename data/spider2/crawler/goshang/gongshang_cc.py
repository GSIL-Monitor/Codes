# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
import random
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper
import name_helper
import util

#logger
loghelper.init_logger("gongshang_summary", stream=True)
logger = loghelper.get_logger("gongshang_summary")

###
# smaller type, higher frequency
###

DATE = None

def add_name(type=0):

    if type == 0:
        #check_all
        pass
    elif type == 1:
        #check famous_investor
        add_famours()

    elif type == 2:
        #check investor_alias
        add_majia()
    elif type == 3:
        #check corporate_alias
        add_corporate_alias()
    elif type == 4:
        #remove inactive name
        remove_corporate_alias()
        pass


def add_famours():
    conn = db.connect_torndb()
    inames = conn.query("select distinct ia.name from investor_alias ia join famous_investor fi on "
                       "ia.investorId = fi.investorId where ia.type=12010 and (ia.active is null or ia.active = 'Y')")
    names = [{"name":iname["name"],"lastCheckTime":None}
             for iname in inames if iname["name"] is not None and iname["name"] != ""]
    save_names(names,1)
    conn.close()

def add_majia():
    conn = db.connect_torndb()
    inames = conn.query("select distinct name from investor_alias where type=12010 and "
                        "(active is null or active = 'Y')")
    names = [{"name": iname["name"], "lastCheckTime": None}
             for iname in inames if iname["name"] is not None and iname["name"] != ""]
    save_names(names, 2)
    conn.close()

def remove_corporate_alias():
    conn = db.connect_torndb()
    inames = conn.query("select * from corporate_alias where type=12010 and "
                        "active = 'N'")
    names = [{"name": iname["name"], "lastCheckTime": None}
             for iname in inames if iname["name"] is not None and iname["name"] != ""]
    save_names(names, 2)
    conn.close()

def add_corporate_alias():
    conn = db.connect_torndb()
    id = 0
    while True:

        inames = conn.query("select * from corporate_alias where "
                            "(active is null or active='Y') and gongshangCheckTime is not null and id>%s"
                            " order by id limit 2000", id)
        names = []
        for iname in inames:
            if iname["id"] > id:
                id = iname["id"]
            if iname["name"] is not None and iname["name"] != "":
                chinese, company = name_helper.name_check(iname["name"])
                if chinese is True:
                    # logger.info("name: %s, time: %s", iname["name"])
                    names.append({"name": iname["name"], "lastCheckTime": iname["gongshangCheckTime"],
                                  "corporateId": int(iname["corporateId"])})
        # names = [{"name": iname["name"], "lastCheckTime": iname["gongshangCheckTime"]}
        #          for iname in inames if iname["name"] is not None and iname["name"] != ""]
        # logger.info(names)
        save_names(names, 3)

        if len(inames) == 0:
            break
    conn.close()



def save_names(names,type, rand=None):
    mongo = db.connect_mongo()
    collection_name = mongo.info.gongshang_name
    for name in names:

        rname = name["name"].strip()
        if rname == "": continue
        name["name"] = rname

        logger.info("add/check name: %s, lastCheckTime :%s, type: %s", name["name"], name.get("lastCheckTime", "null"), type)
        gname = collection_name.find_one({"name": name["name"]})
        if gname is None:
            if rand is None:
                if type == 3:
                    collection_name.insert({"name": name["name"], "type": type, "lastCheckTime": None,
                                            "corporateIds": [name["corporateId"]]})
                else:
                    collection_name.insert({"name": name["name"], "type": type, "lastCheckTime": name["lastCheckTime"]})
            else:
                if type == 3:
                    collection_name.insert({"name": name["name"], "type": type,
                                            "corporateIds": [name["corporateId"]],
                                            "lastCheckTime": datetime.datetime.now() -
                                                             datetime.timedelta(days=random.randint(1, 6))})
                else:
                    collection_name.insert({"name": name["name"], "type": type,
                                            "lastCheckTime": datetime.datetime.now() -
                                                         datetime.timedelta(days=random.randint(1, 6))})
        else:
            #check and update type
            logger.info("here here")
            if gname.has_key("type") is False or (gname["type"] > type):
                collection_name.update_one({"_id": gname["_id"]},{'$set':{"type": type}})
            if type == 3:
                if gname.has_key("corporateIds") is False:
                    collection_name.update_one({"_id": gname["_id"]}, {'$set': {"corporateIds": [name["corporateId"]]}})
                elif name["corporateId"] not in gname["corporateIds"]:
                    collection_name.update_one({"_id": gname["_id"]}, {'$addToSet': {"corporateIds": name["corporateId"]}})

    mongo.close()

def start_run():
    global DATE
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE:
            # init
            add_name(type=3)
            add_name(type=1)
            add_name(type=2)
            DATE = datestr

        time.sleep(60*60)

if __name__ == "__main__":
    start_run()