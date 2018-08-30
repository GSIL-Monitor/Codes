# -*- coding: utf-8 -*-
import os, sys
import json, time
import traceback
from kafka import KafkaConsumer

import process_track_group
import process_track_group_user_rel
import process_track_group_item_rel
import process_track_group_dimension
import import_item

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config

#logger
loghelper.init_logger("run_track_conf", stream=True)
logger = loghelper.get_logger("run_track_conf")


def init_kafka():
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    return KafkaConsumer("track_conf", group_id="run_track_conf",
                    bootstrap_servers=[url],
                    auto_offset_reset='smallest',
                    enable_auto_commit=False,
                    max_poll_records=1,
                    session_timeout_ms=60000,
                    request_timeout_ms=70000
    )


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
                    if type == "track_group":
                        if action == 'create':
                            process_track_group.create(_id)
                        elif action == 'delete':
                            process_track_group.delete(_id)
                    elif type == "track_group_user_rel":
                        if action == 'create':
                            process_track_group_user_rel.create(_id)
                        elif action == 'delete':
                            process_track_group_user_rel.delete(_id)
                    elif type == "track_group_item_rel":
                        if action == 'create':
                            process_track_group_item_rel.create(_id)
                        elif action == 'delete':
                            process_track_group_item_rel.delete(_id)
                    elif type == "track_group_dimension":
                        if action == 'create':
                            process_track_group_dimension.create(_id)
                        elif action == 'delete':
                            process_track_group_dimension.delete(_id)
                    elif type == "track_import":
                        if action == 'create':
                            import_item.process(_id)
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
    main()