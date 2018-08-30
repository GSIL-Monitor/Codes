#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/universal_news", methods=['GET', 'POST', 'OPTIONS'])
def news():

    query = json.loads(request.data)
    if query.get('payload'):
        query = query.get('payload', {})
    results = g.nsc.search('title', **query)
    return make_response(jsonify(results))


@app.route("/api/search/universal_report", methods=['GET', 'POST', 'OPTIONS'])
def report():

    query = json.loads(request.data)
    if query.get('payload'):
        query = query.get('payload', {})
    results = g.rsc.search(**query)
    return make_response(jsonify(results))
