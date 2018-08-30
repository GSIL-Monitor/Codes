# -*- coding: utf-8 -*-
import os, sys
import time
import traceback
import process_topic_message
import process_topic_company
import process_company_message
import process_investor_message

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("process_message4lost", stream=True)
logger = loghelper.get_logger("process_message4lost")


def main():
    logger.info("process topic_company")
    process_topic_company.process_all()
    process_topic_company.patch_all_sector()

    logger.info("process topic_message")
    process_topic_message.process_all()

    logger.info("process company_message")
    process_company_message.process_all()

    logger.info("process investor_message")
    process_investor_message.process_all()

    logger.info("End.")

if __name__ == '__main__':
    while True:
        try:
            main()
            time.sleep(60)
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()