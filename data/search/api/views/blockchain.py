#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from datetime import datetime
from api import app
from flask import request, g, jsonify, make_response

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))


@app.route("/api/search/blockchain", methods=['GET', 'POST', 'OPTIONS'])
def blockchain():

    query = json.loads(request.data)
    rounds = query.get('filter', {}).get('round', [])
    if 1000 in rounds and (0 not in rounds):
        query.setdefault('filter', {}).setdefault('round', []).append(0)
    results = g.sc.search('blockchain', **query)
    return make_response(jsonify(results))
