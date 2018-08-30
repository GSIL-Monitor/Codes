# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("restore", stream=True)
logger = loghelper.get_logger("restore")


def main():
    sql = "select id,topicId,active from topic_message " \
          "where modifyUser=1078 and " \
          "modifyTime>'2017-12-04' and " \
          "topicId in (9,10,44) " \
          "and active='N';"
    topic_messages = conn.query(sql)
    for topic_message in topic_messages:
        logger.info("topicId: %s, topic_message, id: %s", topic_message["topicId"], topic_message["id"])
        conn.update("update topic_message set active='Y' where id=%s", topic_message["id"])

        topic_tab_message_rels = conn.query("select * from topic_tab_message_rel where topicMessageId=%s"
                                            " order by verify desc limit 1",
                                            topic_message["id"])
        for topic_tab_message_rel in topic_tab_message_rels:
            logger.info("topic_tab_message_rel, id: %s", topic_tab_message_rel["id"])
            conn.update("update topic_tab_message_rel set active='Y' where id=%s", topic_tab_message_rel["id"])

        topic_message_company_rels = conn.query("select * from topic_message_company_rel where topicMessageId=%s",
                                                topic_message["id"])
        for topic_message_company_rel in topic_message_company_rels:
            logger.info("topic_message_company_rel, id: %s", topic_message_company_rel["id"])
            conn.update("update topic_message_company_rel set active='Y' where id=%s", topic_message_company_rel["id"])

            topic_company = conn.get("select * from topic_company where id=%s",
                                     topic_message_company_rel["topicCompanyId"])
            logger.info("topic_company, id: %s", topic_company["id"])
            conn.update("update topic_company set active='Y' where id=%s", topic_company["id"])

            topic_tab_company_rels = conn.query("select * from topic_tab_company_rel where topicCompanyId=%s"
                                                " order by verify desc limit 1",
                                                topic_company["id"])
            for topic_tab_company_rel in topic_tab_company_rels:
                logger.info("topic_tab_company_rel, id: %s", topic_tab_company_rel["id"])
                conn.update("update topic_tab_company_rel set active='Y' where id=%s", topic_tab_company_rel["id"])


if __name__ == '__main__':
    conn = db.connect_torndb()
    main()
