__author__ = 'victor'

import torndb
from flask import Flask, g
from elasticsearch import Elasticsearch

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import config
import db as dbcon
# from search import SearchClient
from news_search.news_client import NewsSearchClient
from news_search.report_client import ReportSearchClient
from interior.interior_client import InteriorSearchClient
from blockchain.bc_client import DigitalTokenSearchClient
from universal.universal_client import UniversalSearchClient
from amac.amac_client import AMACClient
from client import SearchClient
from deal import DealSearchClient

# def connect_elasticsearch():
#
#     (ELASTICSEARCH_HOST) = config.get_es_config()
#     return Elasticsearch([ELASTICSEARCH_HOST])


def connect_tshbao():

    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config()
    return torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD)


def connect_crawler():

    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config_crawler()
    return torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD)

# app creation
app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():

    if sys.platform == 'darwin':
        host, port = config.get_es_local()
    else:
        host, port = config.get_es_config()
    es_client = Elasticsearch([{'host': host, 'port': port}])
    g.db = dbcon.connect_torndb()
    g.mongo = dbcon.connect_mongo()
    g.amacsc = AMACClient(es_client)
    g.usc = UniversalSearchClient(es_client)
    g.dsc = DealSearchClient(es_client, False)
    g.nsc = NewsSearchClient(es_client)
    g.rsc = ReportSearchClient(es_client)
    g.isc = InteriorSearchClient(es_client)
    g.dtsc = DigitalTokenSearchClient(es_client)
    g.sc = SearchClient(es_client)
    g.logger = dbcon.connect_mongo().log.search


@app.teardown_request
def teardown_request(exception):

    pass
    # g.conn.close()
    # g.conn_tsb.close()


import api.views.completion
import api.views.collection
import api.views.collection2
import api.views.general
import api.views.blockchain
import api.views.deal_completion
import api.views.deal
import api.views.deal_extention
import api.views.news
import api.views.interior
import api.views.digital_token
import api.views.openapi
import api.views.universal
import api.views.comps
import api.views.amac