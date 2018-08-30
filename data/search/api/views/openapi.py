#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arthur'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/openapi/search/company", methods=['POST'])
def openapi_search_company():
    inputs = json.loads(request.data)
    name = inputs["payload"]["keyword"]
    results = g.sc.search('completion', **{'key': name, 'field': "name"})
    data = {'code': 0}
    if results.get('status', '') == 'failed':
        data["code"] = -1
    # if results.get('status', '') == 'empty':
    #    data["code"] = -1
    data["companySearchVOs"] = __format(results)
    return make_response(jsonify(data))


def __format(results):
    formatted = []
    for k, v in results.items():
        if not len(v) == 0:
            if k == 'name':
                formatted = map(lambda x: {'name': x.get('_name'), 'companyCode': x.get('_code')}, v)
    return formatted