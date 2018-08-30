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
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp'))

import loghelper
from common import dbutil

# logger
loghelper.init_logger("comps", stream=True)
logger_comps = loghelper.get_logger("comps")


@app.route("/api/search/universal_comps", methods=['GET', 'POST', 'OPTIONS'])
def comps():

    global logger_comps
    query = json.loads(request.data).get('payload')
    logger_comps.info('Comps Query, %s' % query)
    cid, tag, start, size = query.get('company'), query.get('tag', 0), query.get('start', 0), query.get('size', 5)
    if tag == 0:
        comps_candidates = dbutil.get_company_comps(g.db, cid)
        logger_comps.info(comps_candidates)
        results = {'company': {'count': len(comps_candidates),
                               'data': map(lambda x: {'id': dbutil.get_company_code(g.db, x)},
                                           comps_candidates)[start: start+size],
                               'tags': dbutil.prompt_tag_filter(g.db, comps_candidates)}}
    else:
        tag = dbutil.get_tag_id(g.db, tag)[0]
        comps_candidates = dbutil.get_filtered_company_comps(g.db, cid, tag)
        results = {'company': {'count': len(comps_candidates),
                               'data': map(lambda x: {'id': dbutil.get_company_code(g.db, x)},
                                           comps_candidates)[start: start+size]}}
    return make_response(jsonify(results))
