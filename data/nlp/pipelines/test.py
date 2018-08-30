# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbcon
from context import Context


if __name__ == '__main__':

    db = dbcon.connect_torndb()
    c = Context(40289, db)
    for a, b, c in c.cut():
        print a, b, c
    db.close()