#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import ConfigParser, os

conf_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '../conf/main.conf')
# print(conf_path)


def get_mongodb_production():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MONGODB", "PRODUCTION")


def get_mongodb_development_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MONGODB", "HOST"), int(cf.get("MONGODB", "PORT"))

def get_mongodb_production_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MONGODB", "CONN_ADDR1"), cf.get("MONGODB", "CONN_ADDR2"), \
        cf.get("MONGODB","REPLICAT_SET"), \
        cf.get("MONGODB", "username"), cf.get("MONGODB", "password")

def get_mongodb_local():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MONGODB_LOCAL", "HOST"), int(cf.get("MONGODB_LOCAL", "PORT"))


def get_kafka_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("KAFKA", "URL")


def get_mysql_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MYSQL", "DB_HOST"), cf.get("MYSQL", "DB_NAME"), \
           cf.get("MYSQL", "DB_USER"), cf.get("MYSQL", "DB_PASSWD")


def get_mysql_readonly_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MYSQL_READONLY", "DB_HOST"), cf.get("MYSQL_READONLY", "DB_NAME"), \
           cf.get("MYSQL_READONLY", "DB_USER"), cf.get("MYSQL_READONLY", "DB_PASSWD")


def get_mysql_proxy_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MYSQL_PROXY", "DB_HOST"), cf.get("MYSQL_PROXY", "DB_NAME"), \
           cf.get("MYSQL_PROXY", "DB_USER"), cf.get("MYSQL_PROXY", "DB_PASSWD")


def get_mysql_config_crawler():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MYSQL", "DB_HOST"), cf.get("MYSQL", "DB_CRAWLER_NAME"), \
           cf.get("MYSQL", "DB_USER"), cf.get("MYSQL", "DB_PASSWD")


def get_mysql_config_test():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("MYSQL", "DB_HOST"), cf.get("MYSQL", "DB_TEST_NAME"), \
           cf.get("MYSQL", "DB_USER"), cf.get("MYSQL", "DB_PASSWD")


def get_es_config():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH", "HOST"), cf.get("ELASTICSEARCH", "PORT")


def get_es_config_with_pswd():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH", "HOST"), cf.get("ELASTICSEARCH", "PORT"), \
           cf.get("ELASTICSEARCH", "USER"), cf.get("ELASTICSEARCH", "PASSWORD")


def get_es_config_1():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH1", "HOST"), cf.get("ELASTICSEARCH1", "PORT")


def get_es_config_2():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH2", "HOST"), cf.get("ELASTICSEARCH2", "PORT")


def get_es_config_test():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH4", "HOST"), cf.get("ELASTICSEARCH4", "PORT")


def get_es_local():

    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get("ELASTICSEARCH", "HOST"), cf.get("ELASTICSEARCH", "PORT")


def get_smtp_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return  cf.get("SMTP", "SMTP_SERVER"), \
            cf.get("SMTP", "SMTP_PORT"), \
            cf.get("SMTP", "SMTP_USERNAME"), \
            cf.get("SMTP", "SMTP_PASSWORD"), \
            cf.get("SMTP", "HOST")

def get_aliyun_smtp_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return  cf.get("ALIYUN_SMTP", "ALIYUN_ACCESS_KEY_ID"), \
            cf.get("ALIYUN_SMTP", "ALIYUN_ACCESS_KEY_SECRET"), \
            cf.get("ALIYUN_SMTP", "HOST")

def get_sendcloud_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return  cf.get("SENDCLOUD", "API_USER"), \
            cf.get("SENDCLOUD", "API_KEY")


def get_oss2_config():
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return  cf.get("OSS2", "access_key_id"), \
            cf.get("OSS2", "access_key_secret"), \
            cf.get("OSS2", "endpoint"), \
            cf.get("OSS2", "bucket_name")
