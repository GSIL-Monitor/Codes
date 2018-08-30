#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import sys,os
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db, json, time, datetime,random
import urllib2

import loghelper
#logger
loghelper.init_logger("proxy_util", stream=True)
logger = loghelper.get_logger("proxy_util")

def get_proxy(type, anonymity):
    try:
        sleep_time = random.randint(10, 30)
        time.sleep(sleep_time)

        conn = db.connect_torndb_crawler()
        if type == 'http':
            t = '1'
        elif type == 'https':
            t = '2'
        elif type == 'socks4':
            t = '4'
        elif type == 'socks5':
            t = '5'

        if anonymity == 'high':
            a = '3,5'
        else:
            a = '2'
        # url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=20&http_type='+t+'&anonymous='+a+'&result_format=json'
        url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=20' \
              '&http_type='+t+'&anonymous='+a+'&result_fields=1,2,3,4,5,6,7,8,9&result_format=json'

        urllib2.install_opener(None)
        s = urllib2.urlopen(url, timeout=60)
        result = s.read()
        result = json.loads(result)

        ip_list = result['result']
        # logger.info(ip_list)

        if len(ip_list) == 0:
            s.close()
            conn.close()
            return

        for proxystr in ip_list:
            ip = {}

            ip['anonymity'] = anonymity
            ip['type'] = type
            ip['transferTime'] = proxystr['transfer_time']
            ip['pingTime'] = proxystr['ping_time']
            ip['isp'] = proxystr['isp']


            countryarr = proxystr['country'].split(':')
            country = countryarr[0]
            province = ''
            if len(countryarr) > 1:
                province = countryarr[1]

            if country == u'中国':
                country = 'cn'

            ip['country'] = country
            ip['province'] = province

            iparr = proxystr['ip:port'].split(':')
            ip['ip'] = str(iparr[0])
            ip['port'] = str(iparr[1])

            # if ip['pingTime'] < 5 and ip['transferTime'] < 5:
            if type == 'http' or type == 'https':
                verify_proxy(ip, 'API', type, conn)
            else:
                insert_db(ip, type, conn)

        s.close()
    except Exception, e:
        logger.info(e)
    finally:
        conn.close()

    print datetime.datetime.now()

def verify_proxy(ip, ip_from, type, conn):
    try:
        proxy = urllib2.ProxyHandler({type: type+'://'+ip['ip']+':'+ip['port']})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        url = type+'://www.baidu.com/'
        s = urllib2.urlopen(url, timeout=5)

        if s.geturl() != url or s.getcode() != 200 or len(s.info()) == 0:
            if ip_from == 'DB':
                sql = 'delete from proxy where id= %s'
                conn.update(sql, ip['id'])
            s.close()
            return

        if ip_from == 'API':
            sql = 'select * from proxy where ip=%s and port=%s and type=%s'
            result = conn.get(sql, ip['ip'], ip['port'], type)
            if result != None:
                s.close()
                return
            sql = 'insert into proxy(ip, port, type, anonymity, transferTime, pingTime, isp, country, province, createTime)' \
                  ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())'
            conn.update(sql, ip['ip'], ip['port'], ip['type'], ip['anonymity'],
                        ip['transferTime'], ip['pingTime'], ip['isp'], ip['country'], ip['province'])
        elif ip_from == 'DB':
            sql = 'update proxy set modifyTime = now() where id = %s'
            conn.update(sql, ip['id'])
        s.close()

    except Exception,e:
        logger.info('verify: ' + str(e))
        if ip_from == 'DB':
            sql = 'delete from proxy where id= %s'
            conn.update(sql, ip['id'])

def insert_db(ip, type, conn):
    sql = 'select * from proxy where ip=%s and port=%s and type=%s'
    result = conn.get(sql, ip['ip'], ip['port'], type)
    if result is None:
        sql = 'insert into proxy(ip, port, type, anonymity, transferTime, pingTime, isp, country, province, createTime)' \
                  ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())'
        conn.insert(sql, ip['ip'], ip['port'], ip['type'], ip['anonymity'],
                        ip['transferTime'], ip['pingTime'], ip['isp'], ip['country'], ip['province'])
