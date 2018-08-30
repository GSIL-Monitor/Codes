#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/deal", methods=['GET', 'POST', 'OPTIONS'])
def deal():

    query = json.loads(request.data)
    # query = json.loads(query, encoding='utf-8')
    results = g.dsc.search('deal', **query)
    return make_response(jsonify(results))