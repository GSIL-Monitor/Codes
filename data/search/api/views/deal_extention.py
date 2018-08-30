#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))

import db as dbcon
from common import dbutil


@app.route("/api/search/deal/extend", methods=['GET', 'POST', 'OPTIONS'])
def deal_extend():

    inputs = json.loads(request.data)
    key, org = inputs.get("input").strip().lower(), inputs.get("orgId")

    # deal
    deals = g.dsc.search('deal', **{'input': key, 'orgId': org})
    db = dbcon.connect_torndb()
    results = {'deal': [{'id': did, 'name': dbutil.get_deal_info(db, did).name} for did in deals.get('data', [])]}
    # company
    companies = g.sc.search('completion', **{'key': key, 'field': 'name'})
    results['company'] = __format(companies)
    return make_response(jsonify(results))


def __format(results):

    if results.get('status') in ['failed', 'empty']:
        return []
    dups = {}
    for item in results.get('name'):
        dups.setdefault((item.get('_code'), item.get('_name')), []).append(item.get('completionName'))
    return [{'name': dk[1], 'code': dk[0]} for dk, dv in dups.items()]