#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/universal_amac_investor", methods=['GET', 'POST', 'OPTIONS'])
def amac_general():

    query = json.loads(request.data).get('payload')
    results = g.amacsc.search('general', query.get('input'), query.get('start', 0), query.get('size', 10))
    return make_response(jsonify(results))


@app.route("/api/search/universal_amac_manager", methods=['GET', 'POST', 'OPTIONS'])
def amac_manager():

    query = json.loads(request.data).get('payload')
    results = g.amacsc.search('manager', query.get('input'), query.get('start', 0), query.get('size', 10))
    return make_response(jsonify(results))


@app.route("/api/search/universal_amac_fund", methods=['GET', 'POST', 'OPTIONS'])
def amac_fund():

    query = json.loads(request.data).get('payload')
    results = g.amacsc.search('fund', query.get('input'), query.get('start', 0), query.get('size', 10))
    return make_response(jsonify(results))
