#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'victor'

import json
from api import app
from flask import request, g, jsonify, make_response

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))

import db as dbcon
from common import dbutil
from score.end import RankScorer

import time
import multiprocessing

@app.route("/api/search/collection", methods=['GET', 'POST', 'OPTIONS'])
def collection():

    query = json.loads(request.data)
    colid = query.get('id')
    results = make_query(query)

    p = multiprocessing.Process(target=update_collection, args=(colid, results, True, query.get('update', False)))
    p.start()
    time.sleep(2)
    return make_response(jsonify({'success': True}))
    # return update_collection(colid, results, update=query.get('update', False))


def make_query(query):

    query['size'] = max(query.get('size', 0), 10000)
    # query['size'] = 1536
    rounds = query.get('round', [])
    if 1000 in rounds and (0 not in rounds):
        query.setdefault('round', []).append(0)
    return g.sc.search('company', **query)


def update_collection(colid, results, in_flask=True, update=False):

    # update collecion
    update_counts = 0
    updates = []
    db = dbcon.connect_torndb()
    if results.get('company'):
        # dbutil.clear_collection(db, colid)
        cids = [db.get('select id from company where code=%s', code).id for code in results.get('company').get('data')]

        # remove old companies that are no longer in this collection
        if update:
            olds = dbutil.get_collection_companies(db, colid)
            remove = [old for old in olds if old not in cids]
            dbutil.clear_collection(db, colid, True, remove)
            # time.sleep(0.0002)
        cids.reverse()
        for cid in cids:
            update_status = dbutil.update_collection(db, colid, cid)
            update_counts += update_status
            if update_status > 0:
                updates.append(cid)
        if in_flask:
            dbutil.set_collection_process_status(db, colid)
            db.close()
            return make_response(jsonify({'success': True}))
        else:
            time.sleep(1)
            # for cid in updates:
            #     dbutil.update_collection(db, colid, cid)
        dbutil.set_collection_process_status(db, colid)
        db.close()
    if in_flask:
        dbutil.clear_collection(db, colid)
        db.close()
        return make_response(jsonify({'success': False}))
    return updates
