# -*- coding: utf-8 -*-
# track私有化部署，同步company和message

import os, sys
import traceback
import time
import requests
import json
import hashlib

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db
import email_helper

#logger
loghelper.init_logger("sync_data", stream=True)
logger = loghelper.get_logger("sync_data")


def sign(org, data):
    tmp = {}
    for (k, v) in data.items():
        if k != "signature" and k != "payload":
            tmp[k] = v
    for (k, v) in data["payload"].items():
        tmp[k] = v
    # logger.info(tmp)

    str_sign = ""
    for key in sorted(tmp.keys()):
        str_sign += key + str(tmp[key])
    str_sign += org["accesskeysecret"]
    logger.info(str_sign)
    sha = hashlib.sha1()
    sha.update(str_sign.encode())
    signature = sha.hexdigest().lower()
    return signature


def datetime_2_string(d):
    if d is None:
        return None
    if d.year<1900:
        return None
    return d.strftime("%Y-%m-%d %H:%M:%S")


def sync_company(company, org):
    if company["code"] is None:
        return

    if company["name"] is None:
        return

    conn = db.connect_torndb()
    corporate = conn.get("select * from corporate where id=%s", company["corporateId"])
    if corporate is None:
        conn.close()
        logger.info("No corporate! companyId: %s", company["id"])
        return False

    ss = conn.query("select name from corporate_alias where corporateId=%s and (active is null or active='Y')",
                    corporate["id"])
    corporate_alias = "##".join([s["name"] or "" for s in ss])

    ss = conn.query("select name from company_alias where companyId=%s and (active is null or active='Y')",
                    company["id"])
    company_alias = "##".join([s["name"] or "" for s in ss])

    ss = conn.query("select name from artifact where companyId=%s and (active is null or active='Y') and"
                    " name is not null and name != '' limit 100",
                    company["id"])
    product_names = "##".join([s["name"] or "" for s in ss])

    location = conn.get("select * from location where locationId=%s", corporate["locationId"])
    tags = conn.query("select t.* from company_tag_rel r join tag t on r.tagId=t.id where"
                      " (t.active is null or t.active='Y') and"
                      " (r.active is null or r.active='Y') and"
                      " r.companyId=%s order by confidence desc limit 5", company["id"])
    str_tags = json.dumps([t["name"] for t in tags])
    conn.close()


    location_name = None
    if location is not None:
        location_name = location["locationName"]
    logo = None
    if company["logo"] is not None:
        logo = "http://www.xiniudata.com/file/" + company["logo"]

    url = org["apihost"] + "/api_track/syncdata/company"
    headers = {'content-type': 'application/json'}
    data = {
        "accesskeyid": org["accesskeyid"],
        "payload": {
            "code": company["code"],
            "tags": str_tags,
            "name": company["name"],
            "fullName": corporate["fullName"],
            "website": company["website"],
            "description": company["description"],
            "round": corporate["round"],
            "companyStatus": company["companyStatus"],
            "location": location_name,
            "logo": logo,
            "establishDate":datetime_2_string(corporate["establishDate"]),
            "createTime": datetime_2_string(company["createTime"]),
            "modifyTime": datetime_2_string(company["modifyTime"]),
            "verify": company["verify"],
            "active": company["active"],
            "corporateAlias": corporate_alias,
            "companyAlias": company_alias,
            "productNames": product_names
        }
    }
    signature = sign(org, data)
    data["signature"] = signature

    times = 0
    while True:
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        except:
            traceback.print_exc()
            continue

        if r.status_code == 200:
            resp = r.json()
            if resp["code"] != 0:
                logger.info(resp)
                # return False
            else:
                break
        else:
            logger.info(r)
            #return False
        times += 1
        if times >= 3:
            str = u"私有部署(orgId: %s)同步公司出错！" % org["organizationId"]
            email_helper.send_mail(u"烯牛数据", u"烯牛数据", "noreply@xiniudata.com", "arthur@xiniudata.com",
                                   str, str)
            return False
        time.sleep(60)

    return True


def sync_all_companies(org_id, start):
    conn = db.connect_torndb()
    org = conn.get("select * from org_private_conf where organizationId=%s", org_id)
    conn.close()
    if org is None:
        return

    _id = start
    while True:
        conn = db.connect_torndb()
        items = conn.query("select * from company where id>%s order by id limit 100", _id)
        conn.close()

        if len(items) == 0:
            break

        for item in items:
            _id = item["id"]
            logger.info("companyId: %s", _id)
            flag = sync_company(item, org)
            if flag is False:
                logger.error("sync fail! companyId: %s", _id)
                # exit()

    conn = db.connect_torndb()
    conn.update("update org_private_conf set syncTimeline=now() where organizationId=%s",
                org_id)
    conn.close()


def sync_companies(org):
    logger.info("sync company, org: %s", org["organizationId"])
    conn = db.connect_torndb()
    items = conn.query("select * from company where modifyTime>%s order by modifyTime", org["syncTimeline"])
    conn.close()

    modifyTime = None
    for item in items:
        _id = item["id"]
        modifyTime = item["modifyTime"]
        logger.info("companyId: %s", _id)
        flag = sync_company(item, org)
        if flag is False:
            logger.error("sync fail! companyId: %s", _id)
            return

    if len(items) > 0:
        conn = db.connect_torndb()
        conn.update("update org_private_conf set syncTimeline=%s where id=%s",
                    modifyTime, org["id"])
        conn.close()


def sync_all_messages(org_id, start):
    conn = db.connect_torndb()
    org = conn.get("select * from org_private_conf where organizationId=%s", org_id)
    conn.close()
    if org is None:
        return

    _id = start
    while True:
        conn = db.connect_torndb()
        items = conn.query("select * from company_message where id>%s and relateType in (10,50,70) "  # 新闻 工商 融资
                           "order by id limit 100", _id)
        conn.close()

        if len(items) == 0:
            break

        for item in items:
            _id = item["id"]
            logger.info("companyMessageId: %s", _id)
            flag = sync_message(item, org)
            # exit()
            if flag is False:
                logger.error("sync fail! companyMessageId: %s", _id)
                # exit()

    conn = db.connect_torndb()
    conn.update("update org_private_conf set syncMessageTimeline=now() where organizationId=%s",
                org_id)
    conn.close()


def sync_messages(org):
    logger.info("sync message, org: %s", org["organizationId"])
    conn = db.connect_torndb()
    items = conn.query("select * from company_message where modifyTime>%s and relateType in (10,50,70) "
                       "order by modifyTime", org["syncMessageTimeline"])
    conn.close()

    modifyTime = None
    for item in items:
        _id = item["id"]
        modifyTime = item["modifyTime"]
        logger.info("companyMessageId: %s", _id)
        flag = sync_message(item, org)
        if flag is False:
            logger.error("sync fail! companyMessageId: %s", _id)
            return

    if len(items) > 0:
        conn = db.connect_torndb()
        conn.update("update org_private_conf set syncMessageTimeline=%s where id=%s",
                    modifyTime, org["id"])
        conn.close()


def sync_message(message, org):
    if message is None:
        return

    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", message["companyId"])
    if company is None:
        conn.close()
        logger.info("No company! companyId: %s", message["companyId"])
        return False
    conn.close()

    data = {
        "accesskeyid": org["accesskeyid"],
        "payload": {
            "id": message["id"],
            "code": company["code"],
            "message": message["message"],
            "trackDimension": message["trackDimension"],
            "relateType": message["relateType"],
            "relateId": message["relateId"],
            "detailId": message["detailId"],
            "publishTime":datetime_2_string(message["publishTime"]),
            "active": message["active"]
        }
    }
    signature = sign(org, data)
    data["signature"] = signature

    url = org["apihost"] + "/api_track/syncdata/message"
    headers = {'content-type': 'application/json'}
    times = 0
    while True:
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        except:
            traceback.print_exc()
            continue

        if r.status_code == 200:
            resp = r.json()
            if resp["code"] != 0:
                logger.info(resp)
                # return False
                if resp["code"] == 1:
                    sync_company(company, org)
                    continue
            else:
                break
        else:
            logger.info(r)
            # return False
        times += 1
        if times >= 3:
            str = u"私有部署(orgId: %s)同步消息出错！" % org["organizationId"]
            email_helper.send_mail(u"烯牛数据",u"烯牛数据", "noreply@xiniudata.com", "arthur@xiniudata.com",
                                   str, str)
            return False
        time.sleep(60)

    return True


def main():
    conn = db.connect_torndb()
    conn.update("update company set modifyTime=createTime where modifyTime is null")
    orgs = conn.query("select * from org_private_conf where active='Y'")
    conn.close()
    for org in orgs:
        try:
            sync_companies(org)
            sync_messages(org)
        except:
            traceback.print_exc()
            pass


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        while True:
            logger.info("Start...")
            main()
            logger.info("End.")
            time.sleep(60)
    else:
        type = sys.argv[1]
        org_id = sys.argv[2]
        start = 0
        if len(sys.argv) >= 3:
            start = int(sys.argv[2])

        if type == "company":
            sync_all_companies(org_id, start)
        if type == "message":
            sync_all_messages(org_id, start)
