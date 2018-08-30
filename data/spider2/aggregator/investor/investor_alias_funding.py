# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json

#公司的股东中去探测含有我们已知的机构马甲，但我们却没相关融资信息的公司


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
import name_helper
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/company/itjuzi'))
import parser_db_util
import itjuzi_helper

#logger
loghelper.init_logger("inf_funding", stream=True)
logger = loghelper.get_logger("inf_funding")

def findc(aname):
    rvalue = 0
    conn = db.connect_torndb()
    aname = aname.replace("（开业）","")
    sourceId = util.md5str(aname)
    sc = conn.get("select * from source_company where source=13100 and sourceId=%s", sourceId)
    if sc is None:
        logger.info("wrong")
        exit()
    companyId = sc["companyId"]
    company =  conn.get("select * from company where id=%s", companyId)
    scs = conn.query("select * from source_company where companyId=%s", companyId)
    # if len(scs) == 1 and scs[0]["source"] == 13096 and company is not None:
    if company is not None and company["active"] in ["A","P","N"]:
        # conn.update("update company set brief=%s,locationId=2 where id=%s", brief, companyId)
        # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])

        # if company["active"] == "A":
            rvalue = 1
            # conn.update("update company set brief=%s,locationId=2 where id=%s", brief,companyId)
            # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])


    conn.close()
    return rvalue,companyId


def set_processed(source_fundings):
    conn = db.connect_torndb()
    for s_f in source_fundings:
        conn.update("update source_funding set processStatus=2 where id=%s", s_f["id"])
    conn.close()

def save(investor_id, investor_alias, corporate_id):
    mongo = db.connect_mongo()
    collection = mongo.investor.iaf
    investor = collection.find_one({"investorId": investor_id, "name": investor_alias})
    if investor is None:
        item = {
            "investorId": investor_id,
            "totalNum": 1,
            "name": investor_alias,
            "corporateIds": [corporate_id]
        }
        collection.insert_one(item)
    else:
        if corporate_id not in investor["corporateIds"]:
            collection.update({"_id": investor["_id"]}, {'$addToSet': {"corporateIds": corporate_id}})
            collection.update({"_id": investor["_id"]}, {'$set': {"totalNum": investor["totalNum"] + 1}})
    mongo.close()



def count_all():
    mongo = db.connect_mongo()
    iafs = list(mongo.investor.iaf.find({}))
    for iaf in iafs:
        if iaf.has_key("totalNum2") is True:
            continue
        investors = list(mongo.investor.iaf.find({"investorId": iaf["investorId"]}))
        cids = []
        for inv in investors:
            logger.info(inv["corporateIds"])
            for id in inv["corporateIds"]:
                if id not in cids:
                    cids.append(id)
        mongo.investor.iaf.update({"_id": iaf["_id"]}, {'$set': {"totalNum2": len(cids)}})
    mongo.close()

def export_all():
    mongo = db.connect_mongo()
    conn = db.connect_torndb()
    iafs = list(mongo.investor.iaf.find({}))
    for iaf in iafs:
        investor = conn.get("select * from investor where id=%s", iaf["investorId"])
        line = "%s+++%s+++%s+++%s+++%s+++%s+++%s\n" % (iaf["investorId"],investor["name"],iaf["totalNum2"],
                                                       investor["online"], iaf["name"],
                                                       iaf["totalNum"], ";".join([str(cid) for cid in iaf["corporateIds"]]))
        fp2.write(line)
    mongo.close()
    conn.close()

if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding investor check start ")
    # count_all()
    fp2 = open("company_sh.txt", "w")
    export_all()
    exit()
    # fp2 = open("company_sh.txt", "w")
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    collection_gongshang = mongo.info.gongshang
    # collection = mongo.
    corporates = conn.query("select * from corporate where (active is null or active ='Y')")
    (n1, n2, n3) = (0, 0, 0)
    for corporate in corporates:
        n3 += 1
        iids = []
        investorids = []
        if corporate["fullName"] is not None:
            gongshang = collection_gongshang.find_one({"name": corporate["fullName"]})
            if gongshang is not None and gongshang.has_key("investors"):
                for ginvestor in gongshang["investors"]:
                    if ginvestor.has_key("type") and ginvestor.has_key("name") and \
                            (ginvestor["type"].find("企业") >= 0 or ginvestor["type"].find("公司") >= 0) and \
                            (ginvestor["name"] is not None and ginvestor["name"].strip() != ""):
                        investor_aliaes = conn.query("select i.name as iname, ia.* from investor i join "
                                                     "investor_alias ia on i.id=ia.investorId where "
                                                     "(i.active is null or i.active='Y') "
                                                     "and (ia.active is null or ia.active='Y') and ia.verify='Y' "
                                                     "and ia.name=%s", ginvestor["name"])
                        for ia in investor_aliaes:
                            logger.info("corporate :%s/%s has investor :%s/%s/%s", corporate["id"], corporate["fullName"],
                                        ia["name"], ia["investorId"], ia["iname"])
                            iids.append({"id":int(ia["investorId"]),
                                         "ia_name":ia["name"]})

            if len(iids) > 0:
                fundings = conn.query("select * from funding where corporateId=%s and (active is null or active ='Y')",
                                      corporate["id"])
                for f in fundings:
                    rels = conn.query("select * from funding_investor_rel where (active is null or active='Y') "
                                      "and fundingId=%s",f["id"])

                    for rel in rels:
                        if int(rel["investorId"]) not in investorids:
                            investorids.append(int(rel["investorId"]))
            flag = True
            for iid in iids:
                if iid["id"] not in investorids:
                    logger.info("******\ncorporate :%s/%s has investor :%s/%s \n******\n\n",
                                corporate["id"], corporate["fullName"],
                                iid["id"], iid["ia_name"])
                    n1 += 1
                    save(iid["id"], iid["ia_name"],int(corporate["id"]))
                    flag = False

            if flag is False:
                n2 += 1





    # logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/", n1, n2, n3)
    mongo.close()
    conn.close()
    logger.info("End.")