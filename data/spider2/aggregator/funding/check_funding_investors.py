# -*- coding: utf-8 -*-
#重新聚合融资信息
import os, sys
import time, json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import funding_aggregator
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../company'))
import company_decompose
import patch_company_round
#logger
loghelper.init_logger("regenerate_funding", stream=True)
logger = loghelper.get_logger("regenerate_funding")




if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    funds = conn.query("select * from funding where (active is null or active='Y') and investors is not null")
    # funds = []

    num = 0; num1 =0; num2 =0; num3 = 0; num4 = 0; num5 = 0; num6 = 0
    tot = len(funds)

    for fund in funds:
        num+=1
        investors_raw = fund["investors"]
        investors = investors_raw.replace("[","").replace("]","").replace("},","}##").split("##")
        investors_raw_new = investors_raw
        inv = False
        update = False
        for investor in investors:
            # logger.info(investor)
            # logger.info(type(investor))
            try:
                j = json.loads(investor)
            except:
                logger.info("%s", investor)
                logger.info("%s -> %s", investors_raw, fund["id"])
                exit()
            # logger.info(j)
            if j.has_key("id") is True and j.has_key("type") is True and j["type"] == "investor":
                inv = True
                # logger.info("funding: %s, has %s->%s", fund["id"], j["type"], j["id"])
                num2 +=1
                inves = conn.get("select * from investor where id=%s", j["id"])
                if inves["active"] is not None and inves["active"] == 'N':
                    num3 += 1
                    logger.info("funding: %s, has %s->%s", fund["id"], j["type"], j["id"])
                    logger.info("*****************Not found investor: %s", j["id"])
                    sql = "select * from audit_reaggregate_investor where beforeProcess like '%%"+str(j["id"])+"%%' order by createTime desc limit 1"
                    # logger.info(sql)
                    ari = conn.get(sql)
                    # for ari in aris:
                    #     logger.info("++++++++++++ %s ---->%s", ari["beforeProcess"], ari["afterProcess"])
                    if ari is not None:
                        logger.info("++++++++++++ %s ---->%s", ari["beforeProcess"], ari["afterProcess"])
                        newinvesid = ari["afterProcess"]
                        newinves  = conn.get("select * from investor where id=%s and (active is null or active='Y')", newinvesid)
                        if newinves is None:
                            logger.info("Wrong")
                            exit()
                        else:
                            update = True
                            logger.info("investor : %s,%s should change to %s,%s", inves["id"], inves["name"], newinves["id"], newinves["name"])
                            logger.info("old: %s", investors_raw)
                            investors_raw_new = investors_raw.replace(str(inves["id"]), str(newinves["id"]))
                            logger.info("new: %s", investors_raw_new)
                else:
                    num4 += 1
                    # logger.info("found investor: %s,%s", inves["id"], inves["name"])


        if inv is True: num1+=1

        if update is True:
            conn.update("update funding set investors =%s where id =%s", investors_raw_new, fund["id"])


    logger.info("%s, %s, %s, %s, %s, %s", num, num1, num2, num3, num4, tot)

    c1=0;c2=0;c3=0
    funds = conn.query("select * from funding where (active is null or active='Y')")
    for fund in funds:
        rels = conn.query("select * from funding_investor_rel where fundingId=%s and (active is null or active='Y')", fund["id"])
        for rel in rels:
            c1+=1
            investor = conn.get("select * from investor where id=%s", rel["investorId"])
            if investor is None:
                c2+=1
            elif investor["active"] is not None and investor["active"] =='N':
                logger.info("id=%s/%s", rel["id"], investor["id"] )
                c3+=1
    logger.info("%s/%s/%s", c1, c2, c3)


    logger.info("End.")