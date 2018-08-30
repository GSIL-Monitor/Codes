# -*- coding: utf-8 -*-
import sys
import time

import itjuzi_investfirm_parser
import itjuzi_member_parser
import itjuzi_company_parser
import itjuzi_funding_parser
import itjuzi_funding_parser2
import itjuzi_news_parser

reload(sys)
sys.setdefaultencoding("utf-8")


if __name__ == '__main__':
    while True:
        itjuzi_investfirm_parser.process()
        # itjuzi_member_parser.process()
        itjuzi_company_parser.process()
        itjuzi_funding_parser.process()
        itjuzi_funding_parser2.process()
        # itjuzi_news_parser.process()

        #break   #test
        time.sleep(60)