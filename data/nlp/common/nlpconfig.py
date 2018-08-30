__author__ = 'victor'

import ConfigParser
import os

dir_path = os.path.split(os.path.realpath(__file__))[0]
segmenter = None


def get_kafka_config():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'url': cf.get("KAFKA", "URL")}


def get_mysql_config_tshbao():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get("MYSQL", "DB_HOST"), 'database': cf.get("MYSQL", "DB_NAME"),
            'user': cf.get("MYSQL", "DB_USER"), 'password': cf.get("MYSQL", "DB_PASSWD")}


def get_mysql_config_crawler():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get("MYSQL_CRAWLER", "DB_HOST"), 'database': cf.get("MYSQL_CRAWLER", "DB_NAME"),
            'user': cf.get("MYSQL_CRAWLER", "DB_USER"), 'password': cf.get("MYSQL_CRAWLER", "DB_PASSWD")}


def get_mysql_local_config():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get("MYSQL_LOCAL", "DB_HOST"), 'database': cf.get("MYSQL_LOCAL", "DB_NAME"),
            'user': cf.get("MYSQL_LOCAL", "DB_USER"), 'password': cf.get("MYSQL_LOCAL", "DB_PASSWD")}


def get_mysql_dump_config():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get("MYSQL_DUMP", "DB_HOST"), 'database': cf.get("MYSQL_DUMP", "DB_NAME"),
            'user': cf.get("MYSQL_DUMP", "DB_USER"), 'password': cf.get("MYSQL_DUMP", "DB_PASSWD")}


def get_mysql_demoday_config():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get("MYSQL_DEMODAY", "DB_HOST"), 'database': cf.get("MYSQL_DEMODAY", "DB_NAME"),
            'user': cf.get("MYSQL_DEMODAY", "DB_USER"), 'password': cf.get("MYSQL_DEMODAY", "DB_PASSWD")}


def get_mongo_config():

    global dir_path
    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(dir_path, "main.conf"))
    return {'host': cf.get('MONGODB', 'HOST'), 'port': int(cf.get('MONGODB', 'PORT'))}


def get_segmenter():

    global segmenter
    if segmenter:
        return segmenter
    else:
        from zhtools.segment import Segmenter
        print 'new'
        segmenter = Segmenter()
        return segmenter


def get_allowed_pos():

    allowed_pos = ['an', 'i', 'n', 'nt', 'nz', 'vn', 'ws', 'eng', 'tag']
    return allowed_pos


def get_skip_list():

    return [19596, 18430, 44178, 49561, 20292, 80763, 63746, 16486]


def get_intern_ids():

    return [50, 51, 52, 87, 88, 118, 122, 123, 124, 154, 167, 168, 169, 170, 206]


if __name__ == '__main__':

    print __file__
    print get_mongo_config()