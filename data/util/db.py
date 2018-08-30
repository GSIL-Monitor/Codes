#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-

import pymysql, torndb
from pymongo import MongoClient
import config


def connect_db():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config()
    conn = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWD,
                             db=DB_NAME,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    #conn.execute("set sql_safe_updates=1")
    return conn


def connect_db_crawler():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config_crawler()
    return pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWD,
                             db=DB_NAME,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def connect_torndb():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config()
    conn = torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD, time_zone='+8:00', charset='utf8mb4')
    #conn.execute("set sql_safe_updates=1")
    return conn


def connect_torndb_readonly():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_readonly_config()
    conn = torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD, time_zone='+8:00', charset='utf8mb4')
    #conn.execute("set sql_safe_updates=1")
    return conn


def connect_torndb_proxy():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_proxy_config()
    conn = torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD, time_zone='+8:00', charset='utf8mb4')
    #conn.execute("set sql_safe_updates=1")
    return conn



def connect_torndb_crawler():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config_crawler()
    return torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD, time_zone='+8:00', charset='utf8mb4')


def connect_torndb_test():
    (DB_HOST, DB_NAME, DB_USER, DB_PASSWD) = config.get_mysql_config_test()
    return torndb.Connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWD, time_zone='+8:00', charset='utf8mb4')


def connect_mongo():
    production = config.get_mongodb_production()
    if production == 'Y':
        conn1, conn2, replicat_set, username, password = config.get_mongodb_production_config()
        client = MongoClient([conn1, conn2], replicaSet=replicat_set)
        client.admin.authenticate(username, password)
        return client
    else:
        host, port = config.get_mongodb_development_config()
        return MongoClient(host, port)


def connect_mongo_local():
    host, port = config.get_mongodb_local()
    return MongoClient(host, port)


if __name__ == "__main__":
    conn = connect_torndb()
    # conn.execute("delete from sms")
    conn.close()