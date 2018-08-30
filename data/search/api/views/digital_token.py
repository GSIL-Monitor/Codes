#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/token", methods=['GET', 'POST', 'OPTIONS'])
def token():

    inputs = json.loads(request.data)
    key, actives = inputs.get("input").strip().lower(), inputs.get("actives", None)
    results = g.dtsc.search(key, actives, inputs.get("start", 0), inputs.get('size', 10),
                            inputs.get("sort", 4), inputs.get('order', 'desc'))
    return make_response(jsonify(results))
