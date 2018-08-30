# -*- coding: utf-8 -*-
import os, sys
import datetime, time, json
import traceback
from kafka import KafkaConsumer

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("user_saoanzi_conf_init", stream=True)
logger = loghelper.get_logger("user_saoanzi_conf_init")

conn=None

def init_kafka():
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    return KafkaConsumer("admin", group_id="user_saoanzi_conf_init",
                    bootstrap_servers=[url],
                    auto_offset_reset='smallest',
                    enable_auto_commit=False,
                    max_poll_records=1,
                    session_timeout_ms=60000,
                    request_timeout_ms=70000
    )


def process_user(user, org):
    logger.info(user["username"])

    # user_saoanzi_sector_conf
    # sector_confs = conn.query(" select * from user_saoanzi_sector_conf "
    #                           " where "
    #                           " organizationId=%s and userId=%s",
    #                           org["id"], user["id"])
    # if len(sector_confs) == 0:
    #     tags = conn.query("select * from tag where sectorType=1 and (active is null or active='Y')")
    #     for tag in tags:
    #         conn.insert(" insert user_saoanzi_sector_conf(userId,organizationId,tagId,createTime,modifyTime,active) "
    #                     " values(%s,%s,%s, now(),now(),'Y')",
    #                     user["id"], org["id"], tag["id"])

    # user_saoanzi_conf
    conf = conn.get(" select * from user_saoanzi_conf where organizationId=%s and userId=%s "
                    " and active='Y' limit 1",
                    org["id"], user["id"])
    if conf is None:
        conn.insert(" insert user_saoanzi_conf(userId,organizationId,createTime,modifyTime,active) "
                    " values(%s,%s,now(),now(),'Y')",
                    user["id"], org["id"])

    # user_saoanzi_source_conf
    # source_confs = conn.query(" select * from user_saoanzi_source_conf "
    #                           " where "
    #                           " organizationId=%s and userId=%s",
    #                           org["id"], user["id"])
    # if len(source_confs) == 0:
    #     sources = conn.query("select * from saoanzi_source where active='Y'")
    #     for source in sources:
    #         conn.insert(" insert user_saoanzi_source_conf(userId,organizationId,saoanziSourceId,createTime,modifyTime,active) "
    #                     " values(%s,%s,%s,now(),now(),'Y')",
    #                     user["id"], org["id"], source["id"])


def process_org(org):
    logger.info(org["name"])
    users = conn.query(" select u.* from user_organization_rel r join user u on u.id=r.userId"
                       " where "
                       " r.active='Y' and "
                       " u.active in ('Y', 'N') and "
                       "r.organizationId=%s",
                       org["id"])
    for user in users:
        # if user["id"] != 221: # Test
        #     continue
        process_user(user, org)


def process_org_by_id(org_id):
    global conn
    conn = db.connect_torndb()

    menu = conn.get("select * from org_menu_rel where orgMenuId=9 and active='Y' and orgId=%s limit 1", org_id)
    if menu is None:
        conn.close()
        return

    org = conn.get("select * from organization where id=%s", org_id)
    if org["serviceStatus"] != 'Y':
        conn.close()
        return

    process_org(org)

    conn.close()


def process_user_by_id(user_id):
    global conn
    conn = db.connect_torndb()

    user = conn.get("select * from user where id=%s", user_id)
    if user is None or user.active not in ('Y','N'):
        conn.close()
        return

    rels = conn.query("select * from user_organization_rel where userId=%s", user_id)
    for rel in rels:
        if rel["active"] != "Y":
            continue
        org = conn.get("select * from organization where id=%s", rel["organizationId"])
        if org["serviceStatus"] != 'Y':
            continue
        process_user(user, org)

    conn.close()


def init_all():
    global conn
    conn = db.connect_torndb()
    orgs = conn.query("select o.* from organization o join org_menu_rel r on o.id=r.orgId "
                      "where r.orgMenuId=9 and r.active='Y' and serviceStatus='Y'")
    for org in orgs:
        # if org["id"] != 51: # Test
        #     continue
        process_org(org)
        logger.info("")
    conn.close()


def main():
    kafka_consumer = init_kafka()
    while True:
        try:
            logger.info("start")
            for message in kafka_consumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    try:
                        msg = json.loads(message.value)
                        kafka_consumer.commit()
                    except:
                        kafka_consumer.commit()
                        continue

                    type = msg["type"]
                    action = msg["action"]
                    _id = msg["id"]
                    if type == "org":
                        if action == 'create':
                            process_org_by_id(_id)
                    elif type == "user":
                        if action == 'create':
                            process_user_by_id(_id)
                except Exception, e:
                    traceback.print_exc()
                    kafka_consumer.commit()
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            kafka_consumer = init_kafka()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        if sys.argv[1] == "all":
            init_all()