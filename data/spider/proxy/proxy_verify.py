#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db
import proxy_util, time

import loghelper
# logger
loghelper.init_logger("proxy_verify", stream=True)
logger = loghelper.get_logger("proxy_verify")

conn = None
def proxy_verify(type):
    while True:
        try:
            conn = db.connect_torndb_crawler()
            ip_list = conn.query('select * from proxy where type= %s', type)
            if ip_list:
                for ip in ip_list:
                    ip['ip'] = str(ip['ip'])
                    ip['port'] = str(ip['port'])
                    proxy_util.verify_proxy(ip, 'DB', type, conn)
        except Exception, e:
            logger.info(' ' + type + '  ' + e)
            pass
        finally:
            conn.close()

        time.sleep(30)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        type = sys.argv[1]
        print type
        proxy_verify(type)
