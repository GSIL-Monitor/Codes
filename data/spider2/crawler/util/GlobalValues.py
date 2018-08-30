# -*- coding: utf-8 -*-
import os, sys
import crawler_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper

#logger
loghelper.init_logger("GlobalValues", stream=True)
logger = loghelper.get_logger("GlobalValues")

class GlobalValues:
    def __init__(self, SOURCE, TYPE, flag, back=1):
        self.CURRENT = 0
        self.LATEST = 0
        self.SOURCE = SOURCE
        self.TYPE = TYPE
        self.flag = flag

        start = 1
        if self.flag == 'incr':
            latest = crawler_util.get_latest_key_int(SOURCE, TYPE)
            if latest is not None:
                start = latest + 1
        if start > back:
            start -= back
        else:
            start = 1

        self.CURRENT = start
        self.LATEST = start

    def finish(self, num=50):
        if self.LATEST < self.CURRENT - num:
            return True
        return False

    def nextKey(self):
        # no data in this range for 36kr
        if self.CURRENT > 35396 and self.CURRENT < 130720 and self.SOURCE == 13020:
            self.CURRENT = 130720
            self.LATEST = 130720
        if self.CURRENT > 32501 and self.CURRENT < 33455 and self.SOURCE == 13020:
            self.CURRENT = 33456
            self.LATEST = 33456

        if self.CURRENT > 48241 and self.CURRENT < 80000 and self.SOURCE == 13055:
            self.CURRENT = 80000
            self.LATEST = 80000
        key = str(self.CURRENT)
        self.CURRENT += 1
        return key

    def latestIncr(self):
        if self.LATEST < self.CURRENT - 1:
            self.LATEST = self.CURRENT - 1