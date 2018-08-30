# -*- coding: utf-8 -*-
import sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")


from itjuzi import itjuzi_next_parser
from kr36 import kr36_next_parser
#from demo8 import demo8_next_parser
from mindstore import mindst_next_parser

if __name__ == "__main__":
    while True:
        # itjuzi_next_parser.process()
        kr36_next_parser.process()
        #demo8_next_parser.process()    #停止更新
        # mindst_next_parser.process()
        #break   #test
        time.sleep(10*60)