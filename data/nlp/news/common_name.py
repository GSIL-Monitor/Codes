# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))

import db as dbcon
from search.client import SearchClient

import codecs


def find_common_names(threshold):

    db = dbcon.connect_torndb()
    client = SearchClient()

    with codecs.open(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../common/dict/common.cname'),
                     'w', 'utf-8') as fo:
        for result in db.iter('select distinct company.name, company.id from company left join funding '
                              'on company.id=funding.companyId where companyId is null and '
                              'company.establishDate>"2014-01-01" '
                              'and (company.active is null or company.active="Y") '
                              'and (funding.active is null or funding.active="Y");'):
            if len(result.name) > 4:
                continue
            try:
                count = client.search('open', input=result.name).get('company').get('count')
                if count > threshold:
                    fo.write('%s\n' % result.name)
            except Exception, e:
                print result, e
        for result in db.iter('select distinct company.name as name from company, funding '
                              'where companyId=company.id and (company.active is null or company.active="Y") and '
                              '(funding.active is null or funding.active="Y");'):
            if len(result.name) > 4:
                continue
            try:
                count = client.search('open', input=result.name).get('company').get('count')
                if count > threshold:
                    fo.write('%s\n' % result.name)
            except Exception, e:
                print result, e


if __name__ == '__main__':

    find_common_names(1500)
