import traceback, sys
import logging
from flask import Flask, g, json
from flask import current_app
import torndb
from config import config
import pymongo
from flask_bootstrap import Bootstrap
from flask_moment import Moment


def connect_db(connNum):
    c = current_app.config
    dbName = "MYSQL_DB_NAME" if connNum == 1 else "MYSQL_DB_NAME_2"
    
    conn = torndb.Connection(
        c.get("MYSQL_DB_HOST"),
        c.get(dbName),
        c.get("MYSQL_DB_USER"),
        c.get("MYSQL_DB_PASSWD"),
        time_zone='+8:00',
        charset='utf8mb4',
        maxcached=10, maxconnections=20)
    conn.execute("set sql_safe_updates=1")
    conn.execute("set autocommit=1")
    return conn


def connect_mongo():
    c = current_app.config
    # mongo = pymongo.MongoClient(c.get("MYSQL_DB_HOST"), c.get("MONGO_DB_PORT"))
    # return mongo
    if c.get("MONGO_PRODUCTION") == "Y":
        conn1, conn2, replicat_set, username, password = c.get("CONN_ADDR1"), c.get("CONN_ADDR2"), \
                                                         c.get("REPLICAT_SET"),\
                                                         c.get("MONGO_USER"), c.get("MONGO_PASSWD")
        client = pymongo.MongoClient([conn1, conn2], replicaSet=replicat_set)
        client.admin.authenticate(username, password)
        return client
    else:
        client = pymongo.MongoClient(c.get("MYSQL_DB_HOST"), c.get("MONGO_DB_PORT"))
        return client

def create_app(config_name):
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    moment = Moment(app)

    formatter = logging.Formatter('L%(lineno)d %(pathname)s %(asctime)s %(levelname)-8s %(message)s',
                                  '%a, %d %b %Y %H:%M:%S', )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.config.from_object(config[config_name])

    from .stat import bp as statq
    app.register_blueprint(statq, url_prefix='/stat')

    from .data import bp as dataq
    app.register_blueprint(dataq, url_prefix='/5977875df8716656636efb78/data')

    # @app.errorhandler(404)
    # def page_not_found(e):
    #     data = {"code": -1}
    #     return json.dumps(data)
    #
    # @app.errorhandler(500)
    # def internal_server_error(e):
    #     data = {"code": -1}
    #     return json.dumps(data)
    #
    # @app.errorhandler(Exception)
    # def handle_error(e):
    #     traceback.print_exc()
    #     data = {"code": -1}
    #     return json.dumps(data)

    @app.before_request
    def before_request():
        # print "before_request"
        g.conn = connect_db(1)
        g.mongo = connect_mongo()
        g.conn_crawler = connect_db(2)

    @app.teardown_request
    def teardown_request(exception):
        # print "teardown_request"
        conn = getattr(g, 'conn', None)
        if conn is not None:
            conn.close()

        conn2 = getattr(g, 'conn_crawler', None)
        if conn2 is not None:
            conn2.close()

        mongo = getattr(g, 'mongo', None)
        if mongo is not None:
            mongo.close()

    return app


datacheck = create_app("production")