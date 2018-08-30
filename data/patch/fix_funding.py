# -*- coding: utf-8 -*-
import os, sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("fix_funding", stream=True)
logger = loghelper.get_logger("fix_funding")

conn = db.connect_torndb()


def guess(items):
    for item in items:
        if item["type"] == "text":
            text = item["text"].strip()
            if text in [',',u'，',u'、']:
                if text == ',':
                    text += " "
                return text
    return ", "


def main():
    funding_id = 0
    while True:
        fundings = conn.query("select f.*, c.name from funding f join company c on f.companyId=c.id "
                              "where (f.active is null or f.active='Y') and "
                              "(c.active is null or c.active='Y') and "
                              "f.id>%s "
                              "order by f.id limit 100", funding_id)
        if len(fundings) == 0:
            break

        flag = False
        for funding in fundings:
            funding_id = funding["id"]
            # logger.info("fundingId: %s", funding_id)
            investors_json = funding["investors"]
            if investors_json is None or investors_json.strip() == "":
                continue
            items = json.loads(investors_json)
            _items = []
            split_char = guess(items)
            pre_type = None
            for item in items:
                this_type = item["type"]
                if(this_type=="investor" and this_type==pre_type):
                    logger.info("company: %s, fundingId: %s, investors: %s", funding["name"], funding_id, investors_json)
                    flag = True
                    _items.append({"text":split_char,"type":"text"})
                pre_type = this_type
                _items.append(item)

            if flag:
                _investors_json = json.dumps(_items)
                logger.info(_investors_json)
                conn.update("update funding set investors=%s where id=%s", _investors_json, funding_id)
                # exit()


def check():
    funding_id = 0
    while True:
        fundings = conn.query("select f.*, c.name from funding f join company c on f.companyId=c.id "
                              "where (f.active is null or f.active='Y') and "
                              "(c.active is null or c.active='Y') and "
                              "f.id>%s "
                              "order by f.id limit 100", funding_id)
        if len(fundings) == 0:
            break

        for funding in fundings:
            funding_id = funding["id"]
            investors_json = funding["investors"]
            if investors_json is None or investors_json.strip() == "":
                continue
            items = json.loads(investors_json)
            for item in items:
                if item["type"] != "investor":
                    continue
                investor = conn.get("select * from investor where id=%s", item["id"])
                if investor["active"] == 'N':
                    logger.info("[Investor deleted] company: %s fundingId: %s, investorId: %s", funding["name"], funding_id, item["id"])
                else:
                    name = item["text"].strip()
                    if investor["name"] != name:
                        investor_alias = conn.get("select * from investor_alias where (active is null or active='Y') and investorId=%s and name=%s limit 1",
                                                  item["id"], name)
                        if investor_alias is None:
                            logger.info("[InvestorAlias deleted] company: %s, fundingId: %s, investorId: %s, name: %s", funding["name"], funding_id, item["id"], name)

if __name__ == "__main__":
    main()
    # check()