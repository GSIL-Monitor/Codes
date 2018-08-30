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

import db as dbcon
from common import dbutil


@app.route("/api/search/general", methods=['GET', 'POST', 'OPTIONS'])
def general():

    query = json.loads(request.data)
    uid = request.cookies
    uid = uid.get('userid', 139) if uid else 139
    db = dbcon.connect_torndb()
    if int(uid) in dbutil.get_banned_user(db):
        db.close()
        g.logger.insert({
            'query': query,
            'userId': uid,
            'mark': 'banned',
            'time': datetime.utcnow()
        })
        return make_response(jsonify({"company": {"count": 1, "data": 'xiniushuju'}}))
    # query = json.loads(query, encoding='utf-8')
    rounds = query.get('filter', {}).get('round', [])
    if 1000 in rounds and (0 not in rounds):
        query.setdefault('filter', {}).setdefault('round', []).append(0)
    results = g.sc.search('general', **query)
    # print 'results', results
    g.logger.insert({
        'query': query,
        'userId': uid,
        'results': results,
        'time': datetime.utcnow()
    })
    return make_response(jsonify(results))
