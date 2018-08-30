# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db

if __name__ == "__main__":
    print "Start..."
    id = 0
    while True:
        conn = db.connect_torndb()
        ds = conn.query("select * from deal where id>%s order by id limit 1000", id)
        for d in ds:
            print "dealId: %s" % d["id"]
            if d["id"] > id:
                id = d["id"]
            if d["assignee"]:
                da = conn.get("select * from deal_assignee where dealId=%s and userId=%s",
                              d["id"], d["assignee"])
                if da is None:
                    conn.insert("insert deal_assignee(dealId,userId,createUser,createTime) "
                                "values(%s,%s,%s,%s)",
                                d["id"], d["assignee"], d["assignee"], d["createTime"])
                    # exit()

                p = conn.get("select * from user_deal_panel where dealId=%s and userId=%s",
                             d["id"], d["assignee"])
                if p is None:
                    conn.insert("insert user_deal_panel(dealId,userId,sort,createTime) "
                                "values(%s,%s,%s,now())", d["id"], d["assignee"], d["id"])
        conn.close()

        if len(ds) == 0:
            break

    print "End."
