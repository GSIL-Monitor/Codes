# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_investor_artifact", stream=True)
logger = loghelper.get_logger("migrate_investor_artifact")

conn = db.connect_torndb()


def main():
    investors = conn.query("select * from investor where (active is null or active='Y') and wxid is not null")
    for investor in investors:
        investor_id = investor["id"]
        name = investor["wechatName"]
        domain = investor["wxid"]
        type = 4020
        rel = conn.get("select * from investor_artifact where investorId=%s and type=%s and domain=%s",
                       investor_id, type, domain)
        if rel is not None:
            continue
        logger.info("%s, %s, %s", investor["name"], name, domain)
        conn.insert("insert investor_artifact(investorId,type,name,domain,verify,active,createTime,modifyTime,createUser,modifyUser) "
                    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    investor_id, type, name, domain,
                    investor["verify"], 'Y', investor["createTime"], investor["modifyTime"],
                    investor["createUser"], investor["modifyUser"])


if __name__ == '__main__':
    main()