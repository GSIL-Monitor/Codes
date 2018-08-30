# -*- coding: utf-8 -*-
# 主题最新加入的公司，用于pc web版首页显示
import os, sys
import time
import datetime
import json
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("latest_topic_company", stream=True)
logger = loghelper.get_logger("latest_topic_company")

'''
+----+-----------------------------------------------+
| id | name                                          |
+----+-----------------------------------------------+
|  1 | 36氪报道的早期项目实时追踪                    |
|  6 | 新进iOS总榜前50的创业公司追踪                 |
|  7 | 分榜前50-新入iOS分榜创业公司追踪              |
|  8 | 近期安卓市场下载激增的创业公司                |
|  9 | BAT背景创业者的新项目追踪                     |
| 10 | 北大清华创业者的新项目追踪                    |
| 12 | 铅笔道报道的早期项目实时追踪                  |
| 13 | 猎云网报道的早期项目实时追踪                  |
| 28 | 红杉真格经纬IDG在投什么新案子                 |
| 29 | BAT的资本布局                                 |
| 30 | 首次被公开报道的项目提醒                      |
| 52 | 正在融资项目推送                              |
+----+-----------------------------------------------+
'''
def main():
    logger.info("start...")
    conn = db.connect_torndb()
    items = list(conn.query("select c.* from topic t "
                       "join topic_company tc on t.id=tc.topicId "
                       "join company c on tc.companyId=c.id "
                       "where t.id in (1,6,7,8,9,10,12,13,28,29,30,52) and "
                       "(t.active is null or t.active='Y') and "
                       "tc.active='Y' and "
                       "(c.active is null or c.active='Y') and "
                       "c.verify='Y' "
                       "order by tc.publishTime desc "
                       "limit 100"))
    items.reverse()

    conn.execute("delete from latest_topic_company")

    for item in items:
        cs = conn.query("select * from latest_topic_company where companyId=%s", item["id"])
        if len(cs) > 0:
            continue
        in_fundings = conn.query("select * from topic_company where topicId=26 and companyId=%s and "
                                 "publishTime>date_sub(now(), interval 3 day)",
                     item["id"])
        if len(in_fundings) > 0:
            continue
        conn.insert("insert latest_topic_company(companyId,createTime,modifyTime) values(%s,now(),now())",
                    item["id"])


    # result = conn.get("select min(id) id from latest_topic_company order by id desc limit 100")
    # id = result["id"]
    # conn.execute("delete from latest_topic_company where id<%s", id)
    conn.close()
    logger.info("end.")


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)