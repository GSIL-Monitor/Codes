# -*- coding: utf-8 -*-
import os, sys

reload(sys)

sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper
import db

#logger
loghelper.init_logger("import_deals_funding", stream=True)
logger = loghelper.get_logger("import_deals_funding")

if __name__ == '__main__':
    conn = db.connect_torndb()
    dfile = open("xiniu_deals.txt")
    content = dfile.read()
    dfile.close()
    deals = content.split("******")
    for deal in deals:
        t = deal.split("|||")
        code = t[0]
        if code == "":
            continue
        currency = int(t[4])
        preMoney = int(t[5])
        investment = int(t[6])
        if preMoney == 0:
            preMoney = None
        if investment == 0:
            investment = None
        if preMoney is None and investment is None:
            currency = None

        postMoney = None
        shareRatio = None
        if preMoney is not None and investment is not None:
            postMoney = preMoney + investment
            shareRatio = float(investment) / float(postMoney)
        if currency is not None or preMoney is not None or investment is not None or postMoney is not None or shareRatio is not None:
            logger.info("%s, %s, %s, %s, %s, %s",code,currency,preMoney,investment, postMoney, shareRatio)

            c = conn.get("select * from company where code=%s", code)
            if c is None:
                continue
            d = conn.get("select * from deal where organizationId=1 and companyId=%s",c["id"])
            if d is None:
                logger.info("Deal not found!")
            else:
                conn.update("update deal set currency=%s, preMoney=%s, postMoney=%s,investment=%s,shareRatio=%s where id=%s",
                            currency,preMoney,postMoney,investment,shareRatio, d["id"])
    conn.close()