# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

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
            latest = crawler_util.get_lastest_key_int_news(SOURCE, TYPE)
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
        key = str(self.CURRENT)
        self.CURRENT += 1
        return key

    def latestIncr(self):
        if self.LATEST < self.CURRENT - 1:
            self.LATEST = self.CURRENT - 1