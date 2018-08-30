import os


class BaseConfig:
    pass


class DevelopmentConfig(BaseConfig):
    MYSQL_DB_HOST = "127.0.0.1"
    MYSQL_DB_NAME = "tsb_v2"
    MYSQL_DB_USER = "root"
    MYSQL_DB_PASSWD = ""

    MONGO_DB_HOST = "127.0.0.1"
    MONGO_DB_PORT=27017
    CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'
    MYSQL_DB_NAME_2 = "crawler_v2"


class ProductionConfig(BaseConfig):
    MYSQL_DB_HOST = "rm-2zez8kikh91xe2b59.mysql.rds.aliyuncs.com"
    MYSQL_DB_NAME = "tsb_v2"
    MYSQL_DB_USER = "gobi"
    MYSQL_DB_PASSWD = "Tb_67168"

    MONGO_DB_HOST = "127.0.0.1"
    MONGO_DB_PORT = 27017
    MONGO_PRODUCTION = 'Y'
    CONN_ADDR1 = "dds-2ze211ee68246e341.mongodb.rds.aliyuncs.com:3717"
    CONN_ADDR2 = "dds-2ze211ee68246e342.mongodb.rds.aliyuncs.com:3717"
    REPLICAT_SET = "mgset-1321009"
    MONGO_USER = "root"
    MONGO_PASSWD = "tb67168"

    CSRF_ENABLED = True
    SECRET_KEY = 'you-will-never-guess'
    MYSQL_DB_NAME_2 = "crawler_v2"


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
