# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("investor_external_invest", stream=True)
logger = loghelper.get_logger("investor_external_invest")

conn = None
mongo = None

# TODO 如果删除错误的数据？
def check(investor):
    aliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                         "investorId=%s and type=12010",
                         investor["id"])
    for alias in aliases:
        gongshang_name = alias["name"].strip().replace("(",u"（").replace(")",u"）")
        gongshang = mongo.info.gongshang.find_one({"name": gongshang_name}, {"invests": 1})
        if gongshang is None:
            continue
        invests = gongshang.get("invests")
        if invests is None:
            continue
        for invest in invests:
            name = invest["name"]
            _aliases = conn.query("select * from investor_alias where (active is null or active='Y') and "
                              "type=12010 and name=%s", name)
            managers = []
            for _alias in _aliases:
                if investor["id"] != _alias["investorId"]:
                    manager = conn.get("select * from investor where id=%s and (active is null or active='Y')", _alias["investorId"])
                    if manager is not None:
                        managers.append(manager)
                        # TODO 排除企业投资者
            if len(managers) == 1:
                manager_id = managers[0]["id"]
                logger.info("%s->%s managed by %s", gongshang_name, name, manager_id)
                ext = conn.get("select * from investor_external_invest where investorId=%s and managerId=%s",
                               investor["id"], manager_id)
                if ext is None:
                    conn.insert("insert investor_external_invest(investorId,name,managerId,createTime,modifyTime) "
                                "values(%s,%s,%s,now(),now())",
                                investor["id"], name, manager_id)
                # exit()
            elif len(managers) > 1:
                logger.info("Error! %s->%s managed by %s", gongshang_name, name, ",".join(i["name"] for i in managers))


def main():
    global conn, mongo
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    _id = 0
    while True:
        investors = conn.query("select * from investor where id>%s order by id limit 100", _id)
        if len(investors) == 0:
            break
        for investor in investors:
            _id = investor["id"]
            if investor["active"] == 'N':
                continue
            logger.info("**** %s ****", investor["name"])
            check(investor)
    mongo.close()
    conn.close()


if __name__ == '__main__':
    while True:
        main()
        break
        time.sleep(3600*24)  #24hour