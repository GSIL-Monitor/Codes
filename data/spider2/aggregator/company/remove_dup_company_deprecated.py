# -*- coding: utf-8 -*-
import os, sys
import datetime
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db

#logger
loghelper.init_logger("remove_dup_company", stream=True)
logger = loghelper.get_logger("remove_dup_company")

#mongo
mongo = db.connect_mongo()

collection = mongo.raw.dup_company

def find_dup(ids):
    logger.info("%s", ",".join(str(i) for i in ids))
    data = {}
    for id in ids:
        ss = conn.query("select * from source_company where companyId=%s", id)
        locationIds = []
        establishDates = []
        for s in ss:
            if s["locationId"] > 0:
                locationIds.append(s["locationId"])
            if s["establishDate"] is not None:
                establishDates.append(s["establishDate"])

        data[id] = {"locationIds":locationIds, "establishDates":establishDates}

    groups = []
    while True:
        if len(ids) == 0:
            break
        id1 = ids.pop(0)
        matched = []
        for id in ids:
            flag = compare_data(data[id1],data[id])
            if flag:
                matched.append(id)
        if len(matched) > 0:
            group = [id1]
            group.extend(matched)
            groups.append(group)
            for match in matched:
                ids.remove(match)

    return groups

def compare_data(data1, data2):
    locationIds1 = data1["locationIds"]
    locationIds2 = data2["locationIds"]
    for locationId1 in locationIds1:
        for locationId2 in locationIds2:
            if locationId1 == locationId2:
                return True

    dates1 = data1["establishDates"]
    dates2 = data2["establishDates"]
    for date1 in dates1:
        for date2 in dates2:
            if date1.year==date2.year and date1.month==date2.month:
                return True

    return False


def choose_best(group):
    max_round = 0
    round_ids = []
    group_companies = {}
    choosed = None
    best_group = []

    for id in group:
        r = conn.get("select count(*) cnt from source_company where companyId=%s and (source=13020 or source=13030)", id)
        if r["cnt"] > 0:
            best_group.append(id)

    if len(best_group) == 1:
        return best_group[0]

    if len(best_group) > 1:
        group = best_group

    for id in group:
        c = conn.get("select * from company where id=%s", id)
        group_companies[id] = c

    for id in group:
        c = group_companies[id]
        if c["round"] > max_round:
            max_round = c["round"]

    for id in group:
        c = group_companies[id]
        if c["round"] == max_round:
            round_ids.append(id)

    if len(round_ids) == 1:
        return round_ids[0]

    choosed = round_ids.pop(0)
    c = group_companies[choosed]
    max_len = len(c["description"])
    for id in round_ids:
        c = group_companies[id]
        if len(c["description"]) > max_len:
            max_len = len(c["description"])
            choosed = id

    return choosed


def process_dup(group):
    global dup_num
    logger.info("group: %s", ",".join(str(i) for i in group))
    companyId = choose_best(group)
    logger.info("choosed: %s", companyId)
    for id in group:
        if id != companyId:
            #set active='N'
            conn.update("update company set active='N', modifyTime=now() where id=%s", id)
            if collection.find_one({"companyId":id}) is None:
                collection.insert_one({"companyId":id})

            dup_num += 1
            pass

dup_num = 0
if __name__ == '__main__':
    exit()
    logger.info("Begin...")
    conn = db.connect_torndb()
    cs = conn.query("select name,count(*) cnt from company where active is null or active='Y' group by name having cnt>1")
    cnt = 0
    for c in cs:
        logger.info("%s, %s",c["name"],c["cnt"])
        ids = []
        companies = conn.query("select * from company where name=%s",c["name"])
        for company in companies:
            #logger.info("%s, %s, %s", company["id"], company["locationId"], company["establishDate"])
            ids.append(company["id"])
        groups = find_dup(ids)
        for group in groups:
            process_dup(group)

        cnt += 1
        if cnt >= 2:
            #break
            pass
    conn.close()

    logger.info("dup_num=%s", dup_num)
    logger.info("End.")