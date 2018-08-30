# -*- coding: utf-8 -*-
import os, sys
from pypinyin import lazy_pinyin

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_corporate_round", stream=True)
logger = loghelper.get_logger("patch_corporate_round")


def fix_round(conn,cp):
    if cp["active"] == 'N':
        return

    funding = conn.get("select * from funding where (active is null or active='Y') and corporateId=%s order by fundingDate desc limit 1",
                       cp["id"])
    if funding is None:
        if cp["round"] != -1:
            logger.info("no founding! id: %s, name: %s", cp["id"], cp["name"])
            conn.update("update corporate set round=-1 where id=%s", cp["id"])
            # exit()
    else:
        # if cp["round"] != funding["round"]:
        #     logger.info("round is different! id: %s, name: %s, funding_round: %s, corporate_round: %s", cp["id"], cp["name"], funding["round"], cp["round"])
        #     conn.update("update corporate set round=%s where id=%s", funding["round"], cp["id"])
        #     # exit()
        if cp["round"] is None:
            logger.info("round is different! id: %s, name: %s, funding_round: %s, corporate_round: %s", cp["id"], cp["name"], funding["round"], cp["round"])
            conn.update("update corporate set round=%s where id=%s", funding["round"], cp["id"])
            # exit()
        pass


def main():
    conn = db.connect_torndb_proxy()
    _id = -1
    while True:
        # cps = conn.query("select * from corporate where id>%s order by id limit 1000", _id)
        cps = conn.query("select * from corporate where round is null and (active is null or active !='N')")
        for cp in cps:
            _id = cp["id"]
            fix_round(conn,cp)
        if len(cps) == 0:
            break

    conn.close()


if __name__ == "__main__":
    main()