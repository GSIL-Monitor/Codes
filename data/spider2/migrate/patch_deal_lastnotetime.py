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
            conn.update("update deal_note set modifyTime=createTime "
                        "where dealId=%s and modifyTime is null",
                        d["id"])
            n = conn.get("select * from deal_note where (active is null or active='Y') and dealId=%s "
                         "order by modifyTime desc limit 1",
                         d["id"])
            if n:
                conn.update("update deal set lastNoteTime=%s where id=%s",
                            n["modifyTime"], d["id"])
                #exit()
        conn.close()

        if len(ds) == 0:
            break

    print "End."
