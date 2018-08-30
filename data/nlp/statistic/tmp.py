# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db as dbcon

from itertools import chain


def count_tags(source=13030):

    db = dbcon.connect_torndb()
    tags = chain(*[item.tags.split(',') for item in db.query('select tags from source_company '
                                                             'where source=%s', source)])
    print len(set(tags))


if __name__ == '__main__':

    print __file__
    print count_tags(sys.argv[1])
