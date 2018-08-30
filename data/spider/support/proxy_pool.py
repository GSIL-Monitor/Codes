#!/opt/py-env/bin/python
# -*- coding: utf-8 -*-

import os, sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

import db

proxy_list = []
global current_proxy
current_proxy = None

def get_single_proxy(proxy):
    conn = db.connect_torndb_crawler()
    country = ''
    isp = ''
    ping = ''
    transfer = ''
    if proxy.get('country') != None:
        country =' and country= "'+ proxy['country'] + '"'

    #if proxy.get('isp') != None:
    #    isp = ' and isp= "'+proxy['isp'] + '"'
    isp = ' and isp!="移动"'

    if proxy.get('ping') != None:
        ping = ' and pingTime < ' + str(proxy['ping'])

    if proxy.get('transferTime') != None:
        transfer = ' and transferTime < ' + str(proxy['transferTime'])

    sql = 'select * from proxy where type="'+proxy['type']+'" and anonymity= "'+ proxy['anonymity'] +'" ' +isp+country+ping+transfer+ ' order by rand() limit 1'
    result = conn.get(sql)

    conn.close()
    return result

def get_proxy(type):
    global proxy_list
    flag = False

    len_list = len(proxy_list)
    conn = db.connect_db_crawler()
    with conn.cursor() as cursor:
        sql = 'select * from proxy where type=%s order by rand() limit 1'
        cursor.execute(sql, type)
        result = cursor.fetchone()
        proxy = {'link': result, 'active':'Y'}
        if len(proxy_list) == 0:
            proxy_list.append(proxy)
        else:
            for p in proxy_list:
                if p["link"]['id'] == result['id']:
                    flag = True

            if not flag:
                proxy_list.append(proxy)

    if len(proxy_list) == len_list:
        get_proxy(type)

    current_proxy = proxy
    return proxy

def proxy_shutdown():
    if current_proxy == None:
        return

    for p in proxy_list:
        if p["link"]['id'] == current_proxy['id']:
            p1 = p
            proxy_list.remove(p)
            p1.active = 'N'
            proxy_list.append(p1)



if __name__ == '__main__':
    # print get_a_proxy('http','high')
    proxy = {'type': 'http', 'anonymity':'high', 'country': 'cn', 'ping': 5}
    print get_single_proxy(proxy)