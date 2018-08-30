#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/deal/complete", methods=['GET', 'POST', 'OPTIONS'])
def deal_complete():

    inputs = json.loads(request.data)
    key, org = inputs.get("data").strip().lower(), inputs.get("orgId")
    results = g.dsc.search('deal_completion', **{'key': key, 'org': org})
    return make_response(jsonify({'deal': results}))