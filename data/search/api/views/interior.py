#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/interior", methods=['GET', 'POST', 'OPTIONS'])
def interior():

    inputs = json.loads(request.data)
    key, actives = inputs.get("data").strip().lower(), inputs.get("actives", None)
    results = g.isc.search(key, actives)
    return make_response(jsonify(results))