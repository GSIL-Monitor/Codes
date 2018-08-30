# -*- coding: utf-8 -*-
import sys
import time

import lagou_company_parser

reload(sys)
sys.setdefaultencoding("utf-8")


if __name__ == '__main__':
    while True:
        lagou_company_parser.process()
        #break   #test
        time.sleep(30*60)