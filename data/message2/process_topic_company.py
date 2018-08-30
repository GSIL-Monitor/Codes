# -*- coding: utf-8 -*-
import os, sys
import traceback
import process_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("process_topic_company", stream=True)
logger = loghelper.get_logger("process_topic_company")

def process_all():
    # 处理60秒前创建的还未处理的消息
    conn = db.connect_torndb_proxy()
    items = conn.query("select * from topic_company where verify is null and tabStatus=0 and createTime < date_sub(now(), interval 60 SECOND)")
    conn.close()
    for item in items:
        process(item["id"])


def patch_all_sector():
    conn = db.connect_torndb_proxy()
    topic_companies = conn.query("select * from topic_company where active='Y' and sectorStatus=0")
    for topic_company in topic_companies:
        patch_sector(topic_company, _conn=conn)
    conn.close()
    conn.close()


def delete_invalid_company():
    logger.info("Start delete invalid company...")
    mid = -1
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from topic_company where id>%s order by id limit 1000", mid)
        if len(ms) == 0:
            conn.close()
            break
        for m in ms:
            mid = m["id"]
            if m["active"] != 'Y':
                continue

            company = conn.get("select * from company where id=%s", m["companyId"])
            if company is None or (company["active"] is not None and company["active"]!='Y'):
                logger.info("should delete topic_company_id: %s", mid)

                conn.update("update topic_tab_company_rel set active='N',modifyTime=now(), modifyUser=1078"
                            " where topicCompanyId=%s", mid)
                rels = conn.query("select * from topic_message_company_rel where topicCompanyId=%s and (active='Y' or active is null)",
                                  mid)
                for r in rels:
                    topic_message_id = r["topicMessageId"]
                    conn.update("update topic_tab_message_rel set active='N',modifyTime=now(), modifyUser=1078"
                                " where topicMessageId=%s", topic_message_id)
                    conn.update("update topic_message set active='N',modifyTime=now(), modifyUser=1078"
                                " where id=%s", topic_message_id)
                    conn.update("update topic_message_company_rel set active='N',modifyTime=now(), modifyUser=1078"
                                " where id=%s", r["id"])

                conn.update("update topic_company set active='N',modifyTime=now(), modifyUser=1078"
                            " where id=%s", mid)
        conn.close()
        conn.close()

    logger.info("Delete invalid company over.")


def process(topic_company_id):
    try:
        _process(topic_company_id)
    except Exception, e:
        logger.exception(e)
        traceback.print_exc()


def _process(topic_company_id):
    logger.info("process topic_company_id: %s", topic_company_id)
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    topic_company = conn.get("select * from topic_company where id=%s", topic_company_id)
    process_util.audit_company_from_topic_company(topic_company["companyId"], topic_company["topicId"], topic_company["createTime"])
    patch_sector(topic_company, _conn=conn)

    if topic_company["verify"] is None:
        topic = conn.get("select * from topic where id=%s", topic_company["topicId"])

        # 补充 topic_tab_company_rel
        conn.execute("delete from topic_tab_company_rel where topicCompanyId=%s", topic_company_id)
        topic_tabs = conn.query("select * from topic_tab where topicId=%s", topic["id"])
        for tab in topic_tabs:
            if tab["subType"] == 1200: #所有公司
                conn.insert("insert topic_tab_company_rel(topicTabId,topicCompanyId,createTime) "
                            "values(%s,%s,now())",
                            tab["id"], topic_company_id)
            elif tab["subType"] == 1201: #死亡公司
                company_id = topic_company["companyId"]
                company = conn.get("select * from company where id=%s", company_id)
                if company["companyStatus"] in [2020, 2025]:
                    conn.insert("insert topic_tab_company_rel(topicTabId,topicCompanyId,createTime) "
                                "values(%s,%s,now())",
                                tab["id"], topic_company_id)
            else:
                pass

        conn.update("update topic_company set tabStatus=1 where id=%s", topic_company_id)
    mongo.close()
    conn.close()


def delete(topic_company_id):
    conn = db.connect_torndb_proxy()
    conn.execute("delete from topic_tab_company_rel where topicCompanyId=%s", topic_company_id)
    conn.close()


def patch_sector(topic_company, _conn=None):
    logger.info("patch sector topic_company_id: %s", topic_company["id"])
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn

    if topic_company is None or topic_company["sectorStatus"] == 1:
        if _conn is None:
            conn.close()
        return

    topic_message = conn.get("select m.* from topic_message m join topic_message_company_rel r on m.id=r.topicMessageId "
                             "where r.topicCompanyId=%s and (m.active='Y' or m.active='N') order by m.publishTime desc limit 1",
                             topic_company["id"]
                             )
    if topic_message is None:
        # 从company sector获取, 并将sectorStatus=0
        patch_sector_by_company_sector(topic_company, conn)
    else:
        if topic_message["active"] == "N":
            patch_sector_by_company_sector(topic_company, conn)
            conn.update("update topic_company set sectorStatus=1 where id=%s", topic_company["id"])
        elif topic_message["relateType"] == 10:
            if topic_message["sectorStatus"] == 1:
                #使用topic_message_sector_rel, 并将sectorStatus=1
                conn.execute("delete from topic_company_sector_rel where topicCompanyId=%s", topic_company["id"])
                srels = conn.query("select * from topic_message_sector_rel where topicMessageId=%s", topic_message["id"])
                for r in srels:
                    conn.insert("insert topic_company_sector_rel(topicCompanyId,sectorId) values(%s,%s)",
                                topic_company["id"], r["sectorId"])
                conn.update("update topic_company set sectorStatus=1 where id=%s", topic_company["id"])
            else:
                # 从company sector获取, 并将sectorStatus=0
                patch_sector_by_company_sector(topic_company, conn)
        else:
            # 从company sector获取, 并将sectorStatus=1
            patch_sector_by_company_sector(topic_company, conn)
            conn.update("update topic_company set sectorStatus=1 where id=%s", topic_company["id"])
    if _conn is None:
        conn.close()


def patch_sector_by_company_sector(topic_company, conn):
    conn.execute("delete from topic_company_sector_rel where topicCompanyId=%s", topic_company["id"])
    sectors = get_company_sectors(topic_company["companyId"], conn)
    for sector in sectors:
        conn.insert("insert topic_company_sector_rel(topicCompanyId,sectorId) values(%s,%s)",
                    topic_company["id"], sector["id"])


def get_company_sectors(company_id, conn):
    sectors = conn.query("select s.* from company_tag_rel r join tag t on t.id=r.tagId "
                      "join sector s on s.tagId=t.Id "
                      "where (r.active is null or r.active='Y') and (t.active is null or t.active='Y') "
                      "and s.level=1 and s.active='Y' "
                      "and r.companyId=%s and t.type=11012", company_id)
    return sectors


if __name__ == '__main__':
    # topic_company_id = 13897
    # conn = db.connect_torndb()
    # topic_company = conn.get("select * from topic_company where id=%s", topic_company_id)
    # patch_sector(topic_company, _conn=conn)
    # conn.close()
    patch_all_sector()