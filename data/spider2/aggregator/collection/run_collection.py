# -*- coding: utf-8 -*-
import sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")


import collection_fa
import collection_newproduct
import collection_funding
import timeline
import collection_pencilnews
import collection_microsoft

if __name__ == "__main__":
    while True:
        collection_fa.process()
        #collection_newproduct.process()
        collection_funding.process1()
        collection_pencilnews.process()
        collection_microsoft.process()
        #timeline.process()
        #break   #test
        time.sleep(10*60)