# -*- coding: utf-8 -*-
import os, sys
import time
import pandas as pd

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("qmp_coin", stream=True)
logger = loghelper.get_logger("qmp_coin")

mongo = db.connect_mongo()

def main():
    cnt = 0
    cnt_lost = 0
    result = []
    pages = []
    items = list(mongo.raw.qmp.find({"url":"http://pro.api.qimingpian.com/d/digitalCurrency"}))
    for item in items:
        ls = item["data"]["list"]
        for l in ls:
            data = (l["product"],l["product_detail"])
            if data not in result:
                result.append(data)
                cnt += 1
                page = item["postdata"]["page"]
                if page not in pages:
                    pages.append(page)

    losts = {
        "product": [],
        "detail": []
    }
    for product, detail in result:
        tmps = detail.split("id=")
        if len(tmps)!=2:
            continue
        id = tmps[1]
        # logger.info("id: %s", id)

        item = mongo.raw.qmp.find_one({"url":{"$in":["http://vip.api.qimingpian.com/d/c3","http://pro.api.qimingpian.com/d/c3"]},
                                              "postdata.id": id})
        if item is None:
            logger.info("%s, %s", product, detail)
            cnt_lost += 1
            losts["product"].append(product)
            losts["detail"].append(detail)

    logger.info("total: %s, lost: %s", cnt, cnt_lost)
    df = pd.DataFrame(losts)
    df.to_excel('logs/coins.xlsx', index=False, columns=["product", "detail"])


if __name__ == "__main__":
    main()
