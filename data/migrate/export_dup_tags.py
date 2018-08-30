# -*- coding: utf-8 -*-
import os, sys
import pandas as pd

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("export_dup_tag", stream=True)
logger = loghelper.get_logger("export_dup_tag")

conn = db.connect_torndb()

def get_chains(tag_id):
    chains = []
    rels = conn.query("select * from tags_rel where tag2id=%s and type=54041", tag_id)
    for rel in rels:
        chains.append(rel["tagId"])
        upchains = get_chains(rel["tagId"])
        chains.extend(upchains)
    return chains

def main():
    items = conn.query("select tag2Id, count(*) cnt "
            "from tags_rel " 
            "where type=54041 " 
            "group by tag2id "
            "having cnt>1;")
    for item in items:
        dup_tag = conn.get("select * from tag where id=%s", item["tag2Id"])
        rels = conn.query("select * from tags_rel where tag2id=%s and type=54041", item["tag2Id"])
        for rel in rels:
            up_tag = conn.get("select * from tag where id=%s", rel["tagId"])
            rels2 = conn.query("select * from tags_rel where tag2id=%s and type=54041", rel["tagId"])
            if len(rels2)>0:
                for rel2 in rels2:
                    up2_tag = conn.get("select * from tag where id=%s", rel2["tagId"])
                    # logger.info("%s -> %s -> %s", dup_tag["name"], up_tag["name"], up2_tag["name"])
            else:
                logger.info("%s -> %s", dup_tag["name"], up_tag["name"])


if __name__ == '__main__':
    main()