# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("sector_adjust", stream=True)
logger = loghelper.get_logger("sector_adjust")

conn = db.connect_torndb()
mongo = db.connect_mongo()

DELETE_SECTORS = [
    (1, (2,)),
    (13, (14,)),
    (16, (8,)),
    (20, (8,)),
    (20003,(27,23,26))
]


def clean_dup_user_sector():
    items = conn.query("select sectorId,userId,count(*) cnt from user_sector where active='Y' group by sectorId,userId having cnt>1")
    for item in items:
        ss = list(conn.query("select * from user_sector where userId=%s and sectorId=%s and active='Y'",
                        item["userId"], item["sectorId"]))
        for s in ss[1:]:
            conn.update("update user_sector set active='N',modifyTime=now() where id=%s", s["id"])


def user_sector():
    logger.info("user_sector")
    for delete_sector_id, new_sector_ids in DELETE_SECTORS:
        logger.info("delete_sector_id: %s", delete_sector_id)
        logger.info("new_sector_ids: %s", new_sector_ids)
        uss = conn.query("select * from user_sector where sectorId=%s and "
                         "(active is null or active='Y')",
                         delete_sector_id)
        for us in uss:
            logger.info("id: %s, userId: %s, sectorId: %s", us["id"], us["userId"], us["sectorId"])
            for new_sector_id in new_sector_ids:
                new_us = conn.get("select * from user_sector where userId=%s and sectorId=%s and "
                              "(active is null or active='Y')",
                              us["userId"], new_sector_id)
                if new_us is None:
                    conn.insert("insert user_sector(sectorId,userId,active,createTime,modifyTime) "
                                "values(%s,%s,'Y',now(),now())",
                                new_sector_id, us["userId"])
                    # exit()
            conn.update("update user_sector set active='N',modifyTime=now() where id=%s", us["id"])
            # exit()

    supplement = [
        (2,25),
        (4,24),
        (20000,22)
    ]
    for id1,id2 in supplement:
        uss = conn.query("select * from user_sector where sectorId=%s and "
                         "(active is null or active='Y')",
                         id1)
        for us in uss:
            logger.info("id: %s, userId: %s, sectorId: %s", us["id"], us["userId"], us["sectorId"])
            new_us = conn.get("select * from user_sector where userId=%s and sectorId=%s and "
                              "(active is null or active='Y')",
                              us["userId"], id2)
            if new_us is None:
                conn.insert("insert user_sector(sectorId,userId,active,createTime,modifyTime) "
                            "values(%s,%s,'Y',now(),now())",
                            id2, us["userId"])
                # exit()


def adjust1():
    tables = [
        ("industry_sector_rel", "industryId"),
        ("hot_company", "companyId")
    ]

    for table, column in tables:
        logger.info("table: %s", table)
        for delete_sector_id, new_sector_ids in DELETE_SECTORS:
            logger.info("delete_sector_id: %s", delete_sector_id)
            logger.info("new_sector_ids: %s", new_sector_ids)
            if len(new_sector_ids) > 1:
                # TODO
                continue
            new_sector_id = new_sector_ids[0]
            rels = conn.query("select * from " + table + " where sectorId=%s and "
                              "(active is null or active='Y')",
                              delete_sector_id)
            for rel in rels:
                logger.info("%s, id: %s", table, rel["id"])
                column_id = rel[column]
                _rel = conn.get("select * from " + table + " where " + column + "=%s and "
                                "sectorId=%s and (active is null or active='Y')",
                                column_id, new_sector_id)
                if _rel is None:
                    conn.insert("insert " + table + "(sectorId," + column + ",createUser,modifyUser,createTime,modifyTime,active) "
                                "values(%s,%s,221,221,now(),now(),'Y')",
                                new_sector_id, column_id)
                conn.update("update " + table + " set active='N', modifyUser=221,modifyTime=now() where id=%s",
                            rel["id"])
                #exit()


def adjust2():
    tables = [
        ("push_pool", "companyId"),
    ]

    for table, column in tables:
        logger.info("table: %s", table)
        for delete_sector_id, new_sector_ids in DELETE_SECTORS:
            logger.info("delete_sector_id: %s", delete_sector_id)
            logger.info("new_sector_ids: %s", new_sector_ids)
            if len(new_sector_ids) > 1:
                continue
            new_sector_id = new_sector_ids[0]
            rels = conn.query("select * from " + table + " where sectorId=%s",
                              delete_sector_id)
            for rel in rels:
                logger.info("%s, id: %s", table, rel["id"])
                column_id = rel[column]
                _rel = conn.get("select * from " + table + " where " + column + "=%s and "
                                "sectorId=%s",
                                column_id, new_sector_id)
                if _rel is None:
                    conn.update("update " + table + " set sectorId=%s, modifyTime=now() where id=%s",
                                new_sector_id, rel["id"])
                else:
                    conn.execute("delete from " + table + " where id=%s", rel["id"])
                    # exit()


def adjust3():
    tables = [
        ("topic_company_sector_rel", "topicCompanyId"),
        ("topic_message_sector_rel", "topicMessageId"),
    ]

    for table, column in tables:
        logger.info("table: %s", table)
        for delete_sector_id, new_sector_ids in DELETE_SECTORS:
            logger.info("delete_sector_id: %s", delete_sector_id)
            logger.info("new_sector_ids: %s", new_sector_ids)
            # if len(new_sector_ids) > 1:
            #     continue
            new_sector_id = new_sector_ids[0]
            rels = conn.query("select * from " + table + " where sectorId=%s",
                              delete_sector_id)
            for rel in rels:
                logger.info("%s, id: %s", table, rel["id"])
                column_id = rel[column]
                _rel = conn.get("select * from " + table + " where " + column + "=%s and "
                                "sectorId=%s",
                                column_id, new_sector_id)
                if _rel is None:
                    conn.update("update " + table + " set sectorId=%s where id=%s",
                                new_sector_id, rel["id"])
                    # exit()
                else:
                    conn.execute("delete from " + table + " where id=%s", rel["id"])
                    # exit()


def clean_dup_topic_company_sector_rel():
    items = conn.query("select topicCompanyId,sectorId,count(*) cnt from topic_company_sector_rel group by topicCompanyId,sectorId having cnt>1")
    for item in items:
        ss = list(conn.query("select * from topic_company_sector_rel where topicCompanyId=%s and sectorId=%s",
                        item["topicCompanyId"], item["sectorId"]))
        for s in ss[1:]:
            conn.execute("delete from topic_company_sector_rel where id=%s", s["id"])


def clean_dup_topic_message_sector_rel():
    items = conn.query("select topicMessageId,sectorId,count(*) cnt from topic_message_sector_rel group by topicMessageId,sectorId having cnt>1")
    for item in items:
        ss = list(conn.query("select * from topic_message_sector_rel where topicMessageId=%s and sectorId=%s",
                        item["topicMessageId"], item["sectorId"]))
        for s in ss[1:]:
            conn.execute("delete from topic_message_sector_rel where id=%s", s["id"])


if __name__ == "__main__":
    # clean_dup_user_sector()
    # user_sector()
    # adjust1()
    # adjust2()
    # clean_dup_topic_company_sector_rel()
    # clean_dup_topic_message_sector_rel()
    adjust3()