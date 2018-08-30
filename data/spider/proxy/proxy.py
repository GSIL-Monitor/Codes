#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import proxy_util

import loghelper
# logger
loghelper.init_logger("proxy", stream=True)
logger = loghelper.get_logger("proxy")

def get_proxy(type, anonymity):
    while True:
        try:
            proxy_util.get_proxy(type, anonymity)
        except Exception,e:
            logger.info(e)



if __name__ == '__main__':
    if len(sys.argv) > 2:
        type = sys.argv[1]
        anonymity = sys.argv[2]
        print type
        print anonymity
        get_proxy(type, anonymity)
