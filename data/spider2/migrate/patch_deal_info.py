# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../nlp/recommend'))
import deal_util

def copy_data_from_company_to_deal(deal_id):
    conn = db.connect_torndb()
    d = conn.get("select * from deal where id=%s", deal_id)
    c = conn.get("select * from company where id=%s", d["companyId"])
    if c is None:
        conn.close()
        return

    flag = False
    if (d["name"] is None or d["name"].strip() == "") and \
        c["name"] is not None and c["name"].strip() != "":
        conn.update("update deal set name=%s where id=%s", c["name"], d["id"])
        flag = True

    if (d["fullName"] is None or d["fullName"].strip() == "") and \
        c["fullName"] is not None and c["fullName"].strip() != "":
        conn.update("update deal set fullName=%s where id=%s", c["fullName"], d["id"])
        flag = True

    if (d["description"] is None or d["description"].strip() == "") and \
        c["description"] is not None and c["description"].strip() != "":
        conn.update("update deal set description=%s where id=%s", c["description"], d["id"])
        flag = True

    if (d["logo"] is None or d["logo"].strip() == "") and \
        c["logo"] is not None and c["logo"].strip() != "":
        conn.update("update deal set logo=%s where id=%s", c["logo"], d["id"])
        flag = True

    if (d["locationId"] is None and c["locationId"] is not None) or \
            (d["locationId"]==0 and c["locationId"] is not None and c["locationId"]>0):
        conn.update("update deal set locationId=%s where id=%s", c["locationId"], d["id"])
        flag = True

    if d["round"]  and c["round"] is not None:
        conn.update("update deal set round=%s where id=%s", c["round"], d["id"])
        flag = True

    if d["establishDate"] is None and c["establishDate"] is not None:
        conn.update("update deal set establishDate=%s where id=%s", c["establishDate"], d["id"])
        flag = True

    deal_tag_cnt = conn.get("select count(*) cnt from deal_tag_rel where dealId=%s", deal_id)
    if deal_tag_cnt["cnt"] == 0:
        company_vip_tags = conn.query("select t.id, t.name, r.confidence, t.confidence tconfidence,t.type from "
                                      "company_tag_rel r join tag t on r.tagId=t.id "
                                      "where t.type=11012 and r.companyId=%s", d["companyId"])
        company_important_tags = conn.query("select t.id, t.name, r.confidence, t.confidence tconfidence,t.type from "
                                      "company_tag_rel r join tag t on r.tagId=t.id "
                                      "where t.type=11011 and r.companyId=%s "
                                            "order by r.confidence desc limit 5",
                                            d["companyId"])
        tags = []
        tags.extend(company_vip_tags)
        tags.extend(company_important_tags)
        for tag in tags:
            deal_tag = conn.get("select * from deal_tag where name=%s and (active='Y' or active is null)",
                                tag["name"])
            if deal_tag is None:
                deal_tag_id = conn.insert("insert deal_tag(name,type,createTime,confidence) values(%s,%s,now(),%s)",
                                          tag["name"], tag["type"], tag["tconfidence"])
            else:
                deal_tag_id = deal_tag["id"]
            conn.insert("insert deal_tag_rel(dealId,dealTagId,createTime,confidence) values(%s,%s,now(),%s)",
                        deal_id, deal_tag_id, tag["confidence"])

    conn.close()

    if flag:
        #exit()
        pass


if __name__ == "__main__":
    print "Start..."
    id = 0
    while True:
        conn = db.connect_torndb()
        ds = conn.query("select * from deal where id>%s and status>19000 order by id limit 1000", id)
        for d in ds:
            print "dealId: %s" % d["id"]
            if d["id"] > id:
                id = d["id"]

            if d["status"] > 19000:
                copy_data_from_company_to_deal(d["id"])

        conn.close()

        if len(ds) == 0:
            break

    print "End."
