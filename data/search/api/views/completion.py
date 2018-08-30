#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


fields = ['name', 'member', 'keyword']


@app.route("/api/search/complete", methods=['GET', 'POST', 'OPTIONS'])
def complete():

    inputs = json.loads(request.data)
    if inputs.get('payload'):
        inputs = inputs.get('payload', {})
    key, field = inputs.get("data").strip().lower(), inputs.get("field", '').strip()
    strict = inputs.get('strict')
    if not strict:
        results = g.sc.search('completion', **{'key': key, 'field': field})
    else:
        results = g.sc.search('completion', **{'key': key, 'field': field, 'online': [True], 'strict': True})
    if results.get('status', '') == 'failed':
        results = {}
    if results.get('status', '') == 'empty':
        results = {}
    results = __format(results, inputs.get("language", 'cn'))
    if not inputs.get("field"):
        try:
            industries = __format(g.sc.search('completion', key=key, field='industry'))
        except Exception, e:
            industries = {}
        try:
            investors = __format(g.sc.search('completion', key=key, field='investor', online=[True]))
        except Exception, e:
            investors = {}
        results['industry'] = industries.get('industry', [])
        results['investor'] = investors.get('investor', [])
    return make_response(jsonify(results))


def __format(results, language='cn'):

    formatted = {}
    for k, v in results.items():
        if not len(v) == 0:
            if k == 'name':
                formatted[k] = map(lambda x: {'name': x.get('_name'), 'code': x.get('_code'),
                                              'completion': x.get('completionName'),
                                              'id': x.get('id')}, v)
            elif k == 'industry':
                formatted[k] = map(lambda x: {'name': x.get('_name'), 'code': x.get('_code'), 'id': x.get('id')[8:]}, v)
            elif k == 'investor':
                formatted[k] = map(lambda x: {'name': x.get('_name'), 'code': x.get('_code'), 'id': x.get('id')[1:]}, v)
            elif k == 'location' and language == 'en':
                formatted[k] = map(lambda x: {'name': x.get('en_name'), 'id': x.get('id')[1:]}, v)
            else:
                formatted[k] = map(lambda x: {'name': x.get('_name'), 'id': x.get('id')[1:]}, v)
    return formatted