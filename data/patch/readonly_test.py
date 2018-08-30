# -*- coding: utf-8 -*-
import os, sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("readonly_test", stream=True)
logger = loghelper.get_logger("readonly_test")


def test():
    conn = db.connect_torndb()
    conn_readonly = db.connect_torndb_readonly()
    conn_proxy = db.connect_torndb_proxy()

    conn.insert("insert alarm(createTime,modifyTime) values(now(),now())")
    time.sleep(1) # 注意同步需要时间
    item = conn_readonly.get("select * from alarm order by id desc limit 1")
    logger.info(item)

    item = conn_proxy.get("/*master*/ select * from company_message order by id desc limit 1")
    logger.info(item)

    conn_readonly.insert("insert alarm(createTime,modifyTime) values(now(),now())")

    conn_readonly.close()
    conn.close()


if __name__ == '__main__':
    test()