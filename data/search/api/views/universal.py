#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response


@app.route("/api/search/universal", methods=['GET', 'POST', 'OPTIONS'])
def universal():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('general', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_combined", methods=['GET', 'POST', 'OPTIONS'])
def universal_combined():

    query = json.loads(request.data).get('payload')
    flag = 'normal'
    # empty search
    if not query.get('input', '').strip():
        query = {
            'input': '',
            'start': query.get('start', 0),
            'size': query.get('size', 10),
            "sort": 76004,
            'filter': {'domestic': True}
        }
        flag = 'empty'
    results = g.usc.search('combined', **query)
    results['code'] = 0
    if flag == 'empty':
        results['industry'] = []
        results['investor'] = {'count': 0, 'data': []}
    return make_response(jsonify(results))


@app.route("/api/search/universal_industry", methods=['GET', 'POST', 'OPTIONS'])
def universal_industry():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('industry', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_topic", methods=['GET', 'POST', 'OPTIONS'])
def universal_topic():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('topic', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_ranklist", methods=['GET', 'POST', 'OPTIONS'])
def universal_ranklist():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('ranklist', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_event", methods=['GET', 'POST', 'OPTIONS'])
def universal_event():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('event', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_exit_event", methods=['GET', 'POST', 'OPTIONS'])
def universal_exit_event():

    query = json.loads(request.data).get('payload')
    # query.setdefault('filter', {})['round'] = [1110, 1120]
    query.setdefault('filter', {})['previous_investor'] = query.setdefault('filter', {}).get('investor', [])
    query.setdefault('filter', {})['investor'] = []
    results = g.usc.search('event', **query)
    results['code'] = 0
    return make_response(jsonify(results))


@app.route("/api/search/universal_investor", methods=['GET', 'POST', 'OPTIONS'])
def universal_investor():

    query = json.loads(request.data).get('payload')
    results = g.usc.search('investor', **query)
    results['code'] = 0
    return make_response(jsonify(results))
