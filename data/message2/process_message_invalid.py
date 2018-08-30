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
loghelper.init_logger("process_message_invalid", stream=False)
logger = loghelper.get_logger("process_message_invalid")


def main():
    process_topic_company.delete_invalid_company()
    process_topic_message.delete_invalid_message()
    process_company_message.delete_invalid_message()
    process_investor_message.delete_invalid_message()

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