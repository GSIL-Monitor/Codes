# -*- coding: utf-8 -*-
import datetime
import os, sys
import time,json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import util
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper


#logger
loghelper.init_logger("patch_investor", stream=True)
logger = loghelper.get_logger("patch_investor")


INVE = {}

rmap = {
    1000: '未融资',
    1010: '天使轮',
    1011: '天使轮',
    1020: 'pre-A',
    1030: 'A',
    1031: 'A+',
    1039: 'Pre-B',
    1040: 'B',
    1041: 'B+',
    1050: 'C',
    1060: 'D',
    1070: 'E',
    1080: 'F',
    1090: '后期阶段',
    1100: 'pre-IPO',
    1105: '新三板',
    1106: '新三板定增',
    1110: 'IPO',
    1120: '被收购',
    1130: '战略投资',
    1140: '私有化',
    1150: '债权融资',
    1160: '股权转让',
}

def get_investor():
    conn = db.connect_torndb()
    investors = conn.query("select * from investor where active is null or active ='Y'")
    for investor in investors:
        investor_aliaes = conn.query("select * from investor_alias where investorId=%s and "
                                     "(active is null or active ='Y')", investor["id"])
        ialist = [ia['name'] for ia in investor_aliaes if ia["name"] is not None and ia["name"].strip() != "" and ia["name"]!=investor["name"]]
        ialist1 = [investor["name"]] + ialist
        INVE[str(int(investor["id"]))] = ialist1
    conn.close()



def check_ok():
    fp = open("company.txt", "w")
    mongo = db.connect_mongo()
    cids = list(mongo.aggreTest.fundingTestPatchinvr.find({}))
    for c in cids:
        link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
        line = "%s***%s" % (c["companyId"],link)

        for memo in c["memo"]:
            line += "***%s/%s/%s" % (memo["round"],memo["investor"],memo["matched"])
        line += "\n"

        fp.write(line)

    fp.close()
    mongo.close()


if __name__ == '__main__':
    logger.info("Begin...")
    logger.info("funding investor repatch start ")
    check_ok()
    exit()
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    get_investor()
    logger.info("done investor")
    (n1, n2, n3, n4, n5, n6, n7) = (0, 0, 0, 0, 0, 0, 0)
    cnt = 0
    fs = conn.query("select * from funding where (active is null or active='Y') and investorsRaw is not null")
    for f in fs:
        if f["corporateId"] is None: continue
        corporate = conn.get("select * from corporate where (active is null or active!='N') and id=%s",
                             f["corporateId"])
        if corporate is None: continue

        companies = conn.query("select * from company where (active is null or active!='N') and corporateId=%s",
                             f["corporateId"])

        if len(companies) == 0: continue

        firels = conn.query("select * from funding_investor_rel where (active is null or active='Y') and "
                            "fundingId=%s", f["id"])

        flist = [str(int(firel["investorId"])) for firel in firels if firel["investorId"] is not None]
        # logger.info(flist)

        flag = False
        for inv in INVE:
            if inv in flist: continue
            for name in INVE[inv]:
                if f["investorsRaw"].find(name)>=0:
                    flag = True
                    if f["investors"] is not None and f["investors"].strip() != "":
                        inves = f["investors"].replace("[", "").replace("]", "").replace("},", "}##").split("##")
                        for inve in inves:
                            try:
                                j = json.loads(inve)
                            except:
                                pass

                            if j.has_key("id") is True and j.has_key("type") is True and j["type"] == "investor" \
                                    and j["text"] is not None and j["text"].find(name) >= 0:
                                flag = False
                                break

                    if flag is True:
                        logger.info("%s---%s---%s---%s---%s-->%s|%s|%s",
                                    companies[0]["id"], companies[0]["code"], corporate["id"], f["id"],
                                    rmap.get(f["round"], "未知轮次"), name, INVE[inv][0], inv)

                        if mongo.aggreTest.fundingTestPatchinvr.find_one({'companyId': companies[0]["id"]}) is not None:
                            mongo.aggreTest.fundingTestPatchinvr.update_one({'companyId': companies[0]["id"],
                                                                             "code": companies[0]["code"],
                                                                             "corporateId": corporate["id"]},
                                                                            {'$addToSet':{"memo":{
                                                                                "round":rmap.get(f["round"], "未知轮次"),
                                                                                "fundingId": f["id"],
                                                                                "matched": name,
                                                                                "investor": INVE[inv][0],
                                                                                "investorId": int(inv)}}})
                            pass
                        else:
                            mongo.aggreTest.fundingTestPatchinvr.insert_one({'companyId': companies[0]["id"],
                                                                             "code":companies[0]["code"],
                                                                             "corporateId": corporate["id"]
                                                                             })


                            mongo.aggreTest.fundingTestPatchinvr.update_one({'companyId': companies[0]["id"]},
                                                                            {'$addToSet': {"memo": {
                                                                                "round": rmap.get(f["round"], "未知轮次"),
                                                                                "fundingId": f["id"],
                                                                                "matched": name,
                                                                                "investor": INVE[inv][0],
                                                                                "investorId": int(inv)}}})
                        break
            if flag is True:
                break

        if flag is True:
            n1 += 1

        # cnt = f["id"]


    logger.info("%s/%s/%s/%s/%s/%s", n1, n2, n3, n4, n5, n6)

    conn.close()
    mongo.close()
    logger.info("End.")